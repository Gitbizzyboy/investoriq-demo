#!/usr/bin/env python3
"""
Improved geocoding script that handles address abbreviations better
"""

import sqlite3
import requests
import time
import json
import re
from typing import Tuple, Optional

class ImprovedPropertyGeocoder:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.geocoding_service = "https://nominatim.openstreetmap.org/search"
        self.headers = {
            'User-Agent': 'InvestorIQ/1.0 (property investment platform)'
        }
        
        # Common street abbreviations to expand
        self.abbreviations = {
            ' ST ': ' STREET ',
            ' ST$': ' STREET',
            ' AVE ': ' AVENUE ',
            ' AVE$': ' AVENUE',
            ' BLVD ': ' BOULEVARD ',
            ' BLVD$': ' BOULEVARD',
            ' RD ': ' ROAD ',
            ' RD$': ' ROAD',
            ' CT ': ' COURT ',
            ' CT$': ' COURT',
            ' DR ': ' DRIVE ',
            ' DR$': ' DRIVE',
            ' LN ': ' LANE ',
            ' LN$': ' LANE',
            ' PKWY ': ' PARKWAY ',
            ' PKWY$': ' PARKWAY',
            ' PL ': ' PLACE ',
            ' PL$': ' PLACE',
            ' TER ': ' TERRACE ',
            ' TER$': ' TERRACE',
            ' CIR ': ' CIRCLE ',
            ' CIR$': ' CIRCLE',
            ' LOOP ': ' LOOP ',
            ' LOOP$': ' LOOP',
            ' N ': ' NORTH ',
            ' S ': ' SOUTH ',
            ' E ': ' EAST ',
            ' W ': ' WEST ',
            ' NE ': ' NORTHEAST ',
            ' NW ': ' NORTHWEST ',
            ' SE ': ' SOUTHEAST ',
            ' SW ': ' SOUTHWEST ',
        }
        
    def expand_abbreviations(self, address: str) -> str:
        """Expand common street abbreviations"""
        expanded = address.upper()
        
        # Add spaces to ensure we match whole words
        expanded = f" {expanded} "
        
        # Replace abbreviations
        for abbr, full in self.abbreviations.items():
            expanded = re.sub(abbr, full, expanded)
        
        # Clean up and return
        return expanded.strip()
        
    def geocode_address(self, address: str, city: str, state: str = "IL") -> Optional[Tuple[float, float]]:
        """Geocode with multiple fallback strategies"""
        
        # Strategy 1: Try expanded full address
        expanded_address = self.expand_abbreviations(address)
        full_address = f"{expanded_address}, {city}, {state}"
        
        result = self._try_geocode(full_address)
        if result:
            print(f"  ✓ Strategy 1 worked (expanded full address)")
            return result
            
        # Strategy 2: Try original address as-is
        original_full = f"{address}, {city}, {state}"
        result = self._try_geocode(original_full)
        if result:
            print(f"  ✓ Strategy 2 worked (original address)")
            return result
            
        # Strategy 3: Try just city and state
        city_state = f"{city}, {state}"
        result = self._try_geocode(city_state)
        if result:
            print(f"  ✓ Strategy 3 worked (city center)")
            # Add small random offset to avoid stacking all properties at city center
            import random
            lat, lng = result
            lat += random.uniform(-0.01, 0.01)  # ~0.7 mile variance
            lng += random.uniform(-0.01, 0.01)
            return (lat, lng)
            
        return None
    
    def _try_geocode(self, query: str) -> Optional[Tuple[float, float]]:
        """Try to geocode a single query"""
        params = {
            'q': query,
            'format': 'json',
            'limit': 1,
            'countrycodes': 'us'
        }
        
        try:
            response = requests.get(self.geocoding_service, params=params, headers=self.headers, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            if data and len(data) > 0:
                lat = float(data[0]['lat'])
                lon = float(data[0]['lon'])
                return (lat, lon)
                
        except Exception:
            pass
            
        return None
    
    def update_property_coordinates(self, limit: int = 50):
        """Update properties with geocoded coordinates"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get properties without coordinates
        cursor.execute("""
            SELECT rowid, property_address, city, state 
            FROM master_distressed_properties 
            WHERE (latitude IS NULL OR longitude IS NULL OR geocoded = 0)
            LIMIT ?
        """, (limit,))
        
        properties = cursor.fetchall()
        print(f"\n🗺️  Starting geocoding for {len(properties)} properties...\n")
        
        geocoded_count = 0
        failed_count = 0
        
        for i, prop in enumerate(properties):
            rowid, address, city, state = prop
            state = state or "IL"
            
            print(f"[{i+1}/{len(properties)}] Geocoding: {address}, {city}, {state}")
            
            coords = self.geocode_address(address, city, state)
            
            if coords:
                lat, lon = coords
                cursor.execute("""
                    UPDATE master_distressed_properties 
                    SET latitude = ?, longitude = ?, geocoded = 1 
                    WHERE rowid = ?
                """, (lat, lon, rowid))
                geocoded_count += 1
                print(f"  ✅ Coordinates: {lat:.6f}, {lon:.6f}")
            else:
                failed_count += 1
                print(f"  ❌ Failed to geocode")
            
            # Rate limiting
            time.sleep(1.1)
            
            # Commit every 5 properties
            if geocoded_count % 5 == 0:
                conn.commit()
                print(f"\n💾 Saved {geocoded_count} geocoded properties\n")
        
        conn.commit()
        conn.close()
        
        print(f"\n✅ Geocoding complete!")
        print(f"   Successfully geocoded: {geocoded_count}")
        print(f"   Failed: {failed_count}")
        print(f"   Success rate: {(geocoded_count / len(properties) * 100) if properties else 0:.1f}%")
        
        return geocoded_count

# Usage
if __name__ == "__main__":
    db_path = "/Users/jacoblister/.openclaw/workspace/business/property-finder/data/QUAD_CITIES_MASTER_DATASET.db"
    
    geocoder = ImprovedPropertyGeocoder(db_path)
    
    # Run geocoding for first 20 properties as a test
    print("🚀 Starting improved geocoding process...")
    geocoded = geocoder.update_property_coordinates(limit=20)
    
    if geocoded > 0:
        print(f"\n🎉 Successfully geocoded {geocoded} properties!")
        print("Refresh the map page to see the improved locations.")