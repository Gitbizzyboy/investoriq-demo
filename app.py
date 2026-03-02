#!/usr/bin/env python3
"""
InvestorIQ Property Intelligence Platform - Demo Version
Full functionality without authentication barriers
"""

from flask import Flask, render_template, jsonify, request, redirect, url_for
import os
import sqlite3
from datetime import datetime
import hashlib
import secrets
import urllib.parse

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))

class PropertyIntelligencePlatform:
    def __init__(self):
        self.init_database_connections()
        
    def init_database_connections(self):
        """Initialize database connections"""
        self.master_db = './QUAD_CITIES_MASTER_DATASET.db'  # SQLite for property data (read-only)
    
    def get_properties_data(self, limit=100, filters=None):
        """Get properties with optional filtering"""
        try:
            if not os.path.exists(self.master_db):
                return []
                
            conn = sqlite3.connect(self.master_db)
            cursor = conn.cursor()
            
            query = '''
                SELECT id, property_address, owner_name, city, county, state, 
                       assessed_value, tax_amount, property_type, distressed_type,
                       investment_potential, street_view_url, google_maps_url,
                       phone_lookup_url, latitude, longitude, distress_indicators
                FROM master_distressed_properties 
                WHERE 1=1
            '''
            params = []
            
            if filters:
                if filters.get('city'):
                    query += ' AND city = ?'
                    params.append(filters['city'])
                if filters.get('county'):
                    query += ' AND county = ?'
                    params.append(filters['county'])
                if filters.get('investment_potential'):
                    query += ' AND investment_potential = ?'
                    params.append(filters['investment_potential'])
                if filters.get('min_value'):
                    query += ' AND assessed_value >= ?'
                    params.append(filters['min_value'])
                if filters.get('max_value'):
                    query += ' AND assessed_value <= ?'
                    params.append(filters['max_value'])
            
            query += ' ORDER BY assessed_value DESC LIMIT ?'
            params.append(limit)
            
            cursor.execute(query, params)
            
            properties = []
            for row in cursor.fetchall():
                properties.append({
                    'id': row[0],
                    'property_address': row[1],
                    'owner_name': row[2],
                    'city': row[3],
                    'county': row[4],
                    'state': row[5],
                    'assessed_value': row[6],
                    'tax_amount': row[7],
                    'property_type': row[8],
                    'distressed_type': row[9],
                    'investment_potential': row[10],
                    'street_view_url': row[11],
                    'google_maps_url': row[12],
                    'phone_lookup_url': row[13],
                    'latitude': row[14],
                    'longitude': row[15],
                    'distress_indicators': row[16]
                })
            
            conn.close()
            return properties
            
        except Exception as e:
            print(f"Error getting properties: {e}")
            return []
    
    def get_analytics_summary(self):
        """Get platform analytics summary"""
        try:
            if not os.path.exists(self.master_db):
                return {}
                
            conn = sqlite3.connect(self.master_db)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM master_distressed_properties")
            total_properties = cursor.fetchone()[0]
            
            cursor.execute("SELECT SUM(assessed_value) FROM master_distressed_properties")
            total_assessed_value = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT SUM(tax_amount) FROM master_distressed_properties")
            total_tax_debt = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT county, COUNT(*) FROM master_distressed_properties GROUP BY county")
            county_breakdown = dict(cursor.fetchall())
            
            cursor.execute("SELECT investment_potential, COUNT(*) FROM master_distressed_properties GROUP BY investment_potential")
            potential_breakdown = dict(cursor.fetchall())
            
            cursor.execute("SELECT distressed_type, COUNT(*) FROM master_distressed_properties GROUP BY distressed_type")
            methodology_breakdown = dict(cursor.fetchall())
            
            conn.close()
            
            return {
                'total_properties': total_properties,
                'total_assessed_value': total_assessed_value,
                'total_tax_debt': total_tax_debt,
                'county_breakdown': county_breakdown,
                'potential_breakdown': potential_breakdown,
                'methodology_breakdown': methodology_breakdown,
                'avg_assessed_value': total_assessed_value / total_properties if total_properties > 0 else 0
            }
        except Exception as e:
            print(f"Error getting analytics: {e}")
            return {}
    
    def get_cities_list(self):
        """Get list of available cities"""
        try:
            if not os.path.exists(self.master_db):
                return []
                
            conn = sqlite3.connect(self.master_db)
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT city FROM master_distressed_properties WHERE city IS NOT NULL ORDER BY city")
            cities = [row[0] for row in cursor.fetchall()]
            conn.close()
            return cities
        except Exception as e:
            print(f"Error getting cities: {e}")
            return ['Milan', 'Moline', 'Rock Island', 'Davenport']

# Initialize platform
platform = PropertyIntelligencePlatform()

# Main Routes
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
    """API endpoint for properties data"""
    limit = request.args.get('limit', 100, type=int)
    city = request.args.get('city')
    county = request.args.get('county')
    investment_potential = request.args.get('investment_potential')
    min_value = request.args.get('min_value', type=int)
    max_value = request.args.get('max_value', type=int)
    
    filters = {}
    if city: filters['city'] = city
    if county: filters['county'] = county
    if investment_potential: filters['investment_potential'] = investment_potential
    if min_value: filters['min_value'] = min_value
    if max_value: filters['max_value'] = max_value
    
    properties = platform.get_properties_data(limit=limit, filters=filters)
    return jsonify(properties)

@app.route('/api/analytics')
def api_analytics():
    """API endpoint for analytics data"""
    analytics = platform.get_analytics_summary()
    return jsonify(analytics)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)