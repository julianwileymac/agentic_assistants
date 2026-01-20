-- Migration: 005_learning_framework
-- Description: Learning framework tables for goals, topics, lesson plans, 
--              annotations, evaluations, and artifacts
-- Created: 2026-01-19

-- ============================================================================
-- Learning Goals Table
-- ============================================================================

-- User or project-level learning objectives
CREATE TABLE IF NOT EXISTS learning_goals (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    
    -- Scope: user-level or project-level
    level TEXT NOT NULL DEFAULT 'user',  -- user, project
    project_id TEXT REFERENCES projects(id) ON DELETE CASCADE,
    user_id TEXT,  -- For user-level goals
    
    -- Status and priority
    status TEXT NOT NULL DEFAULT 'active',  -- active, completed, paused, archived
    priority TEXT DEFAULT 'medium',  -- low, medium, high, critical
    
    -- Timeline
    target_date TEXT,  -- Target completion date
    completed_at TEXT,
    
    -- Progress tracking
    progress_percent REAL DEFAULT 0.0,
    
    -- Timestamps
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    
    -- Flexible metadata
    tags TEXT DEFAULT '[]',  -- JSON array
    metadata TEXT DEFAULT '{}'  -- JSON object
);

CREATE INDEX IF NOT EXISTS idx_learning_goals_level ON learning_goals(level);
CREATE INDEX IF NOT EXISTS idx_learning_goals_project ON learning_goals(project_id);
CREATE INDEX IF NOT EXISTS idx_learning_goals_status ON learning_goals(status);
CREATE INDEX IF NOT EXISTS idx_learning_goals_user ON learning_goals(user_id);


-- ============================================================================
-- Learning Topics Table
-- ============================================================================

-- Active learning topics with progress tracking
CREATE TABLE IF NOT EXISTS learning_topics (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    
    -- Associations
    goal_id TEXT REFERENCES learning_goals(id) ON DELETE SET NULL,
    project_id TEXT REFERENCES projects(id) ON DELETE SET NULL,
    
    -- Progress
    status TEXT NOT NULL DEFAULT 'not_started',  -- not_started, in_progress, completed, paused
    progress_percent REAL DEFAULT 0.0,
    
    -- Source information
    source_type TEXT DEFAULT 'manual',  -- manual, paper, inferred, imported
    source_reference TEXT,  -- URL, paper ID, or other reference
    
    -- Lesson plan reference (populated after generation)
    lesson_plan_id TEXT,  -- Will reference lesson_plans(id)
    
    -- Difficulty and time estimates
    difficulty_level TEXT DEFAULT 'intermediate',  -- beginner, intermediate, advanced, expert
    estimated_hours REAL,
    actual_hours REAL DEFAULT 0.0,
    
    -- Timestamps
    started_at TEXT,
    completed_at TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    
    -- Flexible metadata
    tags TEXT DEFAULT '[]',  -- JSON array
    metadata TEXT DEFAULT '{}'  -- JSON object
);

CREATE INDEX IF NOT EXISTS idx_learning_topics_goal ON learning_topics(goal_id);
CREATE INDEX IF NOT EXISTS idx_learning_topics_project ON learning_topics(project_id);
CREATE INDEX IF NOT EXISTS idx_learning_topics_status ON learning_topics(status);
CREATE INDEX IF NOT EXISTS idx_learning_topics_source ON learning_topics(source_type);


-- ============================================================================
-- Lesson Plans Table
-- ============================================================================

-- LLM-generated structured lesson plans
CREATE TABLE IF NOT EXISTS lesson_plans (
    id TEXT PRIMARY KEY,
    topic_id TEXT NOT NULL REFERENCES learning_topics(id) ON DELETE CASCADE,
    
    -- Plan content
    title TEXT NOT NULL,
    overview TEXT,
    objectives TEXT,  -- JSON array of learning objectives
    prerequisites TEXT,  -- JSON array of prerequisites
    
    -- Generation info
    generated_by TEXT,  -- Model name (e.g., "llama3.2")
    generation_prompt TEXT,  -- The prompt used to generate this plan
    generation_config TEXT,  -- JSON config used for generation
    
    -- Status
    status TEXT DEFAULT 'draft',  -- draft, active, completed, archived
    version INTEGER DEFAULT 1,
    
    -- Completion tracking
    total_sections INTEGER DEFAULT 0,
    completed_sections INTEGER DEFAULT 0,
    
    -- Estimated duration
    estimated_duration_minutes INTEGER,
    
    -- Timestamps
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    
    -- Flexible metadata
    metadata TEXT DEFAULT '{}'  -- JSON object
);

CREATE INDEX IF NOT EXISTS idx_lesson_plans_topic ON lesson_plans(topic_id);
CREATE INDEX IF NOT EXISTS idx_lesson_plans_status ON lesson_plans(status);


-- ============================================================================
-- Lesson Plan Sections Table
-- ============================================================================

-- Individual sections within lesson plans
CREATE TABLE IF NOT EXISTS lesson_plan_sections (
    id TEXT PRIMARY KEY,
    lesson_plan_id TEXT NOT NULL REFERENCES lesson_plans(id) ON DELETE CASCADE,
    
    -- Section content
    title TEXT NOT NULL,
    content TEXT,  -- Main content (markdown supported)
    summary TEXT,  -- Brief summary
    
    -- Ordering
    section_order INTEGER NOT NULL DEFAULT 0,
    parent_section_id TEXT REFERENCES lesson_plan_sections(id) ON DELETE CASCADE,
    
    -- Section type
    section_type TEXT DEFAULT 'content',  -- content, exercise, quiz, reading, project
    
    -- Completion tracking
    is_completed BOOLEAN DEFAULT FALSE,
    completed_at TEXT,
    
    -- Time tracking
    estimated_minutes INTEGER,
    actual_minutes INTEGER,
    
    -- Resources and exercises
    resources TEXT DEFAULT '[]',  -- JSON array of resource links
    exercises TEXT DEFAULT '[]',  -- JSON array of exercises
    
    -- Timestamps
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    
    -- Flexible metadata
    metadata TEXT DEFAULT '{}'  -- JSON object
);

CREATE INDEX IF NOT EXISTS idx_lesson_sections_plan ON lesson_plan_sections(lesson_plan_id);
CREATE INDEX IF NOT EXISTS idx_lesson_sections_order ON lesson_plan_sections(lesson_plan_id, section_order);
CREATE INDEX IF NOT EXISTS idx_lesson_sections_parent ON lesson_plan_sections(parent_section_id);


-- ============================================================================
-- Learning Annotations Table
-- ============================================================================

-- Notes, highlights, questions, and chat messages tied to resources
CREATE TABLE IF NOT EXISTS learning_annotations (
    id TEXT PRIMARY KEY,
    
    -- Resource association (polymorphic)
    resource_type TEXT NOT NULL,  -- topic, lesson_plan, section, artifact, goal
    resource_id TEXT NOT NULL,
    
    -- Annotation content
    content TEXT NOT NULL,
    annotation_type TEXT NOT NULL DEFAULT 'note',  -- note, highlight, question, answer, chat, bookmark
    
    -- Position info (for highlights in documents)
    position TEXT,  -- JSON object with start/end positions, page numbers, etc.
    
    -- For chat messages
    role TEXT,  -- user, assistant (for chat type annotations)
    
    -- User info
    user_id TEXT,
    
    -- Visibility
    is_private BOOLEAN DEFAULT TRUE,
    
    -- Timestamps
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    
    -- Flexible metadata
    tags TEXT DEFAULT '[]',  -- JSON array
    metadata TEXT DEFAULT '{}'  -- JSON object
);

CREATE INDEX IF NOT EXISTS idx_learning_annotations_resource ON learning_annotations(resource_type, resource_id);
CREATE INDEX IF NOT EXISTS idx_learning_annotations_type ON learning_annotations(annotation_type);
CREATE INDEX IF NOT EXISTS idx_learning_annotations_user ON learning_annotations(user_id);


-- ============================================================================
-- Learning Evaluations Table
-- ============================================================================

-- Grading results from evaluation agent
CREATE TABLE IF NOT EXISTS learning_evaluations (
    id TEXT PRIMARY KEY,
    
    -- What is being evaluated
    topic_id TEXT REFERENCES learning_topics(id) ON DELETE SET NULL,
    lesson_plan_id TEXT REFERENCES lesson_plans(id) ON DELETE SET NULL,
    section_id TEXT REFERENCES lesson_plan_sections(id) ON DELETE SET NULL,
    
    -- Evaluation type
    evaluation_type TEXT DEFAULT 'comprehension',  -- comprehension, application, synthesis, quiz
    
    -- Question and response
    question TEXT NOT NULL,
    user_response TEXT NOT NULL,
    
    -- Evaluation result
    score REAL,  -- 0-100 numeric score
    grade TEXT,  -- Letter grade or pass/fail
    feedback TEXT,  -- Detailed feedback from evaluator
    evaluation_result TEXT,  -- JSON with detailed breakdown
    
    -- Evaluator info
    evaluated_by TEXT,  -- Model name or 'human'
    evaluation_prompt TEXT,  -- Prompt used for evaluation
    
    -- Status
    status TEXT DEFAULT 'pending',  -- pending, completed, failed
    
    -- Timestamps
    submitted_at TEXT NOT NULL DEFAULT (datetime('now')),
    evaluated_at TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    
    -- User info
    user_id TEXT,
    
    -- Flexible metadata
    metadata TEXT DEFAULT '{}'  -- JSON object
);

CREATE INDEX IF NOT EXISTS idx_learning_evaluations_topic ON learning_evaluations(topic_id);
CREATE INDEX IF NOT EXISTS idx_learning_evaluations_plan ON learning_evaluations(lesson_plan_id);
CREATE INDEX IF NOT EXISTS idx_learning_evaluations_user ON learning_evaluations(user_id);
CREATE INDEX IF NOT EXISTS idx_learning_evaluations_status ON learning_evaluations(status);


-- ============================================================================
-- Learning Artifacts Table
-- ============================================================================

-- Uploaded documents, papers, and reference materials
CREATE TABLE IF NOT EXISTS learning_artifacts (
    id TEXT PRIMARY KEY,
    
    -- Basic info
    name TEXT NOT NULL,
    description TEXT,
    
    -- File information
    file_path TEXT,
    file_type TEXT,  -- pdf, txt, md, url, etc.
    file_size INTEGER,
    original_filename TEXT,
    
    -- For URL-based artifacts
    source_url TEXT,
    
    -- Content extraction
    extracted_text TEXT,  -- Full extracted text content
    summary TEXT,  -- AI-generated summary
    
    -- Vector storage reference
    vector_collection TEXT,  -- ChromaDB collection name
    chunk_count INTEGER DEFAULT 0,
    
    -- Associations
    topic_id TEXT REFERENCES learning_topics(id) ON DELETE SET NULL,
    goal_id TEXT REFERENCES learning_goals(id) ON DELETE SET NULL,
    project_id TEXT REFERENCES projects(id) ON DELETE SET NULL,
    
    -- Processing status
    processing_status TEXT DEFAULT 'pending',  -- pending, processing, completed, failed
    processing_error TEXT,
    
    -- User info
    uploaded_by TEXT,
    
    -- Timestamps
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    processed_at TEXT,
    
    -- Flexible metadata
    tags TEXT DEFAULT '[]',  -- JSON array
    metadata TEXT DEFAULT '{}'  -- JSON object
);

CREATE INDEX IF NOT EXISTS idx_learning_artifacts_topic ON learning_artifacts(topic_id);
CREATE INDEX IF NOT EXISTS idx_learning_artifacts_goal ON learning_artifacts(goal_id);
CREATE INDEX IF NOT EXISTS idx_learning_artifacts_project ON learning_artifacts(project_id);
CREATE INDEX IF NOT EXISTS idx_learning_artifacts_status ON learning_artifacts(processing_status);


-- ============================================================================
-- Learning Chat Sessions Table
-- ============================================================================

-- Chat sessions for topic-based learning conversations
CREATE TABLE IF NOT EXISTS learning_chat_sessions (
    id TEXT PRIMARY KEY,
    
    -- Context
    topic_id TEXT REFERENCES learning_topics(id) ON DELETE CASCADE,
    lesson_plan_id TEXT REFERENCES lesson_plans(id) ON DELETE SET NULL,
    section_id TEXT REFERENCES lesson_plan_sections(id) ON DELETE SET NULL,
    
    -- Session info
    title TEXT,
    system_prompt TEXT,
    model TEXT,  -- Model used for this session
    
    -- Message count
    message_count INTEGER DEFAULT 0,
    
    -- Status
    status TEXT DEFAULT 'active',  -- active, archived
    
    -- User info
    user_id TEXT,
    
    -- Timestamps
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    last_message_at TEXT,
    
    -- Flexible metadata
    metadata TEXT DEFAULT '{}'  -- JSON object
);

CREATE INDEX IF NOT EXISTS idx_learning_chat_sessions_topic ON learning_chat_sessions(topic_id);
CREATE INDEX IF NOT EXISTS idx_learning_chat_sessions_user ON learning_chat_sessions(user_id);


-- ============================================================================
-- Learning Progress Snapshots Table
-- ============================================================================

-- Historical progress snapshots for analytics
CREATE TABLE IF NOT EXISTS learning_progress_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- What is being tracked
    entity_type TEXT NOT NULL,  -- goal, topic, lesson_plan
    entity_id TEXT NOT NULL,
    
    -- Progress at snapshot time
    progress_percent REAL,
    status TEXT,
    
    -- Additional metrics
    completed_items INTEGER,
    total_items INTEGER,
    time_spent_minutes INTEGER,
    
    -- Snapshot timestamp
    snapshot_at TEXT NOT NULL DEFAULT (datetime('now')),
    
    -- User info
    user_id TEXT
);

CREATE INDEX IF NOT EXISTS idx_learning_progress_entity ON learning_progress_snapshots(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_learning_progress_time ON learning_progress_snapshots(snapshot_at);


-- ============================================================================
-- Update lesson_plan_id foreign key in learning_topics
-- ============================================================================

-- Add foreign key constraint (SQLite doesn't support ALTER TABLE ADD CONSTRAINT)
-- The relationship is established through application logic


-- ============================================================================
-- Migration Tracking
-- ============================================================================

-- Record that this migration has been applied
INSERT OR IGNORE INTO schema_migrations (version, name, applied_at) 
VALUES ('005', 'learning_framework', CURRENT_TIMESTAMP);
