#!/usr/bin/env python3
"""
Geocode all remaining properties - careful and methodical approach
"""

import sqlite3
import sys
sys.path.append('.')
from geocode_properties_v2 import ImprovedPropertyGeocoder

db_path = "/Users/jacoblister/.openclaw/workspace/business/property-finder/data/QUAD_CITIES_MASTER_DATASET.db"

# Check current status
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM master_distressed_properties")
total = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM master_distressed_properties WHERE geocoded = 1")
geocoded = cursor.fetchone()[0]

remaining = total - geocoded

print(f"📊 Current Status:")
print(f"   Total properties: {total}")
print(f"   Already geocoded: {geocoded}")
print(f"   Remaining to geocode: {remaining}")

conn.close()

if remaining > 0:
    print(f"\n🚀 Starting geocoding for {remaining} remaining properties...")
    print("⏱️  This will take approximately {:.1f} minutes\n".format(remaining * 1.1 / 60))
    
    geocoder = ImprovedPropertyGeocoder(db_path)
    
    # Geocode all remaining properties
    result = geocoder.update_property_coordinates(limit=remaining)
    
    print(f"\n✅ Geocoding session complete!")
else:
    print("\n✅ All properties already geocoded!")