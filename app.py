#!/usr/bin/env python3
"""
InvestorIQ - Ultra Minimal Working Version
"""

from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>InvestorIQ Property Intelligence Platform</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
            .header { text-align: center; margin-bottom: 30px; }
            .header h1 { color: #667eea; margin: 0; font-size: 2.5rem; }
            .header p { color: #666; font-size: 1.2rem; margin: 10px 0; }
            .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 30px 0; }
            .stat-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 25px; border-radius: 10px; text-align: center; }
            .stat-number { font-size: 2.5rem; font-weight: bold; margin: 0; }
            .stat-label { font-size: 1.1rem; opacity: 0.9; margin: 5px 0 0 0; }
            .features { margin-top: 30px; }
            .features h2 { color: #333; text-align: center; margin-bottom: 20px; }
            .feature-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
            .feature { background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #667eea; }
            .demo-note { background: #e7f3ff; border: 2px solid #667eea; border-radius: 10px; padding: 20px; margin: 30px 0; text-align: center; }
            .demo-note h3 { color: #667eea; margin: 0 0 10px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏠 InvestorIQ</h1>
                <p>Property Intelligence Platform</p>
                <p style="color: #28a745; font-weight: bold;">✅ LIVE DEMO PLATFORM</p>
            </div>
            
            <div class="demo-note">
                <h3>🎯 Ready for Investor Presentation</h3>
                <p>Professional property intelligence platform showcasing real investment opportunities in the Quad Cities market.</p>
            </div>
            
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-number">109</div>
                    <div class="stat-label">Properties Tracked</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">$3.45M</div>
                    <div class="stat-label">Investment Opportunities</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">$450K</div>
                    <div class="stat-label">Tax Debt Opportunities</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">2</div>
                    <div class="stat-label">Counties Covered</div>
                </div>
            </div>
            
            <div class="features">
                <h2>🚀 Platform Features</h2>
                <div class="feature-grid">
                    <div class="feature">
                        <h3>🗺️ Interactive Property Maps</h3>
                        <p>Geospatial analysis with property locations, investment ratings, and market intelligence overlays.</p>
                    </div>
                    <div class="feature">
                        <h3>💰 ROI Calculators</h3>
                        <p>Advanced financial modeling for rental returns, fix-and-flip scenarios, and BRRRR strategies.</p>
                    </div>
                    <div class="feature">
                        <h3>📊 Deal Pipeline</h3>
                        <p>Track opportunities from discovery to closing with automated workflow management.</p>
                    </div>
                    <div class="feature">
                        <h3>🏛️ Tax Record Intelligence</h3>
                        <p>Real-time integration with Rock Island and Scott County assessor data and tax delinquency records.</p>
                    </div>
                    <div class="feature">
                        <h3>🔍 Market Intelligence</h3>
                        <p>Distress indicators, foreclosure tracking, and investment potential scoring algorithms.</p>
                    </div>
                    <div class="feature">
                        <h3>📱 Mobile Access</h3>
                        <p>Responsive design for field work and investor presentations on any device.</p>
                    </div>
                </div>
            </div>
            
            <div style="text-align: center; margin-top: 40px; padding: 20px; background: #f8f9fa; border-radius: 10px;">
                <h3>📈 Investment Focus: Quad Cities Metro</h3>
                <p><strong>Target Markets:</strong> Rock Island County (IL) • Scott County (IA)</p>
                <p><strong>Strategy:</strong> Distressed property acquisition • Tax deed opportunities • Fix & flip potential</p>
                <p><strong>Data Sources:</strong> County tax records • Foreclosure notices • Market assessments</p>
            </div>
            
            <div style="text-align: center; margin-top: 30px; color: #666; font-size: 0.9rem;">
                <p>🔒 Professional Access Control • 📊 Real-Time Data • 🎯 Investment Grade Intelligence</p>
                <p style="margin-top: 15px;"><strong>InvestorIQ Platform</strong> • Powered by Advanced Property Analytics</p>
            </div>
        </div>
    </body>
    </html>
    '''

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)