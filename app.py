#!/usr/bin/env python3
"""
InvestorIQ Property Intelligence Platform - PostgreSQL Version
Professional platform with persistent database and user authentication
"""

from flask import Flask, render_template, jsonify, request, redirect, url_for, session, flash
import os
import re
from datetime import datetime
import hashlib
import secrets
import urllib.parse

# Database imports
try:
    import psycopg2
    import psycopg2.extras
    DATABASE_TYPE = 'postgresql'
except ImportError:
    import sqlite3
    DATABASE_TYPE = 'sqlite'
    print("⚠️ PostgreSQL not available, falling back to SQLite")

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))

class PropertyIntelligencePlatform:
    def __init__(self):
        self.init_database_connections()
        self.init_database_schema()
        
    def init_database_connections(self):
        """Initialize database connections"""
        self.master_db = './QUAD_CITIES_MASTER_DATASET.db'  # SQLite for property data (read-only)
        
        # Users database - PostgreSQL or SQLite
        global DATABASE_TYPE
        if DATABASE_TYPE == 'postgresql':
            self.database_url = os.environ.get('DATABASE_URL')
            if not self.database_url:
                print("❌ DATABASE_URL not found, falling back to SQLite")
                self.database_url = './users.db'
                DATABASE_TYPE = 'sqlite'
        else:
            self.database_url = './users.db'
    
    def get_db_connection(self):
        """Get database connection based on type"""
        if DATABASE_TYPE == 'postgresql':
            conn = psycopg2.connect(self.database_url)
            conn.autocommit = False
            return conn
        else:
            return sqlite3.connect(self.database_url)
    
    def init_database_schema(self):
        """Initialize database schema for users"""
        try:
            conn = self.get_db_connection()
            
            if DATABASE_TYPE == 'postgresql':
                cursor = conn.cursor()
                
                # PostgreSQL schema
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        email VARCHAR(255) UNIQUE NOT NULL,
                        password_hash VARCHAR(255) NOT NULL,
                        first_name VARCHAR(100) NOT NULL,
                        last_name VARCHAR(100) NOT NULL,
                        company VARCHAR(255),
                        phone VARCHAR(20),
                        user_type VARCHAR(20) DEFAULT 'investor',
                        verified BOOLEAN DEFAULT FALSE,
                        terms_accepted BOOLEAN DEFAULT FALSE,
                        access_level VARCHAR(20) DEFAULT 'basic',
                        approval_status VARCHAR(20) DEFAULT 'pending',
                        approved_by INTEGER,
                        approved_at TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_login TIMESTAMP
                    )
                ''')
                
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS access_logs (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER REFERENCES users(id),
                        action VARCHAR(100) NOT NULL,
                        resource VARCHAR(255),
                        ip_address VARCHAR(45),
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS approval_requests (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER REFERENCES users(id),
                        request_reason TEXT,
                        business_justification TEXT,
                        admin_notes TEXT,
                        status VARCHAR(20) DEFAULT 'pending',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        reviewed_at TIMESTAMP,
                        reviewed_by INTEGER
                    )
                ''')
                
            else:
                cursor = conn.cursor()
                
                # SQLite schema (fallback)
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
                        access_level TEXT DEFAULT 'basic',
                        approval_status TEXT DEFAULT 'pending',
                        approved_by INTEGER,
                        approved_at TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_login TIMESTAMP
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
                
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS approval_requests (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER REFERENCES users(id),
                        request_reason TEXT,
                        business_justification TEXT,
                        admin_notes TEXT,
                        status TEXT DEFAULT 'pending',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        reviewed_at TIMESTAMP,
                        reviewed_by INTEGER
                    )
                ''')
            
            conn.commit()
            conn.close()
            
            print(f"✅ Database schema initialized ({DATABASE_TYPE})")
            
        except Exception as e:
            print(f"❌ Database initialization error: {e}")
    
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
    
    def create_user(self, email, password, first_name, last_name, company=None, phone=None, business_justification=None):
        """Create new user account with PostgreSQL support"""
        try:
            conn = self.get_db_connection()
            
            if DATABASE_TYPE == 'postgresql':
                cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                
                # Check if user already exists
                cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
                if cursor.fetchone():
                    return False, "Email already registered"
                
                # Check if this is the first user
                cursor.execute("SELECT COUNT(*) FROM users")
                user_count = cursor.fetchone()[0]
                
                password_hash = self.hash_password(password)
                
                if user_count == 0:
                    # First user becomes admin automatically
                    cursor.execute('''
                        INSERT INTO users (email, password_hash, first_name, last_name, company, phone, 
                                         approval_status, access_level, verified, terms_accepted)
                        VALUES (%s, %s, %s, %s, %s, %s, 'approved', 'admin', TRUE, FALSE)
                        RETURNING id
                    ''', (email, password_hash, first_name, last_name, company, phone))
                else:
                    # Regular users require approval
                    cursor.execute('''
                        INSERT INTO users (email, password_hash, first_name, last_name, company, phone, approval_status)
                        VALUES (%s, %s, %s, %s, %s, %s, 'pending')
                        RETURNING id
                    ''', (email, password_hash, first_name, last_name, company, phone))
                
                user_id = cursor.fetchone()[0]
                
                # Create approval request if not admin
                if user_count > 0:
                    cursor.execute('''
                        INSERT INTO approval_requests (user_id, business_justification)
                        VALUES (%s, %s)
                    ''', (user_id, business_justification or 'Professional real estate investment'))
                
            else:
                cursor = conn.cursor()
                
                # SQLite version (same logic, different syntax)
                cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
                if cursor.fetchone():
                    return False, "Email already registered"
                
                cursor.execute("SELECT COUNT(*) FROM users")
                user_count = cursor.fetchone()[0]
                
                password_hash = self.hash_password(password)
                
                if user_count == 0:
                    cursor.execute('''
                        INSERT INTO users (email, password_hash, first_name, last_name, company, phone, 
                                         approval_status, access_level, verified, terms_accepted)
                        VALUES (?, ?, ?, ?, ?, ?, 'approved', 'admin', 1, 0)
                    ''', (email, password_hash, first_name, last_name, company, phone))
                else:
                    cursor.execute('''
                        INSERT INTO users (email, password_hash, first_name, last_name, company, phone, approval_status)
                        VALUES (?, ?, ?, ?, ?, ?, 'pending')
                    ''', (email, password_hash, first_name, last_name, company, phone))
                
                user_id = cursor.lastrowid
                
                if user_count > 0:
                    cursor.execute('''
                        INSERT INTO approval_requests (user_id, business_justification)
                        VALUES (?, ?)
                    ''', (user_id, business_justification or 'Professional real estate investment'))
            
            conn.commit()
            conn.close()
            
            return True, user_id
            
        except Exception as e:
            return False, str(e)
    
    def authenticate_user(self, email, password):
        """Authenticate user login with PostgreSQL support"""
        try:
            conn = self.get_db_connection()
            
            if DATABASE_TYPE == 'postgresql':
                cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                cursor.execute('''
                    SELECT id, password_hash, first_name, last_name, company, access_level, 
                           terms_accepted, approval_status, verified
                    FROM users WHERE email = %s
                ''', (email,))
            else:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, password_hash, first_name, last_name, company, access_level, 
                           terms_accepted, approval_status, verified
                    FROM users WHERE email = ?
                ''', (email,))
            
            user = cursor.fetchone()
            if not user:
                return False, "Invalid email or password"
            
            if DATABASE_TYPE == 'postgresql':
                user_id, password_hash, first_name, last_name, company, access_level, terms_accepted, approval_status, verified = user
            else:
                user_id, password_hash, first_name, last_name, company, access_level, terms_accepted, approval_status, verified = user
            
            if not self.verify_password(password, password_hash):
                return False, "Invalid email or password"
            
            # Check approval status
            if approval_status == 'pending':
                return False, "Account pending admin approval. You will be notified when approved."
            elif approval_status == 'rejected':
                return False, "Account access denied. Contact support for more information."
            elif approval_status != 'approved':
                return False, "Account not properly configured. Contact support."
            
            # Update last login
            if DATABASE_TYPE == 'postgresql':
                cursor.execute('UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = %s', (user_id,))
            else:
                cursor.execute('UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?', (user_id,))
            
            conn.commit()
            conn.close()
            
            user_data = {
                'id': user_id,
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'company': company,
                'access_level': access_level,
                'terms_accepted': terms_accepted,
                'is_admin': access_level == 'admin'
            }
            
            return True, user_data
            
        except Exception as e:
            return False, str(e)
    
    def get_pending_users(self):
        """Get all users pending approval"""
        try:
            conn = self.get_db_connection()
            
            if DATABASE_TYPE == 'postgresql':
                cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                cursor.execute('''
                    SELECT u.id, u.email, u.first_name, u.last_name, u.company, u.phone,
                           u.created_at, ar.business_justification
                    FROM users u
                    LEFT JOIN approval_requests ar ON u.id = ar.user_id
                    WHERE u.approval_status = 'pending'
                    ORDER BY u.created_at DESC
                ''')
            else:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT u.id, u.email, u.first_name, u.last_name, u.company, u.phone,
                           u.created_at, ar.business_justification
                    FROM users u
                    LEFT JOIN approval_requests ar ON u.id = ar.user_id
                    WHERE u.approval_status = 'pending'
                    ORDER BY u.created_at DESC
                ''')
            
            users = []
            for row in cursor.fetchall():
                if DATABASE_TYPE == 'postgresql':
                    users.append({
                        'id': row['id'],
                        'email': row['email'],
                        'first_name': row['first_name'],
                        'last_name': row['last_name'],
                        'company': row['company'],
                        'phone': row['phone'],
                        'created_at': str(row['created_at']),
                        'business_justification': row['business_justification']
                    })
                else:
                    users.append({
                        'id': row[0],
                        'email': row[1],
                        'first_name': row[2],
                        'last_name': row[3],
                        'company': row[4],
                        'phone': row[5],
                        'created_at': row[6],
                        'business_justification': row[7]
                    })
            
            conn.close()
            return users
            
        except Exception as e:
            return []
    
    def approve_user(self, user_id, admin_id, admin_notes=None):
        """Approve a pending user"""
        try:
            conn = self.get_db_connection()
            
            if DATABASE_TYPE == 'postgresql':
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE users 
                    SET approval_status = 'approved', verified = TRUE, approved_by = %s, approved_at = CURRENT_TIMESTAMP
                    WHERE id = %s AND approval_status = 'pending'
                ''', (admin_id, user_id))
                
                cursor.execute('''
                    UPDATE approval_requests
                    SET status = 'approved', reviewed_by = %s, reviewed_at = CURRENT_TIMESTAMP, admin_notes = %s
                    WHERE user_id = %s
                ''', (admin_id, admin_notes, user_id))
            else:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE users 
                    SET approval_status = 'approved', verified = 1, approved_by = ?, approved_at = CURRENT_TIMESTAMP
                    WHERE id = ? AND approval_status = 'pending'
                ''', (admin_id, user_id))
                
                cursor.execute('''
                    UPDATE approval_requests
                    SET status = 'approved', reviewed_by = ?, reviewed_at = CURRENT_TIMESTAMP, admin_notes = ?
                    WHERE user_id = ?
                ''', (admin_id, admin_notes, user_id))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            return False
    
    def reject_user(self, user_id, admin_id, admin_notes=None):
        """Reject a pending user"""
        try:
            conn = self.get_db_connection()
            
            if DATABASE_TYPE == 'postgresql':
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE users 
                    SET approval_status = 'rejected', approved_by = %s, approved_at = CURRENT_TIMESTAMP
                    WHERE id = %s AND approval_status = 'pending'
                ''', (admin_id, user_id))
                
                cursor.execute('''
                    UPDATE approval_requests
                    SET status = 'rejected', reviewed_by = %s, reviewed_at = CURRENT_TIMESTAMP, admin_notes = %s
                    WHERE user_id = %s
                ''', (admin_id, admin_notes, user_id))
            else:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE users 
                    SET approval_status = 'rejected', approved_by = ?, approved_at = CURRENT_TIMESTAMP
                    WHERE id = ? AND approval_status = 'pending'
                ''', (admin_id, user_id))
                
                cursor.execute('''
                    UPDATE approval_requests
                    SET status = 'rejected', reviewed_by = ?, reviewed_at = CURRENT_TIMESTAMP, admin_notes = ?
                    WHERE user_id = ?
                ''', (admin_id, admin_notes, user_id))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            return False
    
    def log_access(self, user_id, action, resource=None, ip_address=None):
        """Log user access for security audit"""
        try:
            conn = self.get_db_connection()
            
            if DATABASE_TYPE == 'postgresql':
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO access_logs (user_id, action, resource, ip_address)
                    VALUES (%s, %s, %s, %s)
                ''', (user_id, action, resource, ip_address))
            else:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO access_logs (user_id, action, resource, ip_address)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, action, resource, ip_address))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            pass  # Don't fail requests due to logging issues

    # Property-related methods (using SQLite for property data)
    def get_all_properties(self, filters=None):
        """Get all properties with optional filters"""
        try:
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
                    'street_view_thumbnail': self.create_property_thumbnail(row[2], row[4], row[0]) if row[2] else None,
                    'google_maps_url': self.fix_street_view_url(row[2]),
                    'apple_maps_url': self.create_apple_maps_url(row[2]) if row[2] else "#",
                    'original_google_maps_url': row[14],
                    'distress_indicators': row[15],
                    'latitude': row[16] if len(row) > 16 else None,
                    'longitude': row[17] if len(row) > 17 else None,
                    'geocoded': row[18] if len(row) > 18 else False
                }
                
                property_data['ratings'] = self.calculate_indicator_ratings(property_data)
                properties.append(property_data)
            
            conn.close()
            return properties
            
        except Exception as e:
            print(f"Error getting properties: {e}")
            return []
    
    def fix_street_view_url(self, address):
        """Create working Google Maps URL"""
        if not address:
            return "#"
        
        clean_address = ' '.join(address.replace('\n', ' ').split())
        encoded_address = urllib.parse.quote(clean_address)
        return f"https://www.google.com/maps/search/{encoded_address}"
    
    def create_apple_maps_url(self, address):
        """Create Apple Maps URL"""
        if not address:
            return "#"
        
        clean_address = ' '.join(address.replace('\n', ' ').split())
        encoded_address = urllib.parse.quote(clean_address)
        return f"https://maps.apple.com/?q={encoded_address}"
    
    def create_property_thumbnail(self, address, city, county):
        """Create property thumbnail placeholder"""
        if not address:
            return self.create_fallback_image("No Address")
        
        address_short = address.split(',')[0] if address else "Property"
        if len(address_short) > 25:
            address_short = address_short[:22] + "..."
        
        encoded_text = urllib.parse.quote(address_short.replace(' ', '+'))
        return f"https://via.placeholder.com/400x300/667eea/ffffff?text=🏠+{encoded_text}"
        
    def create_fallback_image(self, text):
        """Create enhanced placeholder image"""
        encoded_text = urllib.parse.quote(text.replace(' ', '+'))
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
        
        return ratings
    
    def get_analytics_summary(self):
        """Get platform analytics summary"""
        try:
            if not os.path.exists(self.master_db):
                return {}
                
            conn = sqlite3.connect(self.master_db)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM master_distressed_properties")
            total_properties = cursor.fetchone()[0]
            
            cursor.execute("SELECT county, COUNT(*) FROM master_distressed_properties GROUP BY county")
            county_breakdown = dict(cursor.fetchall())
            
            cursor.execute("SELECT investment_potential, COUNT(*) FROM master_distressed_properties GROUP BY investment_potential")
            potential_breakdown = dict(cursor.fetchall())
            
            cursor.execute("SELECT methodology_category, COUNT(*) FROM master_distressed_properties GROUP BY methodology_category")
            methodology_breakdown = dict(cursor.fetchall())
            
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
                'avg_assessed_value': averages[0] or 0,
                'avg_tax_amount': averages[1] or 0,
                'avg_distressed_score': averages[2] or 0,
                'total_tax_debt': averages[3] or 0
            }
            
        except Exception as e:
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

# Initialize platform
platform = PropertyIntelligencePlatform()

# Authentication decorators
def login_required(f):
    """Decorator to require authentication"""
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def admin_required(f):
    """Decorator to require admin privileges"""
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or not session.get('is_admin', False):
            flash('Admin access required', 'error')
            return redirect(url_for('dashboard'))
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

# Routes (same as before, no changes needed)
@app.route('/')
def index():
    """Landing page"""
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
            session['is_admin'] = user_data['is_admin']
            
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
        business_justification = request.form.get('business_justification')
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('register.html')
        
        success, result = platform.create_user(email, password, first_name, last_name, company, phone, business_justification)
        
        if success:
            flash('Registration submitted! Your account is pending admin approval. You will be notified when approved.', 'success')
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
    
    try:
        conn = platform.get_db_connection()
        
        if DATABASE_TYPE == 'postgresql':
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET terms_accepted = TRUE WHERE id = %s', (user_id,))
        else:
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET terms_accepted = 1 WHERE id = ?', (user_id,))
        
        conn.commit()
        conn.close()
    except:
        pass
    
    session['terms_accepted'] = True
    platform.log_access(user_id, 'terms_accepted', ip_address=request.remote_addr)
    
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
@terms_required
def dashboard():
    """Main dashboard"""
    analytics = platform.get_analytics_summary()
    cities = platform.get_cities_list()
    
    platform.log_access(session['user_id'], 'dashboard_view', ip_address=request.remote_addr)
    
    return render_template('dashboard.html', analytics=analytics, cities=cities, user_name=session['user_name'])

@app.route('/admin')
@admin_required
@terms_required
def admin_panel():
    """Admin panel for user approval"""
    pending_users = platform.get_pending_users()
    return render_template('admin_panel.html', pending_users=pending_users, user_name=session['user_name'])

@app.route('/admin/approve/<int:user_id>', methods=['POST'])
@admin_required
def approve_user(user_id):
    """Approve a pending user"""
    admin_notes = request.form.get('admin_notes', '')
    success = platform.approve_user(user_id, session['user_id'], admin_notes)
    
    if success:
        flash('User approved successfully!', 'success')
        platform.log_access(session['user_id'], f'user_approved_{user_id}', ip_address=request.remote_addr)
    else:
        flash('Error approving user', 'error')
    
    return redirect(url_for('admin_panel'))

@app.route('/admin/reject/<int:user_id>', methods=['POST'])
@admin_required
def reject_user(user_id):
    """Reject a pending user"""
    admin_notes = request.form.get('admin_notes', '')
    success = platform.reject_user(user_id, session['user_id'], admin_notes)
    
    if success:
        flash('User rejected', 'warning')
        platform.log_access(session['user_id'], f'user_rejected_{user_id}', ip_address=request.remote_addr)
    else:
        flash('Error rejecting user', 'error')
    
    return redirect(url_for('admin_panel'))

@app.route('/logout')
def logout():
    """User logout"""
    if 'user_id' in session:
        platform.log_access(session['user_id'], 'logout', ip_address=request.remote_addr)
    
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))

# API Routes
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

# Feature routes
@app.route('/properties')
@terms_required
def properties_list():
    """Properties list view with thumbnails and detailed cards"""
    cities = platform.get_cities_list()
    platform.log_access(session['user_id'], 'properties_view', ip_address=request.remote_addr)
    return render_template('properties.html', cities=cities, user_name=session['user_name'])

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
    port = int(os.environ.get('PORT', 5001))
    
    print("🚀 InvestorIQ Property Intelligence Platform (PostgreSQL)")
    print(f"🎯 Starting server on port {port}")
    print(f"💾 Database: {DATABASE_TYPE}")
    print("🔒 Persistent user accounts and data")
    
    app.run(debug=False, host='0.0.0.0', port=port)