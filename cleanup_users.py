#!/usr/bin/env python3
"""
Clean slate: Remove all user accounts for fresh start
"""

import os

def cleanup_user_database():
    """Remove user database for clean slate"""
    
    # Remove SQLite user database if it exists
    if os.path.exists('users.db'):
        os.remove('users.db')
        print("✅ Removed existing user database")
    else:
        print("📋 No existing user database found")
    
    print("🧹 Clean slate ready!")
    print("🎯 Next user to register = automatic admin")

if __name__ == "__main__":
    cleanup_user_database()