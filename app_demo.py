#!/usr/bin/env python3
"""
InvestorIQ Property Intelligence Platform - DEMO VERSION
Sanitized demo with fictional data - Safe for public deployment
"""

from flask import Flask, render_template, jsonify, request
import sqlite3
import json
import os
import re
from datetime import datetime

app = Flask(__name__)

class PropertyIntelligencePlatformDemo:
    def __init__(self):
        self.init_database_connections()
        
    def init_database_connections(self):
        """Initialize demo database connections"""
        # Use demo database with fictional data
        self.master_db = './DEMO_PROPERTIES.db'
        
    def get_all_properties(self, filters=None):
        """Get all demo properties with optional filters"""
        try:
            # Check if database exists
            if not os.path.exists(self.master_db):
                print(f"Demo database not found: {self.master_db}")
                return []
                
            conn = sqlite3.connect(self.master_db)
            cursor = conn.cursor()
            
            query = '''
            SELECT county, state, property_address, owner_name, city, assessed_value, 
                   tax_amount, distressed_type, distressed_score, investment_potential,
                   methodology_category, market_tier, phone_lookup_url, street_view_url,
                   google_maps_url, distress_indicators, latitude, longitude, geocoded
            FROM master_distressed_properties
            '''
            
            conditions = []
            params = []
            
            if filters:
                if filters.get('county'):
                    conditions.append("county = ?")
                    params.append(filters['county'])
                if filters.get('city'):
                    conditions.append("city = ?")
                    params.append(filters['city'])
                if filters.get('investment_potential'):
                    conditions.append("investment_potential = ?")
                    params.append(filters['investment_potential'])
                if filters.get('methodology_category'):
                    conditions.append("methodology_category = ?")
                    params.append(filters['methodology_category'])
                if filters.get('min_score'):
                    conditions.append("distressed_score >= ?")
                    params.append(int(filters['min_score']))
                if filters.get('max_value'):
                    conditions.append("assessed_value <= ?")
                    params.append(float(filters['max_value']))
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY distressed_score DESC, tax_amount DESC"
            
            cursor.execute(query, params)
            properties = []
            
            for row in cursor.fetchall():
                # Create demo-safe URLs
                fixed_street_view_url = self.fix_street_view_url(row[2])
                google_maps_search = self.fix_street_view_url(row[2])
                apple_maps_url = self.create_apple_maps_url(row[2]) if row[2] else "#"
                
                property_data = {
                    'county': row[0],
                    'state': row[1],
                    'property_address': row[2],
                    'owner_name': row[3],
                    'city': row[4],
                    'assessed_value': row[5],
                    'tax_amount': row[6],
                    'distressed_type': row[7],
                    'distressed_score': row[8],
                    'investment_potential': row[9],
                    'methodology_category': row[10],
                    'market_tier': row[11],
                    'phone_lookup_url': '#',  # Disabled for demo
                    'street_view_url': fixed_street_view_url,
                    'street_view_thumbnail': self.create_property_thumbnail(row[2], row[4], row[0]) if row[2] else None,
                    'google_maps_url': google_maps_search,
                    'apple_maps_url': apple_maps_url,
                    'original_google_maps_url': row[14],
                    'distress_indicators': row[15],
                    'latitude': row[16] if len(row) > 16 else None,
                    'longitude': row[17] if len(row) > 17 else None,
                    'geocoded': row[18] if len(row) > 18 else False
                }
                
                # Calculate indicator ratings
                property_data['ratings'] = self.calculate_indicator_ratings(property_data)
                
                properties.append(property_data)
            
            conn.close()
            return properties
            
        except Exception as e:
            print(f"Error getting properties: {e}")
            return []
    
    def fix_street_view_url(self, address):
        """Create working Google Maps URL that shows property location"""
        import urllib.parse
        if not address:
            return "#"
        
        # Clean up address - remove extra spaces and newlines
        clean_address = ' '.join(address.replace('\n', ' ').split())
        encoded_address = urllib.parse.quote(clean_address)
        
        # Use Google Maps search format - most reliable for finding locations
        return f"https://www.google.com/maps/search/{encoded_address}"
    
    def create_apple_maps_url(self, address):
        """Create Apple Maps URL as alternative"""
        import urllib.parse
        if not address:
            return "#"
        
        clean_address = ' '.join(address.replace('\n', ' ').split())
        encoded_address = urllib.parse.quote(clean_address)
        return f"https://maps.apple.com/?q={encoded_address}"
    
    def create_property_thumbnail(self, address, city, county):
        """Create demo property image placeholder"""
        import urllib.parse
        
        if not address:
            return self.create_fallback_image("Demo Property")
        
        # Use enhanced placeholder for demo
        address_short = address.split(',')[0][:20] if address else "Demo Property"
        encoded_text = urllib.parse.quote(f"DEMO: {address_short}")
        return f"https://via.placeholder.com/400x300/4285f4/ffffff?text={encoded_text}"
        
    def create_fallback_image(self, text):
        """Create enhanced placeholder image"""
        import urllib.parse
        encoded_text = urllib.parse.quote(f"DEMO: {text}")
        return f"https://via.placeholder.com/400x300/667eea/ffffff?text={encoded_text}"
    
    def calculate_indicator_ratings(self, property_data):
        """Calculate ratings for each distress indicator"""
        ratings = {
            'tax_distress': 0,
            'foreclosure_risk': 0,
            'value_opportunity': 0,
            'owner_motivation': 0,
            'acquisition_ease': 0
        }
        
        # Tax distress rating
        tax_amount = property_data.get('tax_amount', 0) or 0
        if tax_amount >= 100000:
            ratings['tax_distress'] = 5
        elif tax_amount >= 50000:
            ratings['tax_distress'] = 4
        elif tax_amount >= 25000:
            ratings['tax_distress'] = 3
        elif tax_amount >= 10000:
            ratings['tax_distress'] = 2
        elif tax_amount > 0:
            ratings['tax_distress'] = 1
        
        # Foreclosure risk rating
        distressed_type = property_data.get('distressed_type', '').lower()
        if 'foreclosure' in distressed_type or 'sheriff' in distressed_type:
            ratings['foreclosure_risk'] = 5
        elif 'tax_foreclosure' in distressed_type:
            ratings['foreclosure_risk'] = 4
        elif 'legal' in distressed_type:
            ratings['foreclosure_risk'] = 3
        elif tax_amount >= 50000:
            ratings['foreclosure_risk'] = 2
        elif tax_amount >= 25000:
            ratings['foreclosure_risk'] = 1
        
        # Value opportunity rating
        assessed_value = property_data.get('assessed_value', 0) or 0
        market_tier = property_data.get('market_tier', '')
        if market_tier == 'Deep-Value' and tax_amount > assessed_value * 0.5:
            ratings['value_opportunity'] = 5
        elif assessed_value < 75000 and tax_amount > 20000:
            ratings['value_opportunity'] = 4
        elif assessed_value < 100000:
            ratings['value_opportunity'] = 3
        elif assessed_value < 150000:
            ratings['value_opportunity'] = 2
        else:
            ratings['value_opportunity'] = 1
        
        # Owner motivation rating
        indicators = property_data.get('distress_indicators', '') or ''
        motivation_score = 0
        if 'out_of_state' in indicators.lower():
            motivation_score += 1
        if 'llc' in indicators.lower() or 'trust' in indicators.lower():
            motivation_score += 1
        if 'estate' in distressed_type.lower():
            motivation_score += 2
        if tax_amount >= 50000:
            motivation_score += 2
        
        ratings['owner_motivation'] = min(motivation_score, 5)
        
        # Acquisition ease rating
        distressed_score = property_data.get('distressed_score', 0) or 0
        if distressed_score >= 300:
            ratings['acquisition_ease'] = 5
        elif distressed_score >= 200:
            ratings['acquisition_ease'] = 4
        elif distressed_score >= 100:
            ratings['acquisition_ease'] = 3
        elif distressed_score >= 50:
            ratings['acquisition_ease'] = 2
        else:
            ratings['acquisition_ease'] = 1
        
        return ratings
    
    def get_analytics_summary(self):
        """Get demo platform analytics summary"""
        try:
            if not os.path.exists(self.master_db):
                return {}
                
            conn = sqlite3.connect(self.master_db)
            cursor = conn.cursor()
            
            # Total properties
            cursor.execute("SELECT COUNT(*) FROM master_distressed_properties")
            total_properties = cursor.fetchone()[0]
            
            # By county
            cursor.execute("SELECT county, COUNT(*) FROM master_distressed_properties GROUP BY county")
            county_breakdown = dict(cursor.fetchall())
            
            # By investment potential
            cursor.execute("SELECT investment_potential, COUNT(*) FROM master_distressed_properties GROUP BY investment_potential")
            potential_breakdown = dict(cursor.fetchall())
            
            # By methodology
            cursor.execute("SELECT methodology_category, COUNT(*) FROM master_distressed_properties GROUP BY methodology_category")
            methodology_breakdown = dict(cursor.fetchall())
            
            # Top opportunities
            cursor.execute('''
            SELECT property_address, city, county, tax_amount, investment_potential
            FROM master_distressed_properties 
            WHERE tax_amount > 50000
            ORDER BY tax_amount DESC
            LIMIT 10
            ''')
            top_opportunities = [
                {
                    'address': row[0],
                    'city': row[1],
                    'county': row[2],
                    'tax_amount': row[3],
                    'potential': row[4]
                } for row in cursor.fetchall()
            ]
            
            # Average values
            cursor.execute('''
            SELECT 
                AVG(assessed_value) as avg_value,
                AVG(tax_amount) as avg_tax,
                AVG(distressed_score) as avg_score,
                SUM(tax_amount) as total_tax_debt
            FROM master_distressed_properties 
            WHERE assessed_value > 0
            ''')
            
            averages = cursor.fetchone()
            
            conn.close()
            
            return {
                'total_properties': total_properties,
                'county_breakdown': county_breakdown,
                'potential_breakdown': potential_breakdown,
                'methodology_breakdown': methodology_breakdown,
                'top_opportunities': top_opportunities,
                'avg_assessed_value': averages[0] or 0,
                'avg_tax_amount': averages[1] or 0,
                'avg_distressed_score': averages[2] or 0,
                'total_tax_debt': averages[3] or 0
            }
            
        except Exception as e:
            print(f"Error getting analytics: {e}")
            return {}
    
    def get_cities_list(self):
        """Get list of cities for filtering"""
        try:
            if not os.path.exists(self.master_db):
                return []
                
            conn = sqlite3.connect(self.master_db)
            cursor = conn.cursor()
            
            cursor.execute("SELECT DISTINCT city FROM master_distressed_properties ORDER BY city")
            cities = [row[0] for row in cursor.fetchall() if row[0]]
            
            conn.close()
            return cities
            
        except Exception as e:
            return []

# Initialize demo platform
platform = PropertyIntelligencePlatformDemo()

@app.route('/')
def index():
    """Main demo dashboard with disclaimers"""
    analytics = platform.get_analytics_summary()
    cities = platform.get_cities_list()
    
    # Add demo disclaimer to analytics
    analytics['is_demo'] = True
    analytics['disclaimer'] = "This is a demonstration version with fictional data for showcase purposes only."
    
    return render_template('demo_index.html', analytics=analytics, cities=cities)

@app.route('/api/properties')
def api_properties():
    """API endpoint for demo properties with filtering"""
    filters = {}
    
    if request.args.get('county'):
        filters['county'] = request.args.get('county')
    if request.args.get('city'):
        filters['city'] = request.args.get('city')
    if request.args.get('investment_potential'):
        filters['investment_potential'] = request.args.get('investment_potential')
    if request.args.get('methodology_category'):
        filters['methodology_category'] = request.args.get('methodology_category')
    if request.args.get('min_score'):
        filters['min_score'] = request.args.get('min_score')
    if request.args.get('max_value'):
        filters['max_value'] = request.args.get('max_value')
    
    properties = platform.get_all_properties(filters)
    return jsonify({
        'success': True,
        'properties': properties,
        'is_demo': True,
        'disclaimer': 'This is demonstration data only. All property information is fictional.'
    })

@app.route('/api/analytics')
def api_analytics():
    """API endpoint for demo analytics data"""
    analytics = platform.get_analytics_summary()
    analytics['is_demo'] = True
    analytics['disclaimer'] = "Demonstration data only - all figures are fictional"
    return jsonify(analytics)

@app.route('/map')
def map_view():
    """Demo map view of properties"""
    return render_template('demo_map.html')

if __name__ == '__main__':
    # Get port from environment variable or default to 5001
    port = int(os.environ.get('PORT', 5001))
    
    print("🚀 InvestorIQ Property Intelligence Platform (DEMO VERSION)")
    print(f"🎯 Starting demo server on port {port}")
    print("🔒 SAFE FOR PUBLIC DEPLOYMENT - All data is fictional")
    
    # Check database existence
    if os.path.exists('./DEMO_PROPERTIES.db'):
        print("✅ Demo database found")
    else:
        print("❌ Demo database not found - run create_demo_database.py first")
    
    app.run(debug=False, host='0.0.0.0', port=port)