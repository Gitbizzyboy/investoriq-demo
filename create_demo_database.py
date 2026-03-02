#!/usr/bin/env python3
"""
Create sanitized demo database for public deployment
Realistic but completely anonymized data
"""

import sqlite3
import random
import os

def create_demo_database():
    """Create sanitized demo database with fake but realistic data"""
    
    # Remove existing demo database if it exists
    demo_db = 'DEMO_PROPERTIES.db'
    if os.path.exists(demo_db):
        os.remove(demo_db)
    
    conn = sqlite3.connect(demo_db)
    cursor = conn.cursor()
    
    # Create the same table structure as real database
    cursor.execute('''
        CREATE TABLE master_distressed_properties (
            county TEXT,
            state TEXT,
            property_address TEXT,
            owner_name TEXT,
            city TEXT,
            assessed_value REAL,
            tax_amount REAL,
            distressed_type TEXT,
            distressed_score INTEGER,
            investment_potential TEXT,
            methodology_category TEXT,
            market_tier TEXT,
            phone_lookup_url TEXT,
            street_view_url TEXT,
            google_maps_url TEXT,
            distress_indicators TEXT,
            latitude REAL,
            longitude REAL,
            geocoded INTEGER
        )
    ''')
    
    # Sample anonymized data
    counties = ['Rock Island County IL', 'Scott County IA']
    cities_il = ['Moline', 'Rock Island', 'East Moline', 'Silvis', 'Milan']
    cities_ia = ['Davenport', 'Bettendorf', 'Pleasant Valley', 'Eldridge']
    
    streets = [
        'Main Street', 'Oak Avenue', 'Elm Street', 'Park Road', 'River Drive',
        'Maple Avenue', 'Cedar Street', 'Pine Street', 'First Avenue', 'Second Street',
        'Third Avenue', 'Fourth Street', 'Fifth Avenue', 'Sixth Street', 'Seventh Avenue',
        'Eighth Street', 'Ninth Avenue', 'Tenth Street', 'Lincoln Way', 'Washington Street'
    ]
    
    owner_patterns = [
        'John D.', 'Sarah M.', 'Michael R.', 'Jennifer L.', 'Robert K.',
        'Lisa W.', 'David B.', 'Mary C.', 'James S.', 'Patricia H.',
        'Property Owner #{}', 'Estate of J. {}', '{} Family Trust',
        '{} Properties LLC', 'Midwest Holdings {}', 'River City Investments',
        'Demo Property Owner', 'Sample Estate', 'Example Trust'
    ]
    
    distressed_types = [
        'Tax Delinquent', 'Tax Foreclosure', 'Sheriff Sale', 'Estate Sale',
        'Probate Property', 'Bank Owned', 'Pre-Foreclosure', 'Auction Property'
    ]
    
    investment_potentials = ['High', 'Medium-High', 'Medium', 'Low-Medium', 'Speculative']
    methodology_categories = ['Court Records', 'Tax Records', 'Public Notices', 'Estate Filings']
    market_tiers = ['Premium', 'Standard', 'Value', 'Deep-Value']
    
    distress_indicators = [
        'Out of State Owner', 'LLC Ownership', 'Estate Property', 'Multiple Years Delinquent',
        'High Tax Debt', 'Foreclosure Filing', 'Sheriff Sale Notice', 'Probate Court'
    ]
    
    # Generate 100 realistic demo properties
    properties = []
    
    for i in range(100):
        county = random.choice(counties)
        if 'Rock Island' in county:
            city = random.choice(cities_il)
            state = 'IL'
            # Approximate Rock Island County coordinates
            lat_base = 41.5
            lng_base = -90.5
        else:
            city = random.choice(cities_ia)
            state = 'IA'
            # Approximate Scott County coordinates
            lat_base = 41.6
            lng_base = -90.6
        
        # Generate realistic property address
        street_num = random.randint(100, 9999)
        street = random.choice(streets)
        address = f"{street_num} {street}, {city}, {state}"
        
        # Generate owner name (anonymized)
        if random.random() < 0.3:  # 30% numbered owners
            owner = f"Property Owner #{random.randint(1001, 9999)}"
        elif random.random() < 0.2:  # 20% business entities
            owner = random.choice([
                f"Demo Properties LLC #{random.randint(1, 99)}",
                f"Sample Holdings {random.randint(1, 99)}",
                f"Example Trust #{random.randint(1, 99)}",
                f"Midwest Investments {random.randint(1, 99)}"
            ])
        else:  # 50% individual names (anonymized)
            owner = random.choice(owner_patterns)
            if '{}' in owner:
                owner = owner.format(random.choice(['A', 'B', 'C', 'D', 'E']))
        
        # Generate realistic financial values
        assessed_value = random.randint(25000, 200000)
        
        # Tax amount based on assessed value with some distress factor
        base_tax_rate = 0.02  # 2% base rate
        distress_multiplier = random.uniform(1.5, 8.0)  # Higher for distressed
        tax_amount = assessed_value * base_tax_rate * distress_multiplier
        
        # Generate scores and categorization
        distressed_score = random.randint(25, 400)
        
        property_data = {
            'county': county,
            'state': state,
            'property_address': address,
            'owner_name': owner,
            'city': city,
            'assessed_value': assessed_value,
            'tax_amount': tax_amount,
            'distressed_type': random.choice(distressed_types),
            'distressed_score': distressed_score,
            'investment_potential': random.choice(investment_potentials),
            'methodology_category': random.choice(methodology_categories),
            'market_tier': random.choice(market_tiers),
            'phone_lookup_url': '#',  # Disabled for demo
            'street_view_url': f"https://www.google.com/maps/search/{street_num}+{street.replace(' ', '+')}+{city}+{state}",
            'google_maps_url': f"https://www.google.com/maps/search/{street_num}+{street.replace(' ', '+')}+{city}+{state}",
            'distress_indicators': ', '.join(random.sample(distress_indicators, random.randint(1, 3))),
            'latitude': lat_base + random.uniform(-0.1, 0.1),
            'longitude': lng_base + random.uniform(-0.1, 0.1),
            'geocoded': 1
        }
        
        properties.append(property_data)
    
    # Sort by distressed_score descending for realistic ordering
    properties.sort(key=lambda x: x['distressed_score'], reverse=True)
    
    # Insert into database
    insert_query = '''
        INSERT INTO master_distressed_properties (
            county, state, property_address, owner_name, city, assessed_value,
            tax_amount, distressed_type, distressed_score, investment_potential,
            methodology_category, market_tier, phone_lookup_url, street_view_url,
            google_maps_url, distress_indicators, latitude, longitude, geocoded
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''
    
    for prop in properties:
        cursor.execute(insert_query, (
            prop['county'], prop['state'], prop['property_address'], prop['owner_name'],
            prop['city'], prop['assessed_value'], prop['tax_amount'], prop['distressed_type'],
            prop['distressed_score'], prop['investment_potential'], prop['methodology_category'],
            prop['market_tier'], prop['phone_lookup_url'], prop['street_view_url'],
            prop['google_maps_url'], prop['distress_indicators'], prop['latitude'],
            prop['longitude'], prop['geocoded']
        ))
    
    conn.commit()
    conn.close()
    
    print(f"✅ Demo database created: {demo_db}")
    print(f"📊 Generated {len(properties)} anonymized properties")
    print("🔒 Zero privacy risks - all data is fictional")
    
    # Show summary
    conn = sqlite3.connect(demo_db)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM master_distressed_properties")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT county, COUNT(*) FROM master_distressed_properties GROUP BY county")
    by_county = cursor.fetchall()
    
    cursor.execute("SELECT SUM(tax_amount) FROM master_distressed_properties")
    total_debt = cursor.fetchone()[0]
    
    print("\n📈 Demo Database Summary:")
    print(f"   Total Properties: {total}")
    for county, count in by_county:
        print(f"   {county}: {count} properties")
    print(f"   Total Demo Tax Debt: ${total_debt:,.2f}")
    
    conn.close()
    return demo_db

if __name__ == "__main__":
    create_demo_database()