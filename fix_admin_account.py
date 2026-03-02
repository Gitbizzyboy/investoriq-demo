#!/usr/bin/env python3
"""
Fix existing user account to work with new admin approval system
"""

import sqlite3
import sys

def fix_admin_account():
    """Fix the first user account to be admin"""
    try:
        conn = sqlite3.connect('./users.db')
        cursor = conn.cursor()
        
        # Check if users table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
            print("❌ No users table found - database needs to be recreated")
            return
        
        # Get all users
        cursor.execute("SELECT id, email, first_name, last_name, approval_status, access_level FROM users")
        users = cursor.fetchall()
        
        if not users:
            print("❌ No users found - you may need to register again")
            return
        
        print("📋 Current users in database:")
        for user in users:
            print(f"  ID: {user[0]} | Email: {user[1]} | Name: {user[2]} {user[3]} | Status: {user[4]} | Level: {user[5]}")
        
        # Make the first user an approved admin
        first_user = users[0]
        user_id = first_user[0]
        user_email = first_user[1]
        
        print(f"\n🔧 Fixing account: {user_email}")
        
        cursor.execute('''
            UPDATE users 
            SET approval_status = 'approved', 
                access_level = 'admin', 
                verified = 1,
                terms_accepted = 0
            WHERE id = ?
        ''', (user_id,))
        
        conn.commit()
        conn.close()
        
        print(f"✅ SUCCESS: {user_email} is now an APPROVED ADMIN")
        print("🔑 Your original login credentials should now work")
        print("👑 You have full admin privileges")
        print("📝 You'll need to accept terms again after login")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 If this doesn't work, try registering a new account - it will automatically become admin")

if __name__ == "__main__":
    fix_admin_account()