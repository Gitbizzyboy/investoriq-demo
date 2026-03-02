#!/usr/bin/env python3
"""Test geocoding API directly"""

import requests
import json

# Test addresses - try different formats
addresses = [
    "10724 52nd Street Court, Milan, Illinois",
    "10724 52nd St Ct, Milan, IL", 
    "Milan, Illinois",
    "1234 Main Street, Davenport, Iowa"
]

for address in addresses:

    print(f"\nTesting: {address}")
    
    headers = {
        'User-Agent': 'InvestorIQ/1.0 (property investment platform)'
    }
    
    params = {
        'q': address,
        'format': 'json',
        'limit': 1,
        'countrycodes': 'us'
    }
    
    try:
        response = requests.get("https://nominatim.openstreetmap.org/search", params=params, headers=headers, timeout=5)
        
        data = response.json()
        
        if data and len(data) > 0:
            lat = float(data[0]['lat'])
            lon = float(data[0]['lon'])
            print(f"  ✓ Success! Coordinates: {lat}, {lon}")
            print(f"    Display name: {data[0]['display_name']}")
        else:
            print(f"  ✗ No results found")
            
    except Exception as e:
        print(f"  ✗ Error: {e}")
    
    import time
    time.sleep(1)  # Rate limit