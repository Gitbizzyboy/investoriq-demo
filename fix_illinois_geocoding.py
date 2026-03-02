#!/usr/bin/env python3
"""
Fix Illinois property geocoding with more aggressive address normalization
"""

import sqlite3
import requests
import time
import re

class IllinoisGeocoder:
    def __init__(self, db_path):
        self.db_path = db_path
        self.geocoding_service = "https://nominatim.openstreetmap.org/search"
        self.headers = {
            'User-Agent': 'InvestorIQ/1.0 (property investment platform)'
        }
    
    def normalize_address(self, address):
        """More aggressive address normalization for Illinois properties"""
        normalized = address.upper().strip()
        
        # Expand numbered streets (52 ST -> 52ND STREET)
        def expand_numbered_street(match):
            number = int(match.group(1))
            suffix = self.get_ordinal_suffix(number)
            return f"{number}{suffix} STREET"
        
        # Fix patterns like "52 ST CT" -> "52ND STREET COURT"
        normalized = re.sub(r'(\d+)\s+ST\s+CT', lambda m: f"{m.group(1)}{self.get_ordinal_suffix(int(m.group(1)))} STREET COURT", normalized)
        normalized = re.sub(r'(\d+)ND\s+ST\s+CT', r'\1ND STREET COURT', normalized)
        normalized = re.sub(r'(\d+)TH\s+ST\s+CT', r'\1TH STREET COURT', normalized)
        normalized = re.sub(r'(\d+)ST\s+ST\s+CT', r'\1ST STREET COURT', normalized)
        normalized = re.sub(r'(\d+)RD\s+ST\s+CT', r'\1RD STREET COURT', normalized)
        
        # Fix avenues like "109 AVE" -> "109TH AVENUE"  
        normalized = re.sub(r'(\d+)\s+AVE\b', lambda m: f"{m.group(1)}{self.get_ordinal_suffix(int(m.group(1)))} AVENUE", normalized)
        normalized = re.sub(r'(\d+)TH\s+AVE\b', r'\1TH AVENUE', normalized)
        normalized = re.sub(r'(\d+)ST\s+AVE\b', r'\1ST AVENUE', normalized)
        normalized = re.sub(r'(\d+)ND\s+AVE\b', r'\1ND AVENUE', normalized)
        normalized = re.sub(r'(\d+)RD\s+AVE\b', r'\1RD AVENUE', normalized)
        
        # General abbreviation expansion
        replacements = {
            ' ST ': ' STREET ',
            ' AVE ': ' AVENUE ',
            ' BLVD ': ' BOULEVARD ',
            ' RD ': ' ROAD ',
            ' CT ': ' COURT ',
            ' DR ': ' DRIVE ',
            ' LN ': ' LANE ',
            ' PKWY ': ' PARKWAY ',
            ' PL ': ' PLACE ',
            ' TER ': ' TERRACE ',
            ' CIR ': ' CIRCLE ',
        }
        
        for abbr, full in replacements.items():
            normalized = normalized.replace(abbr, full)
        
        # Clean up multiple spaces
        normalized = ' '.join(normalized.split())
        
        return normalized
    
    def get_ordinal_suffix(self, number):
        """Get ordinal suffix for a number (1->ST, 2->ND, 3->RD, 4->TH, etc.)"""
        if 10 <= number % 100 <= 20:
            return "TH"
        else:
            suffix = {1: "ST", 2: "ND", 3: "RD"}.get(number % 10, "TH")
            return suffix
    
    def geocode_address(self, address, city, state):
        """Try multiple geocoding strategies"""
        strategies = []
        
        # Strategy 1: Normalized address
        normalized = self.normalize_address(address)
        strategies.append(f"{normalized}, {city}, {state}")
        
        # Strategy 2: Try without court/street type
        simple = re.sub(r'\s+(STREET|AVENUE|COURT|ROAD|DRIVE|LANE|PLACE)\b', '', normalized)
        strategies.append(f"{simple}, {city}, {state}")
        
        # Strategy 3: Original address
        strategies.append(f"{address}, {city}, {state}")
        
        for i, query in enumerate(strategies):
            print(f"  Strategy {i+1}: {query}")
            
            params = {
                'q': query,
                'format': 'json',
                'limit': 1,
                'countrycodes': 'us'
            }
            
            try:
                response = requests.get(self.geocoding_service, params=params, headers=self.headers, timeout=5)
                data = response.json()
                
                if data and len(data) > 0:
                    lat = float(data[0]['lat'])
                    lon = float(data[0]['lon'])
                    
                    # Verify it's not just city center (check if coords vary enough)
                    if self.is_specific_location(lat, lon, city):
                        print(f"  ✓ SUCCESS with strategy {i+1}: {lat:.6f}, {lon:.6f}")
                        return (lat, lon)
                    else:
                        print(f"  ✗ Strategy {i+1} returned city center")
                        
            except Exception as e:
                print(f"  ✗ Strategy {i+1} failed: {e}")
            
            time.sleep(0.5)  # Be nice to the free API
        
        return None
    
    def is_specific_location(self, lat, lon, city):
        """Check if coordinates are specific or just city center"""
        # Milan city center is approximately 41.453, -90.572
        # Moline city center is approximately 41.507, -90.515
        
        city_centers = {
            'Milan': (41.453, -90.572),
            'Moline': (41.507, -90.515)
        }
        
        if city in city_centers:
            center_lat, center_lon = city_centers[city]
            # If coordinates are within 0.005 degrees (~0.3 miles) of city center, it's probably not specific
            if abs(lat - center_lat) < 0.005 and abs(lon - center_lon) < 0.005:
                return False
        
        return True
    
    def fix_illinois_geocoding(self):
        """Re-geocode Illinois properties with suspicious coordinates"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Find Illinois properties that are likely using city center coordinates
        cursor.execute("""
            SELECT rowid, property_address, city, state, latitude, longitude
            FROM master_distressed_properties
            WHERE (state = 'Illinois' OR state = 'IL')
            AND city IN ('Milan', 'Moline')
            ORDER BY city, property_address
        """)
        
        properties = cursor.fetchall()
        print(f"\n🔍 Checking {len(properties)} Illinois properties for better geocoding...\n")
        
        improved_count = 0
        
        for prop in properties:
            rowid, address, city, state, current_lat, current_lon = prop
            
            # Check if current coords are suspicious (clustered at city center)
            if not self.is_specific_location(current_lat, current_lon, city):
                print(f"\n📍 Re-geocoding: {address}, {city}")
                print(f"   Current coords: {current_lat:.6f}, {current_lon:.6f} (likely city center)")
                
                new_coords = self.geocode_address(address, city, state)
                
                if new_coords and self.is_specific_location(new_coords[0], new_coords[1], city):
                    cursor.execute("""
                        UPDATE master_distressed_properties
                        SET latitude = ?, longitude = ?
                        WHERE rowid = ?
                    """, (new_coords[0], new_coords[1], rowid))
                    improved_count += 1
                    print(f"   ✅ IMPROVED to: {new_coords[0]:.6f}, {new_coords[1]:.6f}")
                else:
                    print(f"   ❌ Could not improve geocoding")
            
            # Rate limiting
            time.sleep(1.1)
            
            # Commit every 5 improvements
            if improved_count > 0 and improved_count % 5 == 0:
                conn.commit()
                print(f"\n💾 Saved {improved_count} improvements\n")
        
        conn.commit()
        conn.close()
        
        print(f"\n✅ Geocoding improvements complete!")
        print(f"   Improved locations: {improved_count}")
        print(f"   Total IL properties: {len(properties)}")

if __name__ == "__main__":
    db_path = "/Users/jacoblister/.openclaw/workspace/business/property-finder/data/QUAD_CITIES_MASTER_DATASET.db"
    geocoder = IllinoisGeocoder(db_path)
    geocoder.fix_illinois_geocoding()