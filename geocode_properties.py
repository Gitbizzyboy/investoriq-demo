#!/usr/bin/env python3
"""
Geocode all property addresses and store coordinates in the database
This runs on the server side to avoid CORS issues and improve performance
"""

import sqlite3
import requests
import time
import json
from typing import Tuple, Optional

class PropertyGeocoder:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.geocoding_service = "https://nominatim.openstreetmap.org/search"
        self.headers = {
            'User-Agent': 'InvestorIQ/1.0 (property investment platform)'
        }
        
    def geocode_address(self, address: str, city: str, state: str = "IL") -> Optional[Tuple[float, float]]:
        """Geocode a single address using Nominatim API"""
        # Clean and format the address
        full_address = f"{address}, {city}, {state}, USA"
        
        params = {
            'q': full_address,
            'format': 'json',
            'limit': 1,
            'countrycodes': 'us'
        }
        
        try:
            response = requests.get(self.geocoding_service, params=params, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            if data and len(data) > 0:
                lat = float(data[0]['lat'])
                lon = float(data[0]['lon'])
                return (lat, lon)
            
        except Exception as e:
            print(f"Geocoding error for {address}: {e}")
            
        return None
    
    def update_property_coordinates(self):
        """Update all properties with geocoded coordinates"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Add columns for coordinates if they don't exist
        try:
            cursor.execute("ALTER TABLE master_distressed_properties ADD COLUMN latitude REAL")
            cursor.execute("ALTER TABLE master_distressed_properties ADD COLUMN longitude REAL")
            cursor.execute("ALTER TABLE master_distressed_properties ADD COLUMN geocoded BOOLEAN DEFAULT 0")
            print("Added coordinate columns to database")
        except:
            print("Coordinate columns already exist")
        
        # Get all properties without coordinates
        cursor.execute("""
            SELECT rowid, property_address, city, state 
            FROM master_distressed_properties 
            WHERE latitude IS NULL OR longitude IS NULL
            LIMIT 200
        """)
        
        properties = cursor.fetchall()
        print(f"Found {len(properties)} properties to geocode")
        
        geocoded_count = 0
        for prop in properties:
            rowid, address, city, state = prop
            state = state or "IL"  # Default to Illinois
            
            print(f"Geocoding {address}, {city}, {state}...")
            coords = self.geocode_address(address, city, state)
            
            if coords:
                lat, lon = coords
                cursor.execute("""
                    UPDATE master_distressed_properties 
                    SET latitude = ?, longitude = ?, geocoded = 1 
                    WHERE rowid = ?
                """, (lat, lon, rowid))
                geocoded_count += 1
                print(f"  ✓ Success: {lat:.6f}, {lon:.6f}")
            else:
                print(f"  ✗ Failed to geocode")
            
            # Rate limiting - Nominatim requires max 1 request per second
            time.sleep(1.1)
            
            # Commit every 10 properties
            if geocoded_count % 10 == 0:
                conn.commit()
                print(f"Committed {geocoded_count} geocoded properties")
        
        conn.commit()
        conn.close()
        
        print(f"\nGeocoding complete! Successfully geocoded {geocoded_count}/{len(properties)} properties")
        return geocoded_count

    def get_geocoded_stats(self):
        """Get statistics about geocoded properties"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM master_distressed_properties")
        total = cursor.fetchone()[0]
        
        # Check if geocoded column exists
        cursor.execute("PRAGMA table_info(master_distressed_properties)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'geocoded' in columns:
            cursor.execute("SELECT COUNT(*) FROM master_distressed_properties WHERE geocoded = 1")
            geocoded = cursor.fetchone()[0]
        else:
            geocoded = 0
        
        conn.close()
        
        return {
            'total_properties': total,
            'geocoded_properties': geocoded,
            'remaining': total - geocoded,
            'percentage': (geocoded / total * 100) if total > 0 else 0
        }

# Usage
if __name__ == "__main__":
    db_path = "/Users/jacoblister/.openclaw/workspace/business/property-finder/data/QUAD_CITIES_MASTER_DATASET.db"
    
    geocoder = PropertyGeocoder(db_path)
    
    # Get current stats
    stats = geocoder.get_geocoded_stats()
    print(f"Current geocoding status: {stats['geocoded_properties']}/{stats['total_properties']} ({stats['percentage']:.1f}%)")
    
    # Run geocoding
    if stats['remaining'] > 0:
        print(f"\nStarting geocoding for {stats['remaining']} properties...")
        geocoded = geocoder.update_property_coordinates()
        
        # Get updated stats
        new_stats = geocoder.get_geocoded_stats()
        print(f"\nNew status: {new_stats['geocoded_properties']}/{new_stats['total_properties']} ({new_stats['percentage']:.1f}%)")
    else:
        print("All properties already geocoded!")