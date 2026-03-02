#!/usr/bin/env python3
"""
InvestorIQ Property Intelligence Platform - Production with Authentication
Professional platform with user authentication and terms of service
"""

from flask import Flask, render_template, jsonify, request, redirect, url_for, session, flash
import sqlite3
import json
import os
import re
from datetime import datetime
import hashlib
import secrets
from advanced_analytics import InvestorIQAnalytics
from deal_pipeline import DealPipelineManager
from property_images import PropertyImageService

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))

class PropertyIntelligencePlatform:
    def __init__(self):
        self.init_database_connections()
        self.init_analytics_engine()
        self.init_deal_pipeline()
        self.init_image_service()
        self.init_users_database()
        
    def init_database_connections(self):
        """Initialize all database connections"""
        self.master_db = './QUAD_CITIES_MASTER_DATASET.db'
        self.social_db = './real_estate_intelligence.db'
        self.users_db = './users.db'
        
    def init_users_database(self):
        """Initialize user authentication database"""
        conn = sqlite3.connect(self.users_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                company TEXT,
                phone TEXT,
                user_type TEXT DEFAULT 'investor',
                verified BOOLEAN DEFAULT 0,
                terms_accepted BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                access_level TEXT DEFAULT 'basic'
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER REFERENCES users(id),
                session_token TEXT UNIQUE NOT NULL,
                ip_address TEXT,
                user_agent TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                active BOOLEAN DEFAULT 1
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS access_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER REFERENCES users(id),
                action TEXT NOT NULL,
                resource TEXT,
                ip_address TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def init_analytics_engine(self):
        """Initialize advanced analytics engine"""
        if os.path.exists('./advanced_analytics.py'):
            self.analytics = InvestorIQAnalytics(self.master_db)
        else:
            self.analytics = None
            
    def init_deal_pipeline(self):
        """Initialize deal pipeline manager"""
        if os.path.exists('./deal_pipeline.py'):
            pipeline_db_path = './deal_pipeline.db'
            self.pipeline = DealPipelineManager(pipeline_db_path)
        else:
            self.pipeline = None
            
    def init_image_service(self):
        """Initialize property image service"""
        if os.path.exists('./property_images.py'):
            self.image_service = PropertyImageService()
        else:
            self.image_service = None
    
    def hash_password(self, password):
        """Hash password with salt"""
        salt = secrets.token_hex(32)
        password_hash = hashlib.pbkdf2_hmac('sha256', 
                                          password.encode('utf-8'), 
                                          salt.encode('utf-8'), 
                                          100000)
        return salt + password_hash.hex()
    
    def verify_password(self, password, password_hash):
        """Verify password against hash"""
        salt = password_hash[:64]
        hash_to_check = password_hash[64:]
        password_hash_check = hashlib.pbkdf2_hmac('sha256',
                                                password.encode('utf-8'),
                                                salt.encode('utf-8'),
                                                100000)
        return password_hash_check.hex() == hash_to_check
    
    def create_user(self, email, password, first_name, last_name, company=None, phone=None):
        """Create new user account"""
        try:
            conn = sqlite3.connect(self.users_db)
            cursor = conn.cursor()
            
            # Check if user already exists
            cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
            if cursor.fetchone():
                return False, "Email already registered"
            
            password_hash = self.hash_password(password)
            
            cursor.execute('''
                INSERT INTO users (email, password_hash, first_name, last_name, company, phone)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (email, password_hash, first_name, last_name, company, phone))
            
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return True, user_id
            
        except Exception as e:
            return False, str(e)
    
    def authenticate_user(self, email, password):
        """Authenticate user login"""
        try:
            conn = sqlite3.connect(self.users_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, password_hash, first_name, last_name, company, access_level, terms_accepted
                FROM users WHERE email = ? AND verified = 1
            ''', (email,))
            
            user = cursor.fetchone()
            if not user:
                return False, "Invalid email or password"
            
            user_id, password_hash, first_name, last_name, company, access_level, terms_accepted = user
            
            if not self.verify_password(password, password_hash):
                return False, "Invalid email or password"
            
            # Update last login
            cursor.execute('''
                UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?
            ''', (user_id,))
            
            conn.commit()
            conn.close()
            
            user_data = {
                'id': user_id,
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'company': company,
                'access_level': access_level,
                'terms_accepted': terms_accepted
            }
            
            return True, user_data
            
        except Exception as e:
            return False, str(e)
    
    def log_access(self, user_id, action, resource=None, ip_address=None):
        """Log user access for security audit"""
        try:
            conn = sqlite3.connect(self.users_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO access_logs (user_id, action, resource, ip_address)
                VALUES (?, ?, ?, ?)
            ''', (user_id, action, resource, ip_address))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            pass  # Don't fail requests due to logging issues

    def get_all_properties(self, filters=None):
        """Get all properties with optional filters"""
        try:
            # Check if database exists
            if not os.path.exists(self.master_db):
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
                    'phone_lookup_url': row[12] if row[12] else "#",
                    'street_view_url': self.fix_street_view_url(row[2]),
                    'google_maps_url': self.fix_street_view_url(row[2]),
                    'apple_maps_url': self.create_apple_maps_url(row[2]) if row[2] else "#",
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
        """Create working Google Maps URL"""
        import urllib.parse
        if not address:
            return "#"
        
        clean_address = ' '.join(address.replace('\n', ' ').split())
        encoded_address = urllib.parse.quote(clean_address)
        return f"https://www.google.com/maps/search/{encoded_address}"
    
    def create_apple_maps_url(self, address):
        """Create Apple Maps URL"""
        import urllib.parse
        if not address:
            return "#"
        
        clean_address = ' '.join(address.replace('\n', ' ').split())
        encoded_address = urllib.parse.quote(clean_address)
        return f"https://maps.apple.com/?q={encoded_address}"
    
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
        
        # Additional rating calculations...
        return ratings
    
    def get_analytics_summary(self):
        """Get platform analytics summary"""
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
            
            # Additional analytics...
            
            conn.close()
            
            return {
                'total_properties': total_properties,
                'county_breakdown': county_breakdown,
                # Add more analytics...
            }
            
        except Exception as e:
            print(f"Error getting analytics: {e}")
            return {}

# Initialize platform
platform = PropertyIntelligencePlatform()

# Authentication decorator
def login_required(f):
    """Decorator to require authentication"""
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def terms_required(f):
    """Decorator to require terms acceptance"""
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        if not session.get('terms_accepted', False):
            return redirect(url_for('terms'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route('/')
def index():
    """Landing page - redirect to login or dashboard"""
    if 'user_id' in session:
        if session.get('terms_accepted', False):
            return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('terms'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        success, result = platform.authenticate_user(email, password)
        
        if success:
            user_data = result
            session['user_id'] = user_data['id']
            session['user_email'] = user_data['email']
            session['user_name'] = f"{user_data['first_name']} {user_data['last_name']}"
            session['access_level'] = user_data['access_level']
            session['terms_accepted'] = user_data['terms_accepted']
            
            platform.log_access(user_data['id'], 'login', ip_address=request.remote_addr)
            
            if user_data['terms_accepted']:
                return redirect(url_for('dashboard'))
            else:
                return redirect(url_for('terms'))
        else:
            flash(result, 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        company = request.form.get('company')
        phone = request.form.get('phone')
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('register.html')
        
        success, result = platform.create_user(email, password, first_name, last_name, company, phone)
        
        if success:
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash(result, 'error')
    
    return render_template('register.html')

@app.route('/terms')
@login_required
def terms():
    """Terms of service acceptance"""
    if session.get('terms_accepted', False):
        return redirect(url_for('dashboard'))
    return render_template('terms.html')

@app.route('/accept-terms', methods=['POST'])
@login_required
def accept_terms():
    """Accept terms of service"""
    user_id = session['user_id']
    
    # Update user record
    conn = sqlite3.connect(platform.users_db)
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET terms_accepted = 1 WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()
    
    session['terms_accepted'] = True
    platform.log_access(user_id, 'terms_accepted', ip_address=request.remote_addr)
    
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
@terms_required
def dashboard():
    """Main dashboard"""
    analytics = platform.get_analytics_summary()
    cities = []  # Add cities list logic
    
    platform.log_access(session['user_id'], 'dashboard_view', ip_address=request.remote_addr)
    
    return render_template('dashboard.html', analytics=analytics, cities=cities, user_name=session['user_name'])

@app.route('/logout')
def logout():
    """User logout"""
    if 'user_id' in session:
        platform.log_access(session['user_id'], 'logout', ip_address=request.remote_addr)
    
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))

# API Routes (all require authentication)
@app.route('/api/properties')
@terms_required
def api_properties():
    """API endpoint for properties with filtering"""
    filters = {k: v for k, v in request.args.items() if v}
    properties = platform.get_all_properties(filters)
    
    platform.log_access(session['user_id'], 'properties_api', ip_address=request.remote_addr)
    
    return jsonify({
        'success': True,
        'properties': properties
    })

@app.route('/api/analytics')
@terms_required
def api_analytics():
    """API endpoint for analytics data"""
    analytics = platform.get_analytics_summary()
    platform.log_access(session['user_id'], 'analytics_api', ip_address=request.remote_addr)
    return jsonify(analytics)

# Additional routes for full features...
@app.route('/map')
@terms_required
def map_view():
    """Map view of properties"""
    return render_template('map.html', user_name=session['user_name'])

@app.route('/roi-calculator')
@terms_required
def roi_calculator():
    """ROI Calculator interface"""
    return render_template('roi_calculator.html', user_name=session['user_name'])

@app.route('/deal-pipeline')
@terms_required
def deal_pipeline():
    """Deal pipeline management interface"""
    return render_template('deal_pipeline.html', user_name=session['user_name'])

@app.route('/social-intelligence')
@terms_required
def social_intelligence():
    """Social intelligence dashboard"""
    return render_template('social_intelligence.html', user_name=session['user_name'])

@app.route('/business-intelligence')
@terms_required
def business_intelligence():
    """Business intelligence dashboard"""
    analytics = platform.get_analytics_summary()
    return render_template('business_intelligence.html', analytics=analytics, user_name=session['user_name'])

if __name__ == '__main__':
    # Get port from environment variable or default to 5001
    port = int(os.environ.get('PORT', 5001))
    
    print("🚀 InvestorIQ Property Intelligence Platform (Production)")
    print(f"🎯 Starting secure server on port {port}")
    
    app.run(debug=False, host='0.0.0.0', port=port)