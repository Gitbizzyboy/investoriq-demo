#!/usr/bin/env python3
"""
Deal Pipeline Manager for InvestorIQ
Tracks properties through investment stages with documentation and team collaboration
"""

import sqlite3
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import shutil

class DealPipelineManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()
        
    def init_database(self):
        """Initialize the pipeline database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if tables already exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='deal_pipeline'")
        if cursor.fetchone():
            # Tables already exist, skip initialization
            conn.close()
            return
            
        # Read and execute the schema file
        schema_path = os.path.join(os.path.dirname(__file__), 'deal_pipeline_schema.sql')
        if os.path.exists(schema_path):
            with open(schema_path, 'r') as f:
                schema_sql = f.read()
            
            cursor.executescript(schema_sql)
            conn.commit()
            conn.close()
    
    def create_deal(self, property_data: Dict, user: str = "system") -> int:
        """Create a new deal in the pipeline"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO deal_pipeline (
                    property_id, property_address, city, county, state,
                    stage, asking_price, created_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                property_data.get('property_id', ''),
                property_data['property_address'],
                property_data.get('city', ''),
                property_data.get('county', ''),
                property_data.get('state', 'IL'),
                'watching',
                property_data.get('assessed_value', 0),
                user
            ))
            
            deal_id = cursor.lastrowid
            
            # Create initial stage history entry
            cursor.execute("""
                INSERT INTO deal_stage_history (deal_id, new_stage, changed_by)
                VALUES (?, ?, ?)
            """, (deal_id, 'watching', user))
            
            conn.commit()
            return deal_id
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def update_stage(self, deal_id: int, new_stage: str, user: str = "system", reason: str = None) -> bool:
        """Move a deal to a new stage in the pipeline"""
        valid_stages = ['watching', 'analyzing', 'offer_submitted', 'under_contract', 'closed', 'passed']
        
        if new_stage not in valid_stages:
            raise ValueError(f"Invalid stage: {new_stage}")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get current stage
            cursor.execute("SELECT stage FROM deal_pipeline WHERE id = ?", (deal_id,))
            result = cursor.fetchone()
            if not result:
                return False
            
            current_stage = result[0]
            
            # Update the deal stage
            cursor.execute("""
                UPDATE deal_pipeline 
                SET stage = ?, stage_updated_at = ?, updated_at = ?
                WHERE id = ?
            """, (new_stage, datetime.now(), datetime.now(), deal_id))
            
            # Record stage history
            cursor.execute("""
                INSERT INTO deal_stage_history 
                (deal_id, previous_stage, new_stage, changed_by, reason)
                VALUES (?, ?, ?, ?, ?)
            """, (deal_id, current_stage, new_stage, user, reason))
            
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def add_note(self, deal_id: int, note_content: str, note_type: str = "general", 
                 user: str = "system", is_private: bool = False) -> int:
        """Add a note to a deal"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO deal_notes 
                (deal_id, note_type, note_content, created_by, is_private)
                VALUES (?, ?, ?, ?, ?)
            """, (deal_id, note_type, note_content, user, is_private))
            
            note_id = cursor.lastrowid
            conn.commit()
            return note_id
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def add_document(self, deal_id: int, file_path: str, document_name: str,
                    document_type: str = "general", user: str = "system") -> int:
        """Add a document to a deal"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get file size
            file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
            
            cursor.execute("""
                INSERT INTO deal_documents 
                (deal_id, document_name, document_type, file_path, file_size, uploaded_by)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (deal_id, document_name, document_type, file_path, file_size, user))
            
            doc_id = cursor.lastrowid
            conn.commit()
            return doc_id
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def update_financials(self, deal_id: int, financial_data: Dict) -> bool:
        """Update financial information for a deal"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Build dynamic update query based on provided fields
            fields = []
            values = []
            
            financial_fields = [
                'offer_price', 'accepted_price', 'estimated_repairs',
                'actual_purchase_price', 'roi_rental', 'roi_flip', 
                'roi_brrrr', 'risk_score'
            ]
            
            for field in financial_fields:
                if field in financial_data:
                    fields.append(f"{field} = ?")
                    values.append(financial_data[field])
            
            if not fields:
                return False
            
            # Add updated_at
            fields.append("updated_at = ?")
            values.append(datetime.now())
            values.append(deal_id)
            
            query = f"UPDATE deal_pipeline SET {', '.join(fields)} WHERE id = ?"
            cursor.execute(query, values)
            
            conn.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def get_pipeline_summary(self) -> List[Dict]:
        """Get summary of deals by stage"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                stage,
                COUNT(*) as deal_count,
                SUM(CASE WHEN is_priority = 1 THEN 1 ELSE 0 END) as priority_count,
                ROUND(AVG(offer_price), 2) as avg_offer_price,
                ROUND(SUM(COALESCE(offer_price, asking_price, 0)), 2) as total_pipeline_value
            FROM deal_pipeline
            WHERE is_archived = 0
            GROUP BY stage
            ORDER BY 
                CASE stage
                    WHEN 'watching' THEN 1
                    WHEN 'analyzing' THEN 2
                    WHEN 'offer_submitted' THEN 3
                    WHEN 'under_contract' THEN 4
                    WHEN 'closed' THEN 5
                    WHEN 'passed' THEN 6
                END
        """)
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def get_deals_by_stage(self, stage: str = None, include_archived: bool = False) -> List[Dict]:
        """Get all deals, optionally filtered by stage"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = """
            SELECT 
                dp.*,
                COUNT(DISTINCT dn.id) as note_count,
                COUNT(DISTINCT dd.id) as document_count,
                MAX(dn.created_at) as last_activity
            FROM deal_pipeline dp
            LEFT JOIN deal_notes dn ON dp.id = dn.deal_id
            LEFT JOIN deal_documents dd ON dp.id = dd.deal_id
            WHERE 1=1
        """
        
        params = []
        
        if not include_archived:
            query += " AND dp.is_archived = 0"
        
        if stage:
            query += " AND dp.stage = ?"
            params.append(stage)
        
        query += " GROUP BY dp.id ORDER BY dp.updated_at DESC"
        
        cursor.execute(query, params)
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def get_deal_details(self, deal_id: int) -> Dict:
        """Get complete details for a specific deal"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get main deal info
        cursor.execute("SELECT * FROM deal_pipeline WHERE id = ?", (deal_id,))
        deal = cursor.fetchone()
        if not deal:
            return None
        
        deal_data = dict(deal)
        
        # Get notes
        cursor.execute("""
            SELECT * FROM deal_notes 
            WHERE deal_id = ? 
            ORDER BY created_at DESC
        """, (deal_id,))
        deal_data['notes'] = [dict(row) for row in cursor.fetchall()]
        
        # Get documents
        cursor.execute("""
            SELECT * FROM deal_documents 
            WHERE deal_id = ? 
            ORDER BY uploaded_at DESC
        """, (deal_id,))
        deal_data['documents'] = [dict(row) for row in cursor.fetchall()]
        
        # Get stage history
        cursor.execute("""
            SELECT * FROM deal_stage_history 
            WHERE deal_id = ? 
            ORDER BY changed_at DESC
        """, (deal_id,))
        deal_data['stage_history'] = [dict(row) for row in cursor.fetchall()]
        
        # Get team members
        cursor.execute("""
            SELECT * FROM deal_team 
            WHERE deal_id = ? 
            ORDER BY added_at DESC
        """, (deal_id,))
        deal_data['team'] = [dict(row) for row in cursor.fetchall()]
        
        # Get tasks
        cursor.execute("""
            SELECT * FROM deal_tasks 
            WHERE deal_id = ? 
            ORDER BY due_date ASC, created_at DESC
        """, (deal_id,))
        deal_data['tasks'] = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return deal_data
    
    def search_deals(self, search_term: str) -> List[Dict]:
        """Search deals by address, city, or notes"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        search_pattern = f"%{search_term}%"
        
        cursor.execute("""
            SELECT DISTINCT dp.*
            FROM deal_pipeline dp
            LEFT JOIN deal_notes dn ON dp.id = dn.deal_id
            WHERE 
                dp.property_address LIKE ? OR
                dp.city LIKE ? OR
                dp.investor_notes LIKE ? OR
                dn.note_content LIKE ?
            ORDER BY dp.updated_at DESC
        """, (search_pattern, search_pattern, search_pattern, search_pattern))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def generate_lp_report(self, start_date: datetime = None, end_date: datetime = None) -> Dict:
        """Generate a report suitable for Limited Partners"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Default to last 30 days if no dates provided
        if not end_date:
            end_date = datetime.now()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        report = {
            'period': {
                'start': start_date.strftime('%Y-%m-%d'),
                'end': end_date.strftime('%Y-%m-%d')
            },
            'summary': {},
            'active_deals': [],
            'closed_deals': []
        }
        
        # Get pipeline summary
        report['summary'] = self.get_pipeline_summary()
        
        # Get active deals
        cursor.execute("""
            SELECT 
                property_address, city, stage, offer_price,
                roi_rental, roi_flip, stage_updated_at
            FROM deal_pipeline
            WHERE is_archived = 0 AND stage != 'closed' AND stage != 'passed'
            ORDER BY stage_updated_at DESC
        """)
        report['active_deals'] = [dict(row) for row in cursor.fetchall()]
        
        # Get recently closed deals
        cursor.execute("""
            SELECT 
                property_address, city, actual_purchase_price,
                roi_rental, roi_flip, stage_updated_at as closed_date
            FROM deal_pipeline
            WHERE stage = 'closed' AND stage_updated_at BETWEEN ? AND ?
            ORDER BY stage_updated_at DESC
        """, (start_date, end_date))
        report['closed_deals'] = [dict(row) for row in cursor.fetchall()]
        
        # Calculate totals
        cursor.execute("""
            SELECT 
                COUNT(*) as total_deals,
                SUM(CASE WHEN stage = 'closed' THEN 1 ELSE 0 END) as closed_count,
                SUM(CASE WHEN stage = 'under_contract' THEN 1 ELSE 0 END) as under_contract,
                ROUND(AVG(roi_flip), 2) as avg_roi_flip
            FROM deal_pipeline
            WHERE created_at BETWEEN ? AND ?
        """, (start_date, end_date))
        
        totals = dict(cursor.fetchone())
        report['summary']['period_totals'] = totals
        
        conn.close()
        return report