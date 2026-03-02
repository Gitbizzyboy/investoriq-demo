#!/usr/bin/env python3
"""Quick fix for Milan properties - test geocoding approach"""

import sqlite3
import requests
import time

db_path = "/Users/jacoblister/.openclaw/workspace/business/property-finder/data/QUAD_CITIES_MASTER_DATASET.db"

# Manual address fixes for common Milan patterns
address_fixes = {
    "52 ST CT": "52ND STREET COURT",
    "109 AVE": "109TH AVENUE", 
    "106TH AVE": "106TH AVENUE",
    "52ND ST CT": "52ND STREET COURT"
}

def geocode_test(address, city="Milan", state="IL"):
    """Test geocoding with normalized address"""
    # Normalize the address
    normalized = address.upper()
    for old, new in address_fixes.items():
        if old in normalized:
            normalized = normalized.replace(old, new)
            break
    
    full_address = f"{normalized}, {city}, {state}, USA"
    print(f"\nTrying to geocode: {full_address}")
    
    headers = {'User-Agent': 'InvestorIQ/1.0'}
    params = {
        'q': full_address,
        'format': 'json',
        'limit': 1,
        'countrycodes': 'us'
    }
    
    try:
        response = requests.get("https://nominatim.openstreetmap.org/search", 
                              params=params, headers=headers, timeout=5)
        data = response.json()
        
        if data:
            lat = float(data[0]['lat'])
            lon = float(data[0]['lon'])
            print(f"  SUCCESS: {lat:.6f}, {lon:.6f}")
            print(f"  Display name: {data[0]['display_name']}")
            
            # Check if it's specific or city center
            if abs(lat - 41.453) < 0.005 and abs(lon - -90.572) < 0.005:
                print("  WARNING: This is still city center!")
                return None
            return (lat, lon)
        else:
            print("  FAILED: No results")
    except Exception as e:
        print(f"  ERROR: {e}")
    
    return None

# Test a few addresses
test_addresses = [
    "10724 52 ST CT",
    "5109 109 AVE",
    "5100 106TH AVE"
]

print("Testing Milan address geocoding fixes...")
print("=" * 50)

for addr in test_addresses:
    full_addr = f"{addr}\nMILAN, IL 61264"
    result = geocode_test(addr)
    time.sleep(1.5)  # Rate limit

print("\n" + "=" * 50)
print("If any addresses geocoded successfully, we can apply this fix to all Milan properties.")