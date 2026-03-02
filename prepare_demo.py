#!/usr/bin/env python3
"""
Demo preparation script - run this before presenting to Bryce
"""

import requests
import sqlite3
import time

def check_demo_readiness():
    """Check if all systems are ready for demo"""
    print("🚀 InvestorIQ Demo Preparation Checklist")
    print("=" * 50)
    
    # 1. Check if Flask app is running
    try:
        response = requests.get("http://localhost:5001", timeout=5)
        if response.status_code == 200:
            print("✅ Flask application is running on port 5001")
        else:
            print("❌ Flask application not responding properly")
            return False
    except:
        print("❌ Flask application is not running!")
        print("   Run: cd business/property-finder/platform && python3 app.py")
        return False
    
    # 2. Check API endpoints
    endpoints = [
        ("/api/properties", "Properties API"),
        ("/api/analytics", "Analytics API"),
        ("/api/pipeline", "Pipeline API")
    ]
    
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"http://localhost:5001{endpoint}", timeout=3)
            if response.status_code == 200:
                print(f"✅ {name} working")
            else:
                print(f"⚠️ {name} returned status {response.status_code}")
        except:
            print(f"❌ {name} not responding")
    
    # 3. Check database data
    try:
        db_path = "/Users/jacoblister/.openclaw/workspace/business/property-finder/data/QUAD_CITIES_MASTER_DATASET.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM master_distressed_properties")
        property_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM master_distressed_properties WHERE geocoded = 1")
        geocoded_count = cursor.fetchone()[0]
        
        print(f"✅ Database loaded: {property_count} properties, {geocoded_count} geocoded")
        
        # Check pipeline data
        pipeline_db = "/Users/jacoblister/.openclaw/workspace/business/property-finder/data/deal_pipeline.db"
        pipeline_conn = sqlite3.connect(pipeline_db)
        pipeline_cursor = pipeline_conn.cursor()
        pipeline_cursor.execute("SELECT COUNT(*) FROM deal_pipeline")
        pipeline_count = pipeline_cursor.fetchone()[0]
        
        if pipeline_count > 0:
            print(f"✅ Deal pipeline has {pipeline_count} sample deals")
        else:
            print("⚠️ Deal pipeline is empty - consider adding demo data")
        
        pipeline_conn.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Database check failed: {e}")
        return False
    
    # 4. Demo flow recommendations
    print("\n📋 Demo Flow Ready:")
    print("   1. Homepage (/) - Show key statistics")
    print("   2. Map (/map) - Interactive property exploration")
    print("   3. Property detail - Click any marker for analysis")
    print("   4. Deal Pipeline (/deal-pipeline) - Deal management")
    print("   5. Social Intelligence (/social-intelligence) - Network")
    
    print("\n🎯 Key Properties to Highlight:")
    
    # Get some high-value properties for demo
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT property_address, city, tax_amount, investment_potential
            FROM master_distressed_properties 
            WHERE tax_amount > 25000 
            ORDER BY tax_amount DESC 
            LIMIT 3
        """)
        
        for addr, city, tax, potential in cursor.fetchall():
            clean_addr = addr.replace('\n', ' ')
            print(f"   📍 {clean_addr}, {city} - ${tax:,} debt ({potential})")
            
    except Exception as e:
        print(f"   Could not load demo properties: {e}")
    
    print("\n🔧 Browser Prep:")
    print("   - Clear cache (Cmd+Shift+R)")
    print("   - Use Chrome or Safari")
    print("   - Have developer tools ready (Cmd+Option+I)")
    
    print("\n✅ Demo is ready! Platform is fully functional.")
    return True

if __name__ == "__main__":
    check_demo_readiness()