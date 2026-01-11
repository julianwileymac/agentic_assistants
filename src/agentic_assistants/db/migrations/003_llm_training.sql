-- Migration: LLM Training and Model Management Tables
-- Version: 003
-- Description: Add tables for custom models, training jobs, RL experiments, 
--              data tagging, and lineage tracking

-- =============================================================================
-- Custom Models Table
-- =============================================================================
CREATE TABLE IF NOT EXISTS custom_models (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    base_model TEXT NOT NULL,
    training_method TEXT NOT NULL DEFAULT 'lora',  -- lora, qlora, full
    training_job_id TEXT,
    local_path TEXT,
    hf_repo_id TEXT,
    status TEXT NOT NULL DEFAULT 'created',  -- created, deployed, archived
    metrics TEXT,  -- JSON
    training_config TEXT,  -- JSON
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    tags TEXT,  -- JSON array
    description TEXT,
    mlflow_run_id TEXT,
    mlflow_model_uri TEXT,
    FOREIGN KEY (training_job_id) REFERENCES training_jobs(id)
);

CREATE INDEX IF NOT EXISTS idx_custom_models_name ON custom_models(name);
CREATE INDEX IF NOT EXISTS idx_custom_models_status ON custom_models(status);
CREATE INDEX IF NOT EXISTS idx_custom_models_base_model ON custom_models(base_model);

-- =============================================================================
-- Training Jobs Table
-- =============================================================================
CREATE TABLE IF NOT EXISTS training_jobs (
    id TEXT PRIMARY KEY,
    config TEXT NOT NULL,  -- JSON training config
    status TEXT NOT NULL DEFAULT 'pending',  -- pending, queued, preparing, running, completed, failed, cancelled
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    started_at TEXT,
    completed_at TEXT,
    progress REAL DEFAULT 0.0,
    metrics TEXT,  -- JSON
    logs TEXT,  -- JSON array of log lines
    error_message TEXT,
    output_model_path TEXT,
    output_model_id TEXT,
    mlflow_run_id TEXT,
    mlflow_experiment_id TEXT,
    framework TEXT DEFAULT 'llama_factory',
    FOREIGN KEY (output_model_id) REFERENCES custom_models(id)
);

CREATE INDEX IF NOT EXISTS idx_training_jobs_status ON training_jobs(status);
CREATE INDEX IF NOT EXISTS idx_training_jobs_created ON training_jobs(created_at);

-- =============================================================================
-- Training Datasets Table
-- =============================================================================
CREATE TABLE IF NOT EXISTS training_datasets (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    format TEXT NOT NULL DEFAULT 'alpaca',  -- alpaca, sharegpt, dpo, rlhf
    filepath TEXT,
    hf_dataset_id TEXT,
    num_samples INTEGER DEFAULT 0,
    size_bytes INTEGER DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    version TEXT DEFAULT '1.0.0',
    quality_metrics TEXT,  -- JSON
    source_datasets TEXT,  -- JSON array
    transformations TEXT  -- JSON array
);

CREATE INDEX IF NOT EXISTS idx_training_datasets_name ON training_datasets(name);
CREATE INDEX IF NOT EXISTS idx_training_datasets_format ON training_datasets(format);

-- =============================================================================
-- Data Tags Table
-- =============================================================================
CREATE TABLE IF NOT EXISTS data_tags (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL DEFAULT 'custom',  -- data_type, quality, domain, task, source, processing, language, custom
    description TEXT,
    color TEXT DEFAULT '#808080',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    created_by TEXT,
    usage_count INTEGER DEFAULT 0,
    UNIQUE(name, category)
);

CREATE INDEX IF NOT EXISTS idx_data_tags_category ON data_tags(category);
CREATE INDEX IF NOT EXISTS idx_data_tags_name ON data_tags(name);

-- =============================================================================
-- Dataset Tags (Many-to-Many)
-- =============================================================================
CREATE TABLE IF NOT EXISTS dataset_tags (
    id TEXT PRIMARY KEY,
    tag_id TEXT NOT NULL,
    resource_type TEXT NOT NULL,  -- dataset, sample, model
    resource_id TEXT NOT NULL,
    confidence REAL,
    notes TEXT,
    assigned_at TEXT NOT NULL DEFAULT (datetime('now')),
    assigned_by TEXT,
    FOREIGN KEY (tag_id) REFERENCES data_tags(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_dataset_tags_tag ON dataset_tags(tag_id);
CREATE INDEX IF NOT EXISTS idx_dataset_tags_resource ON dataset_tags(resource_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_dataset_tags_unique ON dataset_tags(tag_id, resource_type, resource_id);

-- =============================================================================
-- Data Lineage Table
-- =============================================================================
CREATE TABLE IF NOT EXISTS data_lineage (
    id TEXT PRIMARY KEY,
    model_id TEXT NOT NULL,
    training_job_id TEXT NOT NULL,
    dataset_id TEXT NOT NULL,
    dataset_version TEXT,
    dataset_name TEXT,
    transformation_steps TEXT,  -- JSON array
    filters_applied TEXT,  -- JSON array
    quality_metrics TEXT,  -- JSON
    sample_count INTEGER DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    metadata TEXT,  -- JSON
    FOREIGN KEY (model_id) REFERENCES custom_models(id),
    FOREIGN KEY (training_job_id) REFERENCES training_jobs(id),
    FOREIGN KEY (dataset_id) REFERENCES training_datasets(id)
);

CREATE INDEX IF NOT EXISTS idx_data_lineage_model ON data_lineage(model_id);
CREATE INDEX IF NOT EXISTS idx_data_lineage_dataset ON data_lineage(dataset_id);

-- =============================================================================
-- Data Relations Table (for lineage graph)
-- =============================================================================
CREATE TABLE IF NOT EXISTS data_relations (
    id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL,
    source_type TEXT NOT NULL,  -- dataset, model, experiment
    target_id TEXT NOT NULL,
    target_type TEXT NOT NULL,
    relationship TEXT NOT NULL,  -- derived_from, transforms_to, subset_of, merged_from, trained_on, evaluated_on
    description TEXT,
    transformation TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    metadata TEXT  -- JSON
);

CREATE INDEX IF NOT EXISTS idx_data_relations_source ON data_relations(source_id);
CREATE INDEX IF NOT EXISTS idx_data_relations_target ON data_relations(target_id);

-- =============================================================================
-- RL Experiments Table
-- =============================================================================
CREATE TABLE IF NOT EXISTS rl_experiments (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    method TEXT NOT NULL,  -- dpo, ppo, rlhf, reward_model, orpo, kto
    config TEXT NOT NULL,  -- JSON
    status TEXT NOT NULL DEFAULT 'pending',  -- pending, running, completed, failed, cancelled
    base_model TEXT NOT NULL,
    reward_model_id TEXT,
    output_model_id TEXT,
    preference_dataset_id TEXT,
    prompt_dataset_id TEXT,
    metrics TEXT,  -- JSON
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    started_at TEXT,
    completed_at TEXT,
    logs TEXT,  -- JSON array
    error_message TEXT,
    mlflow_experiment_id TEXT,
    mlflow_run_id TEXT,
    tags TEXT,  -- JSON array
    description TEXT,
    FOREIGN KEY (reward_model_id) REFERENCES custom_models(id),
    FOREIGN KEY (output_model_id) REFERENCES custom_models(id),
    FOREIGN KEY (preference_dataset_id) REFERENCES training_datasets(id)
);

CREATE INDEX IF NOT EXISTS idx_rl_experiments_method ON rl_experiments(method);
CREATE INDEX IF NOT EXISTS idx_rl_experiments_status ON rl_experiments(status);

-- =============================================================================
-- Preference Data Table (for RLHF)
-- =============================================================================
CREATE TABLE IF NOT EXISTS preference_data (
    id TEXT PRIMARY KEY,
    dataset_id TEXT NOT NULL,
    prompt TEXT NOT NULL,
    chosen TEXT NOT NULL,
    rejected TEXT NOT NULL,
    chosen_score REAL,
    rejected_score REAL,
    source TEXT,
    annotator_id TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    metadata TEXT,  -- JSON
    FOREIGN KEY (dataset_id) REFERENCES training_datasets(id)
);

CREATE INDEX IF NOT EXISTS idx_preference_data_dataset ON preference_data(dataset_id);

-- =============================================================================
-- Human Feedback Table
-- =============================================================================
CREATE TABLE IF NOT EXISTS human_feedback (
    id TEXT PRIMARY KEY,
    experiment_id TEXT,
    prompt TEXT NOT NULL,
    response_a TEXT NOT NULL,
    response_b TEXT NOT NULL,
    preference INTEGER DEFAULT 0,  -- 0=tie, 1=A, 2=B
    rating_a REAL,
    rating_b REAL,
    annotator_id TEXT,
    timestamp TEXT NOT NULL DEFAULT (datetime('now')),
    notes TEXT,
    metadata TEXT,  -- JSON
    FOREIGN KEY (experiment_id) REFERENCES rl_experiments(id)
);

CREATE INDEX IF NOT EXISTS idx_human_feedback_experiment ON human_feedback(experiment_id);
CREATE INDEX IF NOT EXISTS idx_human_feedback_annotator ON human_feedback(annotator_id);

-- =============================================================================
-- Model Deployments Table
-- =============================================================================
CREATE TABLE IF NOT EXISTS model_deployments (
    id TEXT PRIMARY KEY,
    model_id TEXT NOT NULL,
    name TEXT NOT NULL,
    backend TEXT NOT NULL,  -- ollama, vllm, tgi
    host TEXT DEFAULT 'localhost',
    port INTEGER,
    status TEXT NOT NULL DEFAULT 'stopped',  -- stopped, starting, running, error
    config TEXT,  -- JSON
    endpoint_url TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    last_health_check TEXT,
    metadata TEXT,  -- JSON
    FOREIGN KEY (model_id) REFERENCES custom_models(id)
);

CREATE INDEX IF NOT EXISTS idx_model_deployments_model ON model_deployments(model_id);
CREATE INDEX IF NOT EXISTS idx_model_deployments_status ON model_deployments(status);

-- =============================================================================
-- Insert Default Tags
-- =============================================================================
INSERT OR IGNORE INTO data_tags (id, name, category, description, color) VALUES
    ('tag-instruct', 'instruct', 'data_type', 'Instruction-following data', '#4CAF50'),
    ('tag-preference', 'preference', 'data_type', 'Preference/comparison data for RLHF/DPO', '#2196F3'),
    ('tag-completion', 'completion', 'data_type', 'Text completion data', '#9C27B0'),
    ('tag-chat', 'chat', 'data_type', 'Conversational data', '#FF9800'),
    ('tag-high-quality', 'high_quality', 'quality', 'High quality, verified data', '#4CAF50'),
    ('tag-needs-review', 'needs_review', 'quality', 'Requires manual review', '#FFC107'),
    ('tag-synthetic', 'synthetic', 'source', 'Synthetically generated data', '#00BCD4'),
    ('tag-human', 'human', 'source', 'Human-created data', '#E91E63'),
    ('tag-code', 'code', 'domain', 'Programming and code-related', '#607D8B'),
    ('tag-general', 'general', 'domain', 'General domain data', '#795548');
