#!/usr/bin/env python3
"""
Fix database with complete schema for InvestorIQ
"""

import os
import sqlite3
import hashlib

def fix_complete_database():
    """Create complete database with proper schema"""
    
    # Remove any existing users database
    if os.path.exists('users.db'):
        os.remove('users.db')
        print("📁 Removed old users.db")
    
    # Create fresh SQLite database with complete schema
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Complete users table schema (matches what app expects)
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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Approval requests table  
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS approval_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            business_justification TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Access logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS access_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT,
            ip_address TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create your admin account with complete data
    email = 'bizzy.b.33@icloud.com'
    password = 'IIQadmin21$'
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    cursor.execute('''
        INSERT INTO users (email, password_hash, first_name, last_name, company, phone,
                         approval_status, access_level, verified, terms_accepted)
        VALUES (?, ?, ?, ?, ?, ?, 'approved', 'admin', 1, 1)
    ''', (email, password_hash, 'Jacob', 'Lister', 'InvestorIQ Demo', '', ))
    
    # Create auto-admin fallback
    auto_email = 'admin@investoriq.com' 
    auto_password = 'admin123'
    auto_password_hash = hashlib.sha256(auto_password.encode()).hexdigest()
    
    cursor.execute('''
        INSERT INTO users (email, password_hash, first_name, last_name, company, phone,
                         approval_status, access_level, verified, terms_accepted)
        VALUES (?, ?, ?, ?, ?, ?, 'approved', 'admin', 1, 1)
    ''', (auto_email, auto_password_hash, 'System', 'Admin', 'InvestorIQ', ''))
    
    conn.commit()
    conn.close()
    
    print("✅ Created complete database with full schema:")
    print(f"   • {email} (Jacob Lister - Admin)")
    print(f"   • {auto_email} (System Admin)")
    print("   • All tables: users, approval_requests, access_logs")
    print("   • Terms accepted, verified, approved ✅")
    
if __name__ == "__main__":
    fix_complete_database()