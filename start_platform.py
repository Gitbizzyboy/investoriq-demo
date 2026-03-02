#!/usr/bin/env python3
"""
InvestorIQ Property Intelligence Platform Startup
Complete investor platform with integrated intelligence systems
"""

import os
import sys
import sqlite3
import json
import subprocess
import time
from datetime import datetime

def check_dependencies():
    """Check and install required dependencies"""
    print("🔧 Checking platform dependencies...")
    
    required_packages = [
        'flask',
        'sqlite3'  # Built-in with Python
    ]
    
    try:
        import flask
        print("   ✅ Flask installed")
    except ImportError:
        print("   ❌ Flask not found, installing...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'flask'])
    
    print("   ✅ All dependencies satisfied")

def verify_database_connections():
    """Verify all database files exist"""
    print("💾 Verifying database connections...")
    
    database_paths = [
        '/Users/jacoblister/.openclaw/workspace/business/property-finder/data/QUAD_CITIES_MASTER_DATASET.db',
        '/Users/jacoblister/.openclaw/workspace/business/property-finder/data/real_estate_intelligence.db'
    ]
    
    for db_path in database_paths:
        if os.path.exists(db_path):
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                conn.close()
                print(f"   ✅ {os.path.basename(db_path)}: {len(tables)} tables")
            except Exception as e:
                print(f"   ❌ Error with {db_path}: {e}")
        else:
            print(f"   ⚠️ Database not found: {os.path.basename(db_path)}")
    
def create_platform_summary():
    """Create platform summary for display"""
    print("📊 Generating platform summary...")
    
    try:
        master_db = '/Users/jacoblister/.openclaw/workspace/business/property-finder/data/QUAD_CITIES_MASTER_DATASET.db'
        
        if os.path.exists(master_db):
            conn = sqlite3.connect(master_db)
            cursor = conn.cursor()
            
            # Get summary stats
            cursor.execute("SELECT COUNT(*) FROM master_distressed_properties")
            total_properties = cursor.fetchone()[0]
            
            cursor.execute("SELECT SUM(tax_amount) FROM master_distressed_properties WHERE tax_amount > 0")
            total_tax_debt = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT COUNT(*) FROM master_distressed_properties WHERE investment_potential = 'High Opportunity'")
            high_opportunities = cursor.fetchone()[0]
            
            conn.close()
            
            summary = {
                'total_properties': total_properties,
                'total_tax_debt': total_tax_debt,
                'high_opportunities': high_opportunities,
                'platform_ready': True,
                'last_updated': datetime.now().isoformat()
            }
            
            print(f"   📊 {total_properties} properties loaded")
            print(f"   💰 ${total_tax_debt:,.2f} total tax debt")
            print(f"   🎯 {high_opportunities} high opportunity deals")
            
            return summary
        else:
            print("   ⚠️ Master database not found - platform will show demo data")
            return {'platform_ready': False}
            
    except Exception as e:
        print(f"   ❌ Error generating summary: {e}")
        return {'platform_ready': False}

def start_platform():
    """Start the complete platform"""
    print("🚀 INVESTORIQ PROPERTY INTELLIGENCE PLATFORM")
    print("=" * 60)
    print("🎯 Complete investor platform with integrated intelligence")
    print("📊 Features: Property analysis, mapping, social intel, business intel")
    print("=" * 60)
    
    # Verify environment
    check_dependencies()
    verify_database_connections()
    summary = create_platform_summary()
    
    # Change to platform directory
    platform_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(platform_dir)
    
    print(f"\\n📁 Platform directory: {platform_dir}")
    
    # Display platform features
    print(f"\\n🎯 PLATFORM FEATURES:")
    print("   ✅ Interactive Property Dashboard")
    print("   ✅ Detailed Property Map with Filtering")
    print("   ✅ Social Media Intelligence Integration")
    print("   ✅ Business Intelligence & Analytics")
    print("   ✅ ROI Analysis & Deal Pipeline")
    print("   ✅ Competitive Intelligence")
    print("   ✅ Professional Network Directory")
    
    # Display access information
    print(f"\\n🌐 ACCESS INFORMATION:")
    print("   🏠 Main Dashboard: http://localhost:5001")
    print("   🗺️ Interactive Map: http://localhost:5001/map")
    print("   👥 Social Intelligence: http://localhost:5001/social-intelligence")
    print("   📊 Business Intelligence: http://localhost:5001/business-intelligence")
    
    print(f"\\n💼 TARGET AUDIENCE:")
    print("   👨‍💼 Individual Investors (like Bryce)")
    print("   🏢 Institutions (like SFR3)")
    print("   🤝 Real Estate Professionals")
    print("   📈 Investment Firms & Wholesalers")
    
    # Start Flask app
    print(f"\\n🚀 Starting Flask server...")
    print("   Press Ctrl+C to stop the platform")
    print("=" * 60)
    
    # Import and run the Flask app
    try:
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\\n\\n🛑 Platform stopped by user")
    except Exception as e:
        print(f"\\n❌ Error starting platform: {e}")
        print("\\n🔧 Troubleshooting:")
        print("   1. Ensure you're in the platform directory")
        print("   2. Check that app.py exists")
        print("   3. Verify database files are accessible")
        print("   4. Try: python3 app.py")

if __name__ == "__main__":
    start_platform()