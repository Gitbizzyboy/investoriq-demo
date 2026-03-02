#!/usr/bin/env python3
"""Test geocoding functionality"""

import sqlite3
import sys

print("Testing database access...")

db_path = "/Users/jacoblister/.openclaw/workspace/business/property-finder/data/QUAD_CITIES_MASTER_DATASET.db"

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check table structure
    print("\nChecking table structure...")
    cursor.execute("PRAGMA table_info(master_distressed_properties)")
    columns = cursor.fetchall()
    print(f"Found {len(columns)} columns")
    
    # Check if geocoding columns exist
    column_names = [col[1] for col in columns]
    print(f"Columns: {', '.join(column_names[:10])}...")
    
    has_latitude = 'latitude' in column_names
    has_longitude = 'longitude' in column_names
    has_geocoded = 'geocoded' in column_names
    
    print(f"\nGeocoding columns exist: latitude={has_latitude}, longitude={has_longitude}, geocoded={has_geocoded}")
    
    # Try to add columns if they don't exist
    if not has_latitude:
        print("Adding latitude column...")
        cursor.execute("ALTER TABLE master_distressed_properties ADD COLUMN latitude REAL")
        
    if not has_longitude:
        print("Adding longitude column...")
        cursor.execute("ALTER TABLE master_distressed_properties ADD COLUMN longitude REAL")
        
    if not has_geocoded:
        print("Adding geocoded column...")
        cursor.execute("ALTER TABLE master_distressed_properties ADD COLUMN geocoded BOOLEAN DEFAULT 0")
    
    conn.commit()
    
    # Get a sample property
    print("\nGetting sample property...")
    cursor.execute("SELECT rowid, property_address, city, state FROM master_distressed_properties LIMIT 1")
    sample = cursor.fetchone()
    
    if sample:
        print(f"Sample property: {sample[1]}, {sample[2]}, {sample[3]}")
    
    conn.close()
    print("\nDatabase test complete!")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)