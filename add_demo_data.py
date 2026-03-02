#!/usr/bin/env python3
"""
Add sample data to the deal pipeline for demo purposes
"""

import sqlite3
import json
from datetime import datetime, timedelta

db_path = "/Users/jacoblister/.openclaw/workspace/business/property-finder/data/deal_pipeline.db"

# Sample deal data based on real properties
sample_deals = [
    {
        "property_address": "3726 11 AVE\nMOLINE, IL 61265",
        "city": "Moline", 
        "county": "Rock Island",
        "state": "Illinois",
        "tax_amount": 45000,
        "assessed_value": 125000,
        "investment_potential": "High Opportunity",
        "stage": "under_contract",
        "notes": "Negotiated 15% below asking. Inspection scheduled for next week. Good bones, needs cosmetic updates.",
        "priority": "high",
        "estimated_value": 180000,
        "renovation_cost": 25000
    },
    {
        "property_address": "1247 W 3rd Street",
        "city": "Davenport",
        "county": "Scott", 
        "state": "Iowa",
        "tax_amount": 32000,
        "assessed_value": 89000,
        "investment_potential": "Medium Opportunity",
        "stage": "prospecting",
        "notes": "Owner motivated - recent inheritance. Property manager says good rental potential in this neighborhood.",
        "priority": "medium",
        "estimated_value": 135000,
        "renovation_cost": 18000
    },
    {
        "property_address": "5114 109TH AVE\nMILAN, IL 61264", 
        "city": "Milan",
        "county": "Rock Island",
        "state": "Illinois", 
        "tax_amount": 28000,
        "assessed_value": 75000,
        "investment_potential": "High Opportunity",
        "stage": "analyzing",
        "notes": "Great location for fix & flip. Comparable sales suggest 150K ARV. Need contractor quotes.",
        "priority": "high",
        "estimated_value": 150000,
        "renovation_cost": 35000
    },
    {
        "property_address": "2847 Cumberland Road",
        "city": "Bettendorf",
        "county": "Scott",
        "state": "Iowa",
        "tax_amount": 21000, 
        "assessed_value": 110000,
        "investment_potential": "Medium Opportunity",
        "stage": "negotiating",
        "notes": "Counter-offered at 85K. Seller wants quick close. Good rental income potential ($1200/month).",
        "priority": "medium", 
        "estimated_value": 140000,
        "renovation_cost": 12000
    },
    {
        "property_address": "827 W 6th Street",
        "city": "Davenport", 
        "county": "Scott",
        "state": "Iowa",
        "tax_amount": 38000,
        "assessed_value": 95000,
        "investment_potential": "High Opportunity", 
        "stage": "closed",
        "notes": "CLOSED! Purchased for 72K. Renovation started this week. Targeting 145K sale price by Q2.",
        "priority": "high",
        "estimated_value": 145000,
        "renovation_cost": 22000
    }
]

def add_demo_deals():
    """Add sample deals to the pipeline database"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if deals already exist 
    cursor.execute("SELECT COUNT(*) FROM deal_pipeline")
    existing_count = cursor.fetchone()[0]
    
    if existing_count > 0:
        print(f"Pipeline already has {existing_count} deals. Skipping demo data.")
        conn.close()
        return
    
    print("Adding demo deals to pipeline...")
    
    for i, deal in enumerate(sample_deals):
        # Create timestamps
        created_date = datetime.now() - timedelta(days=20-i*3)
        updated_date = datetime.now() - timedelta(days=2-i)
        
        # Map our demo stages to actual pipeline stages
        stage_mapping = {
            'under_contract': 'under_contract',
            'prospecting': 'watching', 
            'analyzing': 'analyzing',
            'negotiating': 'offer_submitted',
            'closed': 'closed'
        }
        
        cursor.execute('''
        INSERT INTO deal_pipeline (
            property_id, property_address, city, county, state, stage,
            asking_price, estimated_repairs, investor_notes, is_priority,
            roi_rental, roi_flip, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            f"{deal['city']}-{i+1}",  # property_id
            deal['property_address'], deal['city'], deal['county'], deal['state'],
            stage_mapping[deal['stage']], deal['assessed_value'], deal['renovation_cost'],
            deal['notes'], 1 if deal['priority'] == 'high' else 0,
            8.5, 15.2, created_date, updated_date  # Sample ROI values
        ))
    
    # Add some sample notes and documents for the first deal
    deal_id = 1
    
    # Sample notes
    notes = [
        ("Initial contact made with owner", datetime.now() - timedelta(days=15)),
        ("Property inspection completed", datetime.now() - timedelta(days=10)), 
        ("Submitted offer at $110K", datetime.now() - timedelta(days=7)),
        ("Counter-offer received at $118K", datetime.now() - timedelta(days=5)),
        ("Agreed on $115K with quick close", datetime.now() - timedelta(days=2))
    ]
    
    for note, timestamp in notes:
        cursor.execute('''
        INSERT INTO deal_notes (deal_id, note, created_at)
        VALUES (?, ?, ?)
        ''', (deal_id, note, timestamp))
    
    # Sample documents
    documents = [
        ("Property_Inspection_Report.pdf", "inspection", "Detailed inspection findings and repair estimates"),
        ("Comparable_Sales_Analysis.xlsx", "analysis", "Market analysis and ARV calculations"),
        ("Purchase_Agreement_Draft.pdf", "contract", "Initial purchase agreement terms")
    ]
    
    for filename, doc_type, description in documents:
        cursor.execute('''
        INSERT INTO deal_documents (deal_id, filename, file_type, description, uploaded_at)
        VALUES (?, ?, ?, ?, ?)
        ''', (deal_id, filename, doc_type, description, datetime.now() - timedelta(days=5)))
    
    conn.commit()
    conn.close()
    
    print(f"✅ Added {len(sample_deals)} demo deals to pipeline!")
    print("Demo data includes:")
    for deal in sample_deals:
        print(f"  - {deal['property_address'].split('\\n')[0]} ({deal['stage']})")

if __name__ == "__main__":
    add_demo_deals()