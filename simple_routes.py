#!/usr/bin/env python3
"""
Simple routes without authentication for demo
"""

def fix_routes():
    """Remove all authentication and session dependencies"""
    
    with open('app.py', 'r') as f:
        content = f.read()
    
    # Remove login and registration routes
    lines = content.split('\n')
    new_lines = []
    skip_until_next_route = False
    
    for line in lines:
        # Skip login/register/terms/logout route blocks
        if any(x in line for x in ["@app.route('/login'", "@app.route('/register'", "@app.route('/terms'", "@app.route('/logout'"]):
            skip_until_next_route = True
            continue
            
        # Stop skipping when we hit the next @app.route
        if skip_until_next_route and line.strip().startswith('@app.route'):
            skip_until_next_route = False
        
        # Skip content in login/register blocks
        if skip_until_next_route:
            continue
            
        # Skip session assignments and other auth code
        if any(x in line for x in ["session['", "if 'user_id' in session", "flash(", "redirect(url_for('login')", "redirect(url_for('terms')"]):
            continue
            
        new_lines.append(line)
    
    # Write clean content
    with open('app.py', 'w') as f:
        f.write('\n'.join(new_lines))
    
    print("✅ Removed authentication routes and session dependencies")

if __name__ == "__main__":
    fix_routes()