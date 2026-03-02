#!/bin/bash

echo "🚀 InvestorIQ Railway Deployment Setup"
echo "======================================"
echo ""

# Check if we're in the right directory
if [ ! -f "app_production.py" ]; then
    echo "❌ Error: Please run this script from the platform directory"
    echo "   cd /Users/jacoblister/.openclaw/workspace/business/property-finder/platform/"
    exit 1
fi

echo "📋 Files ready for deployment:"
echo "   ✅ app_production.py (Flask app)"
echo "   ✅ requirements.txt (Dependencies)"
echo "   ✅ Procfile (Start command)"
echo "   ✅ railway.json (Railway config)"
echo "   ✅ Database files (109 properties)"
echo "   ✅ Templates and static files"
echo ""

echo "🔧 Next Steps:"
echo "1. Create GitHub repository at: https://github.com/new"
echo "   - Repository name: investoriq-platform"
echo "   - Make it Public"
echo "   - Don't initialize with README (we have files already)"
echo ""

echo "2. Run these commands in this directory:"
echo "   git init"
echo "   git add ."
echo "   git commit -m \"InvestorIQ Platform - Railway Deployment\""
echo "   git branch -M main"
echo "   git remote add origin https://github.com/YOUR_USERNAME/investoriq-platform.git"
echo "   git push -u origin main"
echo ""

echo "3. Deploy to Railway:"
echo "   - Go to: https://railway.app/"
echo "   - Sign up with GitHub (free)"
echo "   - New Project → Deploy from GitHub repo"
echo "   - Select your investoriq-platform repository"
echo "   - Railway will auto-deploy!"
echo ""

echo "4. You'll get a public URL like:"
echo "   https://investoriq-platform-production-xyz.up.railway.app"
echo ""

echo "💡 Alternative: I can help you with Codespaces or other platforms if Railway doesn't work."
echo ""

read -p "Ready to start? Press Enter to continue..."

echo ""
echo "🎯 Current directory contents:"
ls -la

echo ""
echo "🚀 You're all set! Follow the steps above to deploy."