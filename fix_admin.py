#!/usr/bin/env python3
"""
Quick script to promote a user to admin in InvestorIQ PostgreSQL database
"""

import os
import psycopg2

def promote_to_admin():
    # Get database URL from environment (same as Railway uses)
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found. Run this on Railway or set the environment variable.")
        return
    
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # List all users
        cursor.execute("SELECT email, is_admin, approved FROM users ORDER BY created_at")
        users = cursor.fetchall()
        
        print("📋 Current users:")
        for email, is_admin, approved in users:
            admin_status = "👑 Admin" if is_admin else "👤 User"
            approval_status = "✅ Approved" if approved else "⏳ Pending"
            print(f"  {email} - {admin_status} - {approval_status}")
        
        # Promote specific user to admin
        email_to_promote = input("\n📝 Enter email to promote to admin: ").strip()
        
        cursor.execute("""
            UPDATE users 
            SET is_admin = TRUE, approved = TRUE 
            WHERE email = %s
        """, (email_to_promote,))
        
        if cursor.rowcount > 0:
            conn.commit()
            print(f"✅ {email_to_promote} promoted to admin and approved!")
        else:
            print(f"❌ User {email_to_promote} not found")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    promote_to_admin()