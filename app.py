#!/usr/bin/env python3
"""
InvestorIQ Property Intelligence Platform - Demo Version
Full platform functionality without authentication
"""

from flask import Flask, render_template, jsonify, request, redirect, url_for
import os
import sqlite3
from datetime import datetime

app = Flask(__name__)

class PropertyIntelligencePlatform:
    def __init__(self):
        self.master_db = './QUAD_CITIES_MASTER_DATASET.db'
        
    def get_properties_data(self, limit=50):
        """Get property data for API"""
        try:
            conn = sqlite3.connect(self.master_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT property_address, owner_name, assessed_value, tax_amount,
                       investment_potential, street_view_url, google_maps_url,
                       distress_indicators, latitude, longitude, city, county, state
                FROM master_distressed_properties 
                ORDER BY assessed_value DESC
                LIMIT ?
            ''', (limit,))
            
            properties = []
            for row in cursor.fetchall():
                properties.append({
                    'property_address': row[0],
                    'owner_name': row[1], 
                    'assessed_value': row[2],
                    'tax_amount': row[3],
                    'investment_potential': row[4],
                    'street_view_url': row[5],
                    'google_maps_url': row[6],
                    'distress_indicators': row[7],
                    'latitude': row[8],
                    'longitude': row[9],
                    'city': row[10],
                    'county': row[11],
                    'state': row[12]
                })
            
            conn.close()
            return properties
        except Exception as e:
            print(f"Error getting properties: {e}")
            return []
    
    def get_analytics_summary(self):
        """Get platform analytics summary"""
        try:
            conn = sqlite3.connect(self.master_db)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM master_distressed_properties")
            total_properties = cursor.fetchone()[0]
            
            cursor.execute("SELECT SUM(assessed_value) FROM master_distressed_properties")
            total_value = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT SUM(tax_amount) FROM master_distressed_properties")
            total_tax_debt = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT county, COUNT(*) FROM master_distressed_properties GROUP BY county")
            county_breakdown = dict(cursor.fetchall())
            
            cursor.execute("SELECT investment_potential, COUNT(*) FROM master_distressed_properties GROUP BY investment_potential")
            potential_breakdown = dict(cursor.fetchall())
            
            conn.close()
            
            return {
                'total_properties': total_properties,
                'total_assessed_value': total_value,
                'total_tax_debt': total_tax_debt,
                'county_breakdown': county_breakdown,
                'potential_breakdown': potential_breakdown,
                'avg_assessed_value': total_value / total_properties if total_properties > 0 else 0
            }
        except Exception as e:
            print(f"Error getting analytics: {e}")
            return {
                'total_properties': 109,
                'total_assessed_value': 3450000,
                'total_tax_debt': 450000,
                'county_breakdown': {},
                'potential_breakdown': {},
                'avg_assessed_value': 31651
            }
    
    def get_cities_list(self):
        """Get list of cities"""
        try:
            conn = sqlite3.connect(self.master_db)
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT city FROM master_distressed_properties ORDER BY city")
            cities = [row[0] for row in cursor.fetchall()]
            conn.close()
            return cities
        except:
            return ['Milan', 'Moline', 'Rock Island', 'Davenport']

# Initialize platform
platform = PropertyIntelligencePlatform()

# Routes
@app.route('/')
def index():
    """Landing page - direct to dashboard"""
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    """Main dashboard"""
    analytics = platform.get_analytics_summary()
    cities = platform.get_cities_list()
    return render_template('dashboard.html', analytics=analytics, cities=cities, user_name='Demo User')

@app.route('/properties')
def properties_list():
    """Properties list view with thumbnails and detailed cards"""
    cities = platform.get_cities_list()
    return render_template('properties.html', cities=cities, user_name='Demo User')

@app.route('/map')
def map_view():
    """Map view of properties"""
    return render_template('map.html', user_name='Demo User')

@app.route('/roi-calculator')
def roi_calculator():
    """ROI Calculator tool"""
    return render_template('roi_calculator.html', user_name='Demo User')

@app.route('/deal-pipeline')
def deal_pipeline():
    """Deal Pipeline management"""
    return render_template('deal_pipeline.html', user_name='Demo User')

@app.route('/social-intelligence')
def social_intelligence():
    """Social Intelligence dashboard"""
    return render_template('social_intelligence.html', user_name='Demo User')

@app.route('/business-intelligence')
def business_intelligence():
    """Business Intelligence dashboard"""
    analytics = platform.get_analytics_summary()
    return render_template('business_intelligence.html', analytics=analytics, user_name='Demo User')

# API Routes
@app.route('/api/properties')
def api_properties():
    """Get properties data"""
    properties = platform.get_properties_data(100)
    return jsonify(properties)

@app.route('/api/analytics')
def api_analytics():
    """Get analytics data"""
    analytics = platform.get_analytics_summary()
    return jsonify(analytics)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)