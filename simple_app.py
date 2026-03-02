#!/usr/bin/env python3
"""
InvestorIQ Property Intelligence Platform - Simple SQLite Version
Reliable deployment with auto-admin creation
"""

# Copy of main app.py but SQLite only, with auto-admin on startup
import os
import shutil

def setup_simple_deployment():
    """Setup simple SQLite-only deployment"""
    
    # Backup original
    if os.path.exists('app.py'):
        shutil.copy('app.py', 'app_postgres.py.backup')
    
    # Create simple app.py (SQLite only)
    with open('app.py', 'r') as f:
        content = f.read()
    
    # Force SQLite mode
    simple_content = content.replace(
        'DATABASE_TYPE = \'postgresql\'',
        'DATABASE_TYPE = \'sqlite\'  # Force SQLite for reliable deployment'
    )
    
    # Remove PostgreSQL imports that cause issues
    simple_content = simple_content.replace(
        '''try:
    import psycopg2
    import psycopg2.extras
    DATABASE_TYPE = 'postgresql'
except ImportError:
    DATABASE_TYPE = 'sqlite'
    print("⚠️ PostgreSQL not available, falling back to SQLite")''',
        '''# Force SQLite for simple deployment
DATABASE_TYPE = 'sqlite'
print("🎯 Using SQLite for reliable deployment")'''
    )
    
    with open('app.py', 'w') as f:
        f.write(simple_content)
    
    print("✅ Created simple SQLite-only app.py")
    print("🎯 Your admin account will be auto-created on startup")

if __name__ == "__main__":
    setup_simple_deployment()