#!/usr/bin/env python3
"""
Test the Google Maps URLs we're generating
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from app import PropertyIntelligencePlatform

# Create platform instance
platform = PropertyIntelligencePlatform()

# Get a sample of properties
properties = platform.get_all_properties()

print("🔍 TESTING GOOGLE MAPS URLs")
print("=" * 60)

if properties:
    for i, prop in enumerate(properties[:5]):  # Test first 5 properties
        print(f"\n🏠 Property {i+1}:")
        print(f"   Address: {prop['property_address']}")
        print(f"   City: {prop['city']}")
        print(f"   Google Maps URL: {prop['google_maps_url']}")
        if 'apple_maps_url' in prop:
            print(f"   Apple Maps URL: {prop['apple_maps_url']}")
        
        # Test the URL by opening it (you can copy and paste)
        print(f"   🌐 Test this URL in your browser:")
        print(f"   {prop['google_maps_url']}")
        print("-" * 40)
else:
    print("❌ No properties found!")

print("\n📋 INSTRUCTIONS:")
print("1. Copy any Google Maps URL above")  
print("2. Paste it in your browser")
print("3. Check if it shows the property location")
print("4. If it works, the platform is fixed!")