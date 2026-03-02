#!/usr/bin/env python3
"""
Reset password for specific user in InvestorIQ
"""

import sqlite3
import hashlib

def reset_user_password():
    """Reset password for Jacob's account"""
    
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # New password hash for IIQadmin21$
    password = 'IIQadmin21$'
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    # Update password
    cursor.execute('''
        UPDATE users 
        SET password_hash = ?
        WHERE email = ?
    ''', (password_hash, 'bizzy.b.33@icloud.com'))
    
    if cursor.rowcount > 0:
        print("✅ Password reset for bizzy.b.33@icloud.com")
    else:
        print("❌ User not found")
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    reset_user_password()