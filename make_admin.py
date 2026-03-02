#!/usr/bin/env python3
"""
Make existing user an admin - run this once to upgrade your account
"""

import sqlite3
import sys

def make_user_admin():
    """Make the first registered user an admin"""
    try:
        conn = sqlite3.connect('./users.db')
        cursor = conn.cursor()
        
        # Get all users
        cursor.execute("SELECT id, email, first_name, last_name FROM users ORDER BY id")
        users = cursor.fetchall()
        
        if not users:
            print("No users found in database")
            return
        
        print("Current users:")
        for user in users:
            print(f"  ID: {user[0]} | Email: {user[1]} | Name: {user[2]} {user[3]}")
        
        # Make first user admin (that's you!)
        first_user_id = users[0][0]
        first_user_email = users[0][1]
        
        cursor.execute('''
            UPDATE users 
            SET access_level = 'admin', verified = 1, terms_accepted = 1
            WHERE id = ?
        ''', (first_user_id,))
        
        conn.commit()
        conn.close()
        
        print(f"\n✅ SUCCESS: {first_user_email} is now an ADMIN")
        print("🔑 Your login credentials remain exactly the same")
        print("👑 You now have admin privileges to approve new users")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    make_user_admin()