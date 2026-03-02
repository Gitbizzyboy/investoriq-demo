-- Deal Pipeline Manager Schema for InvestorIQ
-- Tracks properties through investment stages with full documentation

-- Main pipeline table
CREATE TABLE IF NOT EXISTS deal_pipeline (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    property_id TEXT NOT NULL,  -- Links to master_distressed_properties
    property_address TEXT NOT NULL,
    city TEXT,
    county TEXT,
    state TEXT,
    
    -- Pipeline stage tracking
    stage TEXT NOT NULL DEFAULT 'watching',  -- watching, analyzing, offer_submitted, under_contract, closed, passed
    stage_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Financial tracking
    asking_price REAL,
    offer_price REAL,
    accepted_price REAL,
    estimated_repairs REAL,
    actual_purchase_price REAL,
    
    -- ROI calculations snapshot
    roi_rental REAL,
    roi_flip REAL,
    roi_brrrr REAL,
    risk_score INTEGER,
    
    -- Investor assignment
    assigned_to TEXT,  -- Investor name or ID
    investor_notes TEXT,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    
    -- Status flags
    is_priority BOOLEAN DEFAULT 0,
    is_archived BOOLEAN DEFAULT 0
);

-- Deal documents storage
CREATE TABLE IF NOT EXISTS deal_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    deal_id INTEGER NOT NULL,
    document_name TEXT NOT NULL,
    document_type TEXT,  -- photo, contract, inspection, estimate, report
    file_path TEXT NOT NULL,
    file_size INTEGER,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    uploaded_by TEXT,
    notes TEXT,
    FOREIGN KEY (deal_id) REFERENCES deal_pipeline(id) ON DELETE CASCADE
);

-- Deal notes and activity timeline
CREATE TABLE IF NOT EXISTS deal_notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    deal_id INTEGER NOT NULL,
    note_type TEXT,  -- general, inspection, negotiation, financial
    note_content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    is_private BOOLEAN DEFAULT 0,  -- For sensitive notes not shown to LPs
    FOREIGN KEY (deal_id) REFERENCES deal_pipeline(id) ON DELETE CASCADE
);

-- Stage transition history for audit trail
CREATE TABLE IF NOT EXISTS deal_stage_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    deal_id INTEGER NOT NULL,
    previous_stage TEXT,
    new_stage TEXT NOT NULL,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    changed_by TEXT,
    reason TEXT,  -- Why the stage changed
    FOREIGN KEY (deal_id) REFERENCES deal_pipeline(id) ON DELETE CASCADE
);

-- Deal team members (for larger deals with multiple people)
CREATE TABLE IF NOT EXISTS deal_team (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    deal_id INTEGER NOT NULL,
    member_name TEXT NOT NULL,
    member_role TEXT,  -- investor, contractor, agent, attorney
    member_email TEXT,
    member_phone TEXT,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (deal_id) REFERENCES deal_pipeline(id) ON DELETE CASCADE
);

-- Deal tasks and checklist
CREATE TABLE IF NOT EXISTS deal_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    deal_id INTEGER NOT NULL,
    task_name TEXT NOT NULL,
    task_category TEXT,  -- due_diligence, financing, closing
    due_date DATE,
    assigned_to TEXT,
    is_completed BOOLEAN DEFAULT 0,
    completed_at TIMESTAMP,
    completed_by TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (deal_id) REFERENCES deal_pipeline(id) ON DELETE CASCADE
);

-- Create indexes for performance
CREATE INDEX idx_deal_pipeline_stage ON deal_pipeline(stage);
CREATE INDEX idx_deal_pipeline_created ON deal_pipeline(created_at);
CREATE INDEX idx_deal_documents_deal ON deal_documents(deal_id);
CREATE INDEX idx_deal_notes_deal ON deal_notes(deal_id);
CREATE INDEX idx_deal_stage_history_deal ON deal_stage_history(deal_id);

-- Create view for pipeline summary
CREATE VIEW pipeline_summary AS
SELECT 
    stage,
    COUNT(*) as deal_count,
    SUM(CASE WHEN is_priority = 1 THEN 1 ELSE 0 END) as priority_count,
    AVG(offer_price) as avg_offer_price,
    SUM(offer_price) as total_pipeline_value
FROM deal_pipeline
WHERE is_archived = 0
GROUP BY stage;