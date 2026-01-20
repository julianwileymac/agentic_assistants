-- Migration: 004_enhanced_resources
-- Description: Enhanced resources schema for databases, ML deployments, indexing versions, 
--              service health logs, and global catalog registry
-- Created: 2026-01-11

-- ============================================================================
-- Database Connection Extensions
-- ============================================================================

-- Extended connection metadata for various database types
CREATE TABLE IF NOT EXISTS database_connections (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    driver TEXT NOT NULL,  -- postgresql, mysql, mongodb, redis, elasticsearch, bigquery, snowflake
    host TEXT,
    port INTEGER,
    database_name TEXT,
    schema_name TEXT,
    
    -- Connection options
    connection_string TEXT,  -- Encrypted connection string
    ssl_enabled BOOLEAN DEFAULT FALSE,
    ssl_cert_path TEXT,
    
    -- Authentication
    auth_type TEXT DEFAULT 'password',  -- password, key, oauth, iam
    username TEXT,
    credentials_ref TEXT,  -- Reference to secure credential store
    
    -- Metadata
    is_global BOOLEAN DEFAULT FALSE,
    project_id TEXT REFERENCES projects(id) ON DELETE CASCADE,
    status TEXT DEFAULT 'active',
    last_connected_at TIMESTAMP,
    last_connection_error TEXT,
    
    -- Schema info cache
    cached_schema TEXT,  -- JSON of discovered schema
    schema_cached_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tags TEXT DEFAULT '[]',  -- JSON array
    metadata TEXT DEFAULT '{}'  -- JSON object
);

CREATE INDEX IF NOT EXISTS idx_database_connections_driver ON database_connections(driver);
CREATE INDEX IF NOT EXISTS idx_database_connections_project ON database_connections(project_id);
CREATE INDEX IF NOT EXISTS idx_database_connections_global ON database_connections(is_global);


-- ============================================================================
-- ML Deployment Tracking
-- ============================================================================

-- Track ML model deployments across environments
CREATE TABLE IF NOT EXISTS ml_deployments (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    
    -- Model info
    model_name TEXT NOT NULL,
    model_version TEXT NOT NULL,
    model_uri TEXT,  -- MLFlow model URI or path
    model_framework TEXT,  -- pytorch, tensorflow, sklearn, etc.
    
    -- Deployment target
    target_type TEXT NOT NULL,  -- local, docker, kubernetes, sagemaker, azure_ml
    target_endpoint TEXT,
    target_config TEXT DEFAULT '{}',  -- JSON configuration
    
    -- Status
    status TEXT DEFAULT 'pending',  -- pending, deploying, active, failed, stopped
    health_status TEXT DEFAULT 'unknown',  -- healthy, unhealthy, unknown
    last_health_check TIMESTAMP,
    
    -- Resource allocation
    cpu_limit TEXT,
    memory_limit TEXT,
    gpu_enabled BOOLEAN DEFAULT FALSE,
    replicas INTEGER DEFAULT 1,
    
    -- Traffic management
    traffic_percentage INTEGER DEFAULT 100,  -- For canary/blue-green
    parent_deployment_id TEXT REFERENCES ml_deployments(id),
    
    -- Metrics
    request_count INTEGER DEFAULT 0,
    avg_latency_ms FLOAT,
    error_rate FLOAT,
    
    -- Associations
    project_id TEXT REFERENCES projects(id) ON DELETE CASCADE,
    mlflow_run_id TEXT,
    
    -- Timestamps
    deployed_at TIMESTAMP,
    stopped_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    tags TEXT DEFAULT '[]',
    metadata TEXT DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_ml_deployments_status ON ml_deployments(status);
CREATE INDEX IF NOT EXISTS idx_ml_deployments_project ON ml_deployments(project_id);
CREATE INDEX IF NOT EXISTS idx_ml_deployments_model ON ml_deployments(model_name, model_version);


-- ============================================================================
-- Versioned Indexing System
-- ============================================================================

-- Track indexing versions and metadata for projects
CREATE TABLE IF NOT EXISTS indexing_versions (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    
    -- Version info
    version TEXT NOT NULL,  -- e.g., "2.0"
    schema_version TEXT,
    collection_name TEXT,
    
    -- Status
    status TEXT DEFAULT 'idle',  -- idle, indexing, completed, failed
    progress_percent FLOAT DEFAULT 0,
    
    -- Statistics
    file_count INTEGER DEFAULT 0,
    chunk_count INTEGER DEFAULT 0,
    total_size_bytes INTEGER DEFAULT 0,
    
    -- Timing
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    duration_seconds FLOAT,
    
    -- Error tracking
    error_message TEXT,
    error_count INTEGER DEFAULT 0,
    
    -- Incremental indexing
    last_file_hash TEXT,
    files_indexed TEXT,  -- JSON array of file paths/hashes
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    metadata TEXT DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_indexing_versions_project ON indexing_versions(project_id);
CREATE INDEX IF NOT EXISTS idx_indexing_versions_status ON indexing_versions(status);
CREATE UNIQUE INDEX IF NOT EXISTS idx_indexing_versions_project_version ON indexing_versions(project_id, version);


-- ============================================================================
-- Service Health Monitoring
-- ============================================================================

-- Historical health check logs for services
CREATE TABLE IF NOT EXISTS service_health_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    service_id TEXT NOT NULL REFERENCES services(id) ON DELETE CASCADE,
    
    -- Health check results
    status TEXT NOT NULL,  -- healthy, unhealthy, timeout, error
    status_code INTEGER,
    response_time_ms FLOAT,
    
    -- Details
    endpoint_checked TEXT,
    response_body TEXT,
    error_message TEXT,
    
    -- Metrics
    cpu_usage FLOAT,
    memory_usage FLOAT,
    disk_usage FLOAT,
    
    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_service_health_logs_service ON service_health_logs(service_id);
CREATE INDEX IF NOT EXISTS idx_service_health_logs_status ON service_health_logs(status);
CREATE INDEX IF NOT EXISTS idx_service_health_logs_time ON service_health_logs(checked_at);


-- ============================================================================
-- Global Catalog Registry
-- ============================================================================

-- Global catalog entries that can be inherited by projects
CREATE TABLE IF NOT EXISTS catalog_entries_global (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    entry_type TEXT NOT NULL,  -- table, column, dataset
    
    -- Source info
    source_id TEXT,
    source_type TEXT,
    
    -- Content
    description TEXT,
    schema_definition TEXT,  -- JSON schema
    
    -- Classification
    tags TEXT DEFAULT '[]',
    categories TEXT DEFAULT '[]',
    
    -- Data governance
    owner TEXT,
    steward TEXT,
    classification TEXT,  -- public, internal, confidential, restricted
    pii_fields TEXT DEFAULT '[]',  -- JSON array of PII field names
    
    -- Statistics
    row_count INTEGER,
    size_bytes INTEGER,
    last_updated TIMESTAMP,
    
    -- Versioning
    version TEXT DEFAULT '1.0',
    previous_version_id TEXT,
    
    -- Quality
    quality_score FLOAT,
    completeness_score FLOAT,
    freshness_score FLOAT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    
    metadata TEXT DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_catalog_entries_global_type ON catalog_entries_global(entry_type);
CREATE INDEX IF NOT EXISTS idx_catalog_entries_global_source ON catalog_entries_global(source_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_catalog_entries_global_name ON catalog_entries_global(name, entry_type);


-- ============================================================================
-- Project Catalog Links
-- ============================================================================

-- Links between projects and global catalog entries (for inheritance)
CREATE TABLE IF NOT EXISTS project_catalog_links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    catalog_entry_id TEXT NOT NULL REFERENCES catalog_entries_global(id) ON DELETE CASCADE,
    
    -- Link type
    link_type TEXT DEFAULT 'inherit',  -- inherit, copy, reference
    
    -- Override settings
    override_name TEXT,
    override_description TEXT,
    override_tags TEXT,  -- JSON array
    
    -- Access control
    access_level TEXT DEFAULT 'read',  -- read, write, admin
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    
    UNIQUE(project_id, catalog_entry_id)
);

CREATE INDEX IF NOT EXISTS idx_project_catalog_links_project ON project_catalog_links(project_id);
CREATE INDEX IF NOT EXISTS idx_project_catalog_links_entry ON project_catalog_links(catalog_entry_id);


-- ============================================================================
-- Workflow Executions
-- ============================================================================

-- Track Dify-style workflow executions
CREATE TABLE IF NOT EXISTS workflow_executions (
    id TEXT PRIMARY KEY,
    workflow_id TEXT NOT NULL,
    workflow_name TEXT,
    
    -- Execution status
    status TEXT DEFAULT 'pending',  -- pending, running, completed, failed, cancelled
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    duration_seconds FLOAT,
    
    -- Input/Output
    inputs TEXT DEFAULT '{}',  -- JSON
    outputs TEXT DEFAULT '{}',  -- JSON
    
    -- Node tracking
    total_nodes INTEGER DEFAULT 0,
    completed_nodes INTEGER DEFAULT 0,
    current_node TEXT,
    node_executions TEXT DEFAULT '[]',  -- JSON array of node execution results
    
    -- Error handling
    error_message TEXT,
    error_node TEXT,
    retry_count INTEGER DEFAULT 0,
    
    -- Resource usage
    tokens_used INTEGER DEFAULT 0,
    cost_estimate FLOAT,
    
    -- Association
    project_id TEXT REFERENCES projects(id) ON DELETE SET NULL,
    triggered_by TEXT,  -- user, schedule, webhook, api
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_workflow_executions_status ON workflow_executions(status);
CREATE INDEX IF NOT EXISTS idx_workflow_executions_workflow ON workflow_executions(workflow_id);
CREATE INDEX IF NOT EXISTS idx_workflow_executions_project ON workflow_executions(project_id);


-- ============================================================================
-- Component Usage Statistics
-- ============================================================================

-- Track component usage for analytics
CREATE TABLE IF NOT EXISTS component_usage_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    component_id TEXT NOT NULL REFERENCES components(id) ON DELETE CASCADE,
    
    -- Usage metrics
    usage_count INTEGER DEFAULT 1,
    last_used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Context
    project_id TEXT REFERENCES projects(id) ON DELETE SET NULL,
    workflow_id TEXT,
    user_id TEXT,
    
    -- Performance
    avg_execution_time_ms FLOAT,
    success_count INTEGER DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_component_usage_component ON component_usage_stats(component_id);
CREATE INDEX IF NOT EXISTS idx_component_usage_project ON component_usage_stats(project_id);
CREATE INDEX IF NOT EXISTS idx_component_usage_time ON component_usage_stats(recorded_at);


-- ============================================================================
-- Migration Tracking
-- ============================================================================

-- Record that this migration has been applied
INSERT OR IGNORE INTO schema_migrations (version, name, applied_at) 
VALUES ('004', 'enhanced_resources', CURRENT_TIMESTAMP);
