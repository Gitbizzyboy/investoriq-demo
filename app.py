#!/usr/bin/env python3
"""
InvestorIQ - Minimal Demo Version (No Authentication) - v2
"""

from flask import Flask, render_template, jsonify, redirect
import sqlite3
import os

app = Flask(__name__)

@app.route('/')
def index():
    return redirect('/dashboard')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', 
                         analytics={'total_properties': 109, 'total_assessed_value': 3450000},
                         cities=['Milan', 'Rock Island', 'Moline'],
                         user_name='Demo User')

@app.route('/properties')
def properties():
    return render_template('properties.html', 
                         cities=['Milan', 'Rock Island', 'Moline'],
                         user_name='Demo User')

@app.route('/map')
def map_view():
    return render_template('map.html', user_name='Demo User')

@app.route('/api/properties')
def api_properties():
    try:
        conn = sqlite3.connect('QUAD_CITIES_MASTER_DATASET.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT property_address, owner_name, assessed_value, tax_amount,
                   investment_potential, street_view_url, google_maps_url,
                   distress_indicators, latitude, longitude
            FROM master_distressed_properties 
            ORDER BY assessed_value DESC
            LIMIT 50
        ''')
        
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
                'longitude': row[9]
            })
        
        conn.close()
        return jsonify(properties)
        
    except Exception as e:
        return jsonify([])

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)