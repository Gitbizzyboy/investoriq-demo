#!/usr/bin/env python3
"""
Reset database and create admin user for InvestorIQ
"""

import os
import sqlite3
import hashlib

def create_admin_user():
    """Create admin user in fresh database"""
    
    # Remove any existing users database
    if os.path.exists('users.db'):
        os.remove('users.db')
        print("📁 Removed old users.db")
    
    # Create fresh SQLite database
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            is_admin BOOLEAN DEFAULT FALSE,
            approved BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create your admin account
    email = 'bizzy.b.33@icloud.com'
    password = 'IIQadmin21$'
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    cursor.execute('''
        INSERT INTO users (email, password_hash, is_admin, approved)
        VALUES (?, ?, TRUE, TRUE)
    ''', (email, password_hash))
    
    # Create auto-admin fallback
    auto_email = 'admin@investoriq.com' 
    auto_password = 'admin123'
    auto_password_hash = hashlib.sha256(auto_password.encode()).hexdigest()
    
    cursor.execute('''
        INSERT INTO users (email, password_hash, is_admin, approved)
        VALUES (?, ?, TRUE, TRUE)
    ''', (auto_email, auto_password_hash))
    
    conn.commit()
    conn.close()
    
    print("✅ Created fresh database with admin accounts:")
    print(f"   • {email} (your admin account)")
    print(f"   • {auto_email} (auto-admin fallback)")
    
if __name__ == "__main__":
    create_admin_user()