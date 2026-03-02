#!/usr/bin/env python3
"""
Advanced Analytics Engine for InvestorIQ
ROI calculations, market analysis, and investment modeling
"""

import sqlite3
import json
from datetime import datetime, timedelta
import statistics

class InvestorIQAnalytics:
    def __init__(self, master_db_path):
        self.master_db = master_db_path
        
    def calculate_comprehensive_roi(self, property_data, investment_params):
        """
        Calculate comprehensive ROI with multiple scenarios
        
        investment_params = {
            'purchase_price': 50000,
            'repair_costs': 15000,
            'holding_costs_monthly': 500,
            'expected_rent': 800,
            'target_sale_price': 85000,
            'hold_period_months': 12,
            'financing': {
                'down_payment_percent': 25,
                'interest_rate': 6.5,
                'loan_term_years': 30
            }
        }
        """
        
        # Basic calculations
        total_investment = investment_params['purchase_price'] + investment_params['repair_costs']
        monthly_rent = investment_params.get('expected_rent', 0)
        holding_period = investment_params.get('hold_period_months', 12)
        total_holding_costs = investment_params['holding_costs_monthly'] * holding_period
        
        # Financing calculations if applicable
        financing = investment_params.get('financing', {})
        if financing:
            down_payment = total_investment * (financing.get('down_payment_percent', 0) / 100)
            loan_amount = total_investment - down_payment
            monthly_payment = self.calculate_monthly_payment(
                loan_amount, 
                financing.get('interest_rate', 0), 
                financing.get('loan_term_years', 30)
            )
        else:
            down_payment = total_investment
            loan_amount = 0
            monthly_payment = 0
        
        # Rental income scenario
        total_rental_income = monthly_rent * holding_period
        rental_net_operating_income = total_rental_income - total_holding_costs - (monthly_payment * holding_period)
        
        # Flip scenario
        sale_price = investment_params.get('target_sale_price', total_investment * 1.2)
        sale_costs = sale_price * 0.08  # 8% for closing costs, realtor fees, etc.
        flip_profit = sale_price - sale_costs - total_investment - total_holding_costs
        
        # ROI Calculations
        cash_invested = down_payment + investment_params['repair_costs']
        
        # Rental ROI (annualized)
        if monthly_rent > 0:
            annual_rental_income = monthly_rent * 12
            annual_expenses = investment_params['holding_costs_monthly'] * 12 + (monthly_payment * 12)
            annual_cash_flow = annual_rental_income - annual_expenses
            rental_roi = (annual_cash_flow / cash_invested) * 100 if cash_invested > 0 else 0
        else:
            rental_roi = 0
            annual_cash_flow = 0
        
        # Flip ROI
        flip_roi = (flip_profit / cash_invested) * 100 if cash_invested > 0 else 0
        
        # BRRRR Analysis (Buy, Rehab, Rent, Refinance, Repeat)
        arv = sale_price  # After Repair Value
        refinance_ltv = 0.75  # 75% LTV on refinance
        refinance_amount = arv * refinance_ltv
        cash_recovered = refinance_amount - loan_amount if refinance_amount > loan_amount else 0
        brrrr_score = (cash_recovered / cash_invested) * 100 if cash_invested > 0 else 0
        
        return {
            'investment_summary': {
                'total_investment': total_investment,
                'cash_invested': cash_invested,
                'loan_amount': loan_amount,
                'down_payment': down_payment
            },
            'rental_analysis': {
                'monthly_rent': monthly_rent,
                'annual_cash_flow': annual_cash_flow,
                'rental_roi': round(rental_roi, 2),
                'cash_on_cash_return': round(rental_roi, 2)  # Same for this scenario
            },
            'flip_analysis': {
                'target_sale_price': sale_price,
                'estimated_profit': flip_profit,
                'flip_roi': round(flip_roi, 2),
                'holding_period_months': holding_period
            },
            'brrrr_analysis': {
                'arv': arv,
                'refinance_amount': refinance_amount,
                'cash_recovered': cash_recovered,
                'brrrr_score': round(brrrr_score, 2)
            },
            'risk_factors': self.calculate_risk_factors(property_data, investment_params),
            'recommendations': []  # We'll populate this after the return to avoid recursion
        }
        
        # Calculate recommendations separately to avoid recursion
        result['recommendations'] = self.generate_investment_recommendations_from_data(
            property_data, investment_params, result
        )
        
        return result
    
    def calculate_monthly_payment(self, loan_amount, annual_rate, term_years):
        """Calculate monthly mortgage payment"""
        if annual_rate == 0:
            return loan_amount / (term_years * 12)
        
        monthly_rate = annual_rate / 100 / 12
        num_payments = term_years * 12
        
        payment = loan_amount * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
        return round(payment, 2)
    
    def calculate_risk_factors(self, property_data, investment_params):
        """Assess investment risk factors"""
        risk_score = 0
        risk_factors = []
        
        # Tax distress risk
        tax_amount = property_data.get('tax_amount', 0)
        if tax_amount > 5000:
            risk_score += 2
            risk_factors.append(f"High tax debt: ${tax_amount:,.2f}")
        elif tax_amount > 2000:
            risk_score += 1
            risk_factors.append(f"Moderate tax debt: ${tax_amount:,.2f}")
        
        # Value vs investment risk
        assessed_value = property_data.get('assessed_value', 0)
        total_investment = investment_params['purchase_price'] + investment_params['repair_costs']
        
        if total_investment > assessed_value * 1.5:
            risk_score += 2
            risk_factors.append("Investment exceeds 150% of assessed value")
        elif total_investment > assessed_value * 1.2:
            risk_score += 1
            risk_factors.append("Investment exceeds 120% of assessed value")
        
        # Market tier risk
        market_tier = property_data.get('market_tier', 'Unknown')
        if market_tier == 'C' or market_tier == 'D':
            risk_score += 1
            risk_factors.append(f"Lower market tier: {market_tier}")
        
        # Financing risk
        financing = investment_params.get('financing', {})
        if financing and financing.get('down_payment_percent', 100) < 20:
            risk_score += 1
            risk_factors.append("Low down payment increases leverage risk")
        
        return {
            'overall_risk_score': min(risk_score, 10),  # Cap at 10
            'risk_level': 'Low' if risk_score <= 2 else 'Medium' if risk_score <= 5 else 'High',
            'risk_factors': risk_factors
        }
    
    def generate_investment_recommendations_from_data(self, property_data, investment_params, roi_analysis):
        """Generate AI-powered investment recommendations from pre-calculated data"""
        recommendations = []
        
        # ROI-based recommendations
        rental_roi = roi_analysis['rental_analysis']['rental_roi']
        flip_roi = roi_analysis['flip_analysis']['flip_roi'] 
        brrrr_score = roi_analysis['brrrr_analysis']['brrrr_score']
        
        if rental_roi > 15:
            recommendations.append("🎯 STRONG BUY: Excellent rental ROI above 15%")
        elif rental_roi > 10:
            recommendations.append("👍 BUY: Good rental ROI above 10%")
        elif rental_roi < 5:
            recommendations.append("⚠️ CAUTION: Low rental ROI below 5%")
        
        if flip_roi > 25:
            recommendations.append("💰 FLIP OPPORTUNITY: High flip ROI potential")
        
        if brrrr_score > 80:
            recommendations.append("🔄 BRRRR CANDIDATE: Excellent refinance potential")
        
        # Keep the original method for other uses
        return self.generate_investment_recommendations_simple(property_data, recommendations)
    
    def generate_investment_recommendations_simple(self, property_data, existing_recommendations):
        """Generate property-specific recommendations without ROI recalculation"""
        recommendations = existing_recommendations.copy()
        
        # Property-specific recommendations
        distressed_score = property_data.get('distressed_score', 0)
        if distressed_score > 8:
            recommendations.append("🚨 URGENT: High distress score - act quickly")
        
        tax_amount = property_data.get('tax_amount', 0)
        if tax_amount > 10000:
            recommendations.append("💡 STRATEGY: Negotiate tax debt assumption for discount")
        
        # Market recommendations
        city = property_data.get('city', '')
        if city.lower() in ['moline', 'rock island', 'davenport']:
            recommendations.append("📍 LOCATION: Strong Quad Cities market fundamentals")
        
        return recommendations
    
    def analyze_market_trends(self, county=None, city=None):
        """Analyze market trends for comparative analysis"""
        try:
            conn = sqlite3.connect(self.master_db)
            cursor = conn.cursor()
            
            # Base query
            query = '''
            SELECT city, COUNT(*) as property_count, 
                   AVG(assessed_value) as avg_value,
                   AVG(tax_amount) as avg_tax_debt,
                   AVG(distressed_score) as avg_distress,
                   MIN(assessed_value) as min_value,
                   MAX(assessed_value) as max_value,
                   methodology_category,
                   market_tier
            FROM master_distressed_properties
            '''
            
            conditions = []
            params = []
            
            if county:
                conditions.append("county = ?")
                params.append(county)
            if city:
                conditions.append("city = ?")
                params.append(city)
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " GROUP BY city, methodology_category, market_tier ORDER BY avg_distress DESC"
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            # Process results into market intelligence
            market_data = []
            total_properties = 0
            total_value = 0
            total_tax_debt = 0
            
            for row in results:
                city_data = {
                    'city': row[0],
                    'property_count': row[1],
                    'avg_value': row[2],
                    'avg_tax_debt': row[3],
                    'avg_distress_score': row[4],
                    'value_range': f"${row[5]:,.0f} - ${row[6]:,.0f}",
                    'methodology': row[7],
                    'market_tier': row[8],
                    'opportunity_rating': self.calculate_opportunity_rating(row)
                }
                market_data.append(city_data)
                
                total_properties += row[1]
                total_value += row[2] * row[1]
                total_tax_debt += row[3] * row[1]
            
            # Market summary
            market_summary = {
                'total_properties': total_properties,
                'avg_property_value': total_value / total_properties if total_properties > 0 else 0,
                'total_tax_debt': total_tax_debt,
                'avg_tax_debt_per_property': total_tax_debt / total_properties if total_properties > 0 else 0,
                'market_health': self.assess_market_health(market_data)
            }
            
            conn.close()
            
            return {
                'market_data': market_data,
                'market_summary': market_summary,
                'top_opportunities': sorted(market_data, key=lambda x: x['opportunity_rating'], reverse=True)[:5]
            }
            
        except Exception as e:
            print(f"Error analyzing market trends: {e}")
            return {'error': str(e)}
    
    def calculate_opportunity_rating(self, row):
        """Calculate opportunity rating for a city/market segment"""
        # Higher distress score = more opportunity
        distress_factor = row[4] / 10  # Normalize to 0-1
        
        # More properties = more inventory
        inventory_factor = min(row[1] / 20, 1)  # Cap at 20 properties
        
        # Lower average value = easier entry
        value_factor = max(1 - (row[2] / 200000), 0)  # Normalize around $200k
        
        # Higher tax debt = more motivation
        tax_factor = min(row[3] / 10000, 1)  # Normalize around $10k
        
        opportunity_score = (distress_factor * 0.3 + inventory_factor * 0.2 + 
                           value_factor * 0.3 + tax_factor * 0.2) * 100
        
        return round(opportunity_score, 1)
    
    def assess_market_health(self, market_data):
        """Assess overall market health and investment climate"""
        if not market_data:
            return "Unknown"
        
        avg_distress = statistics.mean([city['avg_distress_score'] for city in market_data])
        avg_opportunity = statistics.mean([city['opportunity_rating'] for city in market_data])
        
        if avg_opportunity > 70:
            return "Excellent - High opportunity environment"
        elif avg_opportunity > 50:
            return "Good - Solid investment opportunities"
        elif avg_opportunity > 30:
            return "Fair - Moderate opportunities available"
        else:
            return "Challenging - Limited opportunities"
    
    def generate_portfolio_recommendations(self, target_investment, risk_tolerance, strategy):
        """
        Generate portfolio recommendations based on investment criteria
        
        target_investment: total dollars to invest
        risk_tolerance: 'conservative', 'moderate', 'aggressive'
        strategy: 'rental', 'flip', 'brrrr', 'mixed'
        """
        
        try:
            conn = sqlite3.connect(self.master_db)
            cursor = conn.cursor()
            
            # Risk-adjusted filtering
            risk_filters = {
                'conservative': "distressed_score <= 6 AND tax_amount <= 5000",
                'moderate': "distressed_score <= 8 AND tax_amount <= 10000", 
                'aggressive': "distressed_score >= 6"  # No upper limit for aggressive
            }
            
            risk_filter = risk_filters.get(risk_tolerance, risk_filters['moderate'])
            
            query = f'''
            SELECT * FROM master_distressed_properties 
            WHERE {risk_filter} AND assessed_value IS NOT NULL
            ORDER BY distressed_score DESC, tax_amount DESC
            LIMIT 50
            '''
            
            cursor.execute(query)
            properties = cursor.fetchall()
            
            # Generate portfolio based on strategy
            portfolio = self.build_optimal_portfolio(properties, target_investment, strategy)
            
            conn.close()
            return portfolio
            
        except Exception as e:
            print(f"Error generating portfolio recommendations: {e}")
            return {'error': str(e)}
    
    def build_optimal_portfolio(self, properties, target_investment, strategy):
        """Build optimal property portfolio within budget"""
        
        # Convert to dictionaries for easier handling
        property_list = []
        for prop in properties:
            # Assume property tuple structure matches database schema
            property_dict = {
                'address': prop[2],
                'assessed_value': prop[5] or 0,
                'tax_amount': prop[6] or 0,
                'distressed_score': prop[8] or 0,
                'city': prop[4],
                'county': prop[0]
            }
            property_list.append(property_dict)
        
        # Strategy-based selection
        if strategy == 'rental':
            # Focus on lower-cost properties for cash flow
            property_list.sort(key=lambda x: x['assessed_value'])
        elif strategy == 'flip':
            # Focus on high distress for maximum upside
            property_list.sort(key=lambda x: x['distressed_score'], reverse=True)
        elif strategy == 'brrrr':
            # Balance of value and distress
            property_list.sort(key=lambda x: x['distressed_score'] / max(x['assessed_value'], 1), reverse=True)
        
        # Build portfolio within budget
        selected_properties = []
        remaining_budget = target_investment
        
        for prop in property_list:
            estimated_purchase = prop['assessed_value'] * 0.8  # 20% discount assumption
            estimated_repairs = prop['assessed_value'] * 0.15  # 15% repair costs
            total_needed = estimated_purchase + estimated_repairs
            
            if total_needed <= remaining_budget and len(selected_properties) < 10:
                selected_properties.append({
                    **prop,
                    'estimated_purchase_price': estimated_purchase,
                    'estimated_repair_costs': estimated_repairs,
                    'total_investment': total_needed
                })
                remaining_budget -= total_needed
        
        return {
            'selected_properties': selected_properties,
            'properties_count': len(selected_properties),
            'total_invested': target_investment - remaining_budget,
            'remaining_budget': remaining_budget,
            'diversification': self.analyze_portfolio_diversification(selected_properties),
            'expected_returns': self.calculate_portfolio_returns(selected_properties, strategy)
        }
    
    def analyze_portfolio_diversification(self, properties):
        """Analyze portfolio diversification across cities and property types"""
        cities = {}
        total_value = 0
        
        for prop in properties:
            city = prop['city']
            value = prop['total_investment']
            
            if city in cities:
                cities[city] += value
            else:
                cities[city] = value
            
            total_value += value
        
        # Calculate diversification metrics
        city_percentages = {city: (value/total_value)*100 for city, value in cities.items()}
        
        return {
            'cities': city_percentages,
            'diversification_score': min(len(cities) * 20, 100),  # Max 100 for 5+ cities
            'largest_city_exposure': max(city_percentages.values()) if city_percentages else 0
        }
    
    def calculate_portfolio_returns(self, properties, strategy):
        """Calculate expected portfolio returns based on strategy"""
        
        strategy_returns = {
            'rental': {'roi': 12, 'timeline': '12+ months'},
            'flip': {'roi': 25, 'timeline': '6-12 months'}, 
            'brrrr': {'roi': 35, 'timeline': '12-18 months'},
            'mixed': {'roi': 20, 'timeline': '6-18 months'}
        }
        
        base_return = strategy_returns.get(strategy, strategy_returns['mixed'])
        
        total_investment = sum(prop['total_investment'] for prop in properties)
        expected_annual_return = total_investment * (base_return['roi'] / 100)
        
        return {
            'strategy': strategy,
            'expected_annual_roi': base_return['roi'],
            'expected_annual_return': expected_annual_return,
            'timeline': base_return['timeline'],
            'total_portfolio_value': total_investment
        }