-- Migration: 006_lineage
-- Description: Add document lineage tracking tables
-- Created: 2026-01-19

-- Document lineage records
CREATE TABLE IF NOT EXISTS document_lineage (
    document_id TEXT PRIMARY KEY,
    source_uri TEXT NOT NULL,
    source_type TEXT NOT NULL,  -- file, url, github, s3, api, database, manual, generated
    collection TEXT NOT NULL,
    ingestion_pipeline TEXT,
    ingestion_run_id TEXT,
    ingestion_timestamp TEXT NOT NULL,
    tags TEXT,  -- JSON array
    metadata TEXT,  -- JSON object
    project_id TEXT,
    user_id TEXT,
    version INTEGER DEFAULT 1,
    previous_version_id TEXT,
    is_deleted INTEGER DEFAULT 0,
    deleted_at TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Processing steps for each document
CREATE TABLE IF NOT EXISTS processing_steps (
    step_id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL,
    step_type TEXT NOT NULL,  -- ingest, chunk, embed, augment, annotate, transform, index, update, delete
    step_name TEXT,
    timestamp TEXT NOT NULL,
    duration_ms REAL DEFAULT 0,
    config TEXT,  -- JSON object
    metrics TEXT,  -- JSON object (chunk_count, token_count, etc.)
    error TEXT,
    parent_step_id TEXT,
    FOREIGN KEY (document_id) REFERENCES document_lineage(document_id) ON DELETE CASCADE
);

-- Document relationships (parent-child for chunks)
CREATE TABLE IF NOT EXISTS document_relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    parent_document_id TEXT NOT NULL,
    child_document_id TEXT NOT NULL,
    relationship_type TEXT DEFAULT 'chunk',  -- chunk, derived, related
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_document_id) REFERENCES document_lineage(document_id) ON DELETE CASCADE,
    FOREIGN KEY (child_document_id) REFERENCES document_lineage(document_id) ON DELETE CASCADE,
    UNIQUE(parent_document_id, child_document_id, relationship_type)
);

-- Lineage events (audit trail)
CREATE TABLE IF NOT EXISTS lineage_events (
    event_id TEXT PRIMARY KEY,
    event_type TEXT NOT NULL,  -- created, updated, deleted, accessed, exported
    document_id TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    user_id TEXT,
    details TEXT,  -- JSON object
    FOREIGN KEY (document_id) REFERENCES document_lineage(document_id) ON DELETE CASCADE
);

-- Document tags table for efficient tag queries
CREATE TABLE IF NOT EXISTS document_tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id TEXT NOT NULL,
    tag TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES document_lineage(document_id) ON DELETE CASCADE,
    UNIQUE(document_id, tag)
);

-- Tag hierarchy for nested tags
CREATE TABLE IF NOT EXISTS tag_hierarchy (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    parent_tag TEXT NOT NULL,
    child_tag TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(parent_tag, child_tag)
);

-- Indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_lineage_collection ON document_lineage(collection);
CREATE INDEX IF NOT EXISTS idx_lineage_project ON document_lineage(project_id);
CREATE INDEX IF NOT EXISTS idx_lineage_user ON document_lineage(user_id);
CREATE INDEX IF NOT EXISTS idx_lineage_source_type ON document_lineage(source_type);
CREATE INDEX IF NOT EXISTS idx_lineage_pipeline ON document_lineage(ingestion_pipeline);
CREATE INDEX IF NOT EXISTS idx_lineage_timestamp ON document_lineage(ingestion_timestamp);
CREATE INDEX IF NOT EXISTS idx_lineage_deleted ON document_lineage(is_deleted);

CREATE INDEX IF NOT EXISTS idx_steps_document ON processing_steps(document_id);
CREATE INDEX IF NOT EXISTS idx_steps_type ON processing_steps(step_type);
CREATE INDEX IF NOT EXISTS idx_steps_timestamp ON processing_steps(timestamp);

CREATE INDEX IF NOT EXISTS idx_relationships_parent ON document_relationships(parent_document_id);
CREATE INDEX IF NOT EXISTS idx_relationships_child ON document_relationships(child_document_id);
CREATE INDEX IF NOT EXISTS idx_relationships_type ON document_relationships(relationship_type);

CREATE INDEX IF NOT EXISTS idx_events_document ON lineage_events(document_id);
CREATE INDEX IF NOT EXISTS idx_events_type ON lineage_events(event_type);
CREATE INDEX IF NOT EXISTS idx_events_timestamp ON lineage_events(timestamp);
CREATE INDEX IF NOT EXISTS idx_events_user ON lineage_events(user_id);

CREATE INDEX IF NOT EXISTS idx_doc_tags_document ON document_tags(document_id);
CREATE INDEX IF NOT EXISTS idx_doc_tags_tag ON document_tags(tag);

CREATE INDEX IF NOT EXISTS idx_tag_hierarchy_parent ON tag_hierarchy(parent_tag);
CREATE INDEX IF NOT EXISTS idx_tag_hierarchy_child ON tag_hierarchy(child_tag);

-- Views for common queries

-- View: Documents with their chunk counts
CREATE VIEW IF NOT EXISTS v_document_chunk_counts AS
SELECT 
    dl.document_id,
    dl.source_uri,
    dl.collection,
    dl.ingestion_timestamp,
    COUNT(dr.child_document_id) as chunk_count
FROM document_lineage dl
LEFT JOIN document_relationships dr ON dl.document_id = dr.parent_document_id
WHERE dl.is_deleted = 0
GROUP BY dl.document_id;

-- View: Processing summary per document
CREATE VIEW IF NOT EXISTS v_document_processing_summary AS
SELECT 
    ps.document_id,
    GROUP_CONCAT(DISTINCT ps.step_type) as step_types,
    COUNT(ps.step_id) as total_steps,
    SUM(ps.duration_ms) as total_duration_ms,
    MAX(ps.timestamp) as last_processed
FROM processing_steps ps
GROUP BY ps.document_id;

-- View: Tag usage statistics
CREATE VIEW IF NOT EXISTS v_tag_stats AS
SELECT 
    dt.tag,
    COUNT(DISTINCT dt.document_id) as document_count,
    th.parent_tag
FROM document_tags dt
LEFT JOIN tag_hierarchy th ON dt.tag = th.child_tag
GROUP BY dt.tag;
