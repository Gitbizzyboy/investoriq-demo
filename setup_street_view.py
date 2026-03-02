#!/usr/bin/env python3
"""
Street View Setup Helper
Enables real property photos with Google Street View API
"""

import os
import sys

def check_api_key():
    """Check if Google Maps API key is configured"""
    api_key = os.environ.get('GOOGLE_MAPS_API_KEY', '')
    
    print("🏠 STREET VIEW SETUP CHECKER")
    print("=" * 50)
    
    if api_key:
        print(f"✅ API Key Found: {api_key[:10]}...")
        print("✅ Street View images will load automatically!")
        return True
    else:
        print("❌ No API Key Found")
        print("\n📋 TO ENABLE REAL STREET VIEW PHOTOS:")
        print("1. Get FREE API key: https://console.cloud.google.com/apis/credentials")
        print("2. Enable 'Street View Static API'")
        print("3. Set environment variable:")
        print("   export GOOGLE_MAPS_API_KEY='your_key_here'")
        print("4. Restart the platform")
        print("\n💡 FREE TIER: 25,000 images/month (perfect for property platforms)")
        return False

def setup_api_key():
    """Interactive API key setup"""
    print("\n🔧 INTERACTIVE SETUP")
    print("-" * 30)
    
    api_key = input("Enter your Google Maps API key (or press Enter to skip): ").strip()
    
    if api_key:
        # Create a simple shell script to set the environment variable
        script_content = f"""#!/bin/bash
# Google Maps API Key Setup
export GOOGLE_MAPS_API_KEY="{api_key}"

# Start the platform with API key
echo "🔑 Starting platform with Street View enabled..."
cd /Users/jacoblister/.openclaw/workspace/business/property-finder/platform
python3 app.py
"""
        
        with open('start_with_streetview.sh', 'w') as f:
            f.write(script_content)
        
        os.chmod('start_with_streetview.sh', 0o755)
        
        print("✅ Setup complete!")
        print("📝 Created: start_with_streetview.sh")
        print("🚀 Run: ./start_with_streetview.sh")
        print("\n🎯 Your platform will now show real property photos!")
    else:
        print("⏭️  Skipped - You can enable this later")

def show_examples():
    """Show example of street view URLs that will be generated"""
    print("\n🖼️  EXAMPLE STREET VIEW IMAGES")
    print("-" * 40)
    
    example_addresses = [
        "5114 109TH AVE MILAN, IL 61264",
        "1247 W 3rd Street Davenport, IA",
        "3808 11 AVE MOLINE, IL 61265"
    ]
    
    api_key = os.environ.get('GOOGLE_MAPS_API_KEY', 'YOUR_API_KEY_HERE')
    
    for addr in example_addresses:
        import urllib.parse
        encoded = urllib.parse.quote(addr)
        url = f"https://maps.googleapis.com/maps/api/streetview?size=400x300&location={encoded}&key={api_key}"
        print(f"📍 {addr}")
        print(f"   🌐 {url}")
        print()

if __name__ == "__main__":
    has_key = check_api_key()
    
    if not has_key:
        print("\n" + "="*50)
        setup_choice = input("Would you like to set up API key now? (y/n): ").lower()
        if setup_choice == 'y':
            setup_api_key()
    
    print("\n📊 CURRENT STATUS:")
    if has_key or os.environ.get('GOOGLE_MAPS_API_KEY'):
        print("✅ Street View: ENABLED")
        print("📸 Property photos will load automatically")
    else:
        print("⚪ Street View: PLACEHOLDER MODE")
        print("🔧 Run setup to enable real photos")
    
    show_examples()
    
    print("\n🚀 Platform URL: http://localhost:5001")
    print("🎯 Ready for investor presentations!")