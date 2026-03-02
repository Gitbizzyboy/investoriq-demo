# Railway Deployment Guide - InvestorIQ

## 🚀 Quick Deploy to Railway

### Step 1: Prepare for Deployment
✅ All files are ready in `/business/property-finder/platform/`

### Step 2: Railway Setup

1. **Go to Railway**: https://railway.app/
2. **Sign up with GitHub** (free tier includes 500 hours/month)
3. **Click "New Project"**
4. **Choose "Deploy from GitHub repo"**

### Step 3: Upload Files to GitHub

You need to push the platform folder to GitHub first:

```bash
# Navigate to the platform directory
cd /Users/jacoblister/.openclaw/workspace/business/property-finder/platform/

# Initialize git repository
git init

# Add all files
git add .

# Commit
git commit -m "InvestorIQ Platform - Railway Deployment"

# Create GitHub repository (you'll need to do this manually on GitHub.com)
# Then add remote and push:
git remote add origin https://github.com/YOUR_USERNAME/investoriq-platform.git
git push -u origin main
```

### Step 4: Connect to Railway

1. **In Railway, select your GitHub repo**
2. **Railway will auto-detect Python and use:**
   - `requirements.txt` for dependencies
   - `railway.json` for configuration
   - `Procfile` for start command

3. **Environment Variables (if needed):**
   - No API keys required for this deployment
   - Uses local SQLite databases

### Step 5: Deploy!

Railway will automatically:
- Install dependencies from `requirements.txt`
- Run the production app with `gunicorn`
- Provide a public URL like: `https://investoriq-platform-production-xyz.up.railway.app`

## ✅ What's Included

### Files Ready for Deployment:
- ✅ `app_production.py` - Production Flask app with relative paths
- ✅ `requirements.txt` - Python dependencies
- ✅ `Procfile` - Railway start command
- ✅ `railway.json` - Railway configuration
- ✅ `QUAD_CITIES_MASTER_DATASET.db` - Property database (109 properties)
- ✅ `real_estate_intelligence.db` - Social intelligence database
- ✅ `templates/` - All HTML templates
- ✅ `static/` - CSS, JS, images

### Production Features:
- ✅ Uses relative database paths (works in cloud)
- ✅ Simplified codebase (removed local dependencies)
- ✅ Gunicorn WSGI server for production
- ✅ Environment variable support for PORT
- ✅ Error handling for missing databases

## 🎯 Result

After deployment, you'll get a permanent public URL like:
`https://investoriq-platform-production-xyz.up.railway.app`

This URL will work 24/7 and be accessible from anywhere in the world!

## 📱 Mobile Access

The platform is fully responsive and works perfectly on mobile devices:
- Touch-friendly interface
- Mobile-optimized maps
- Responsive tables and charts
- Fast loading on mobile networks

## 💰 Railway Pricing

**Starter Plan (Free):**
- 500 hours/month runtime
- $5/month only if you exceed free hours
- Perfect for development and demos

**Pro Plan ($20/month):**
- Unlimited hours
- Custom domains
- Priority support
- Recommended for production

## 🔧 After Deployment

1. **Test the platform** on your new Railway URL
2. **Send the URL to your mom** - it will work from anywhere!
3. **Update any local links** to point to the Railway URL
4. **Consider custom domain** for professional branding

## 🚨 Alternative: GitHub Codespaces

If Railway doesn't work, we can deploy to:
- GitHub Codespaces (free)
- Heroku (free tier)
- Vercel (free tier)
- Replit (free tier)

Ready to deploy! 🚀