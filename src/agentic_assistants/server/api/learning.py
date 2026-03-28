"""
Learning API Router for Agentic Assistants.

Provides endpoints for:
- Learning goals (user and project level)
- Learning topics with progress tracking
- Lesson plan generation and management
- Research paper import and parsing
- Interactive learning chat
"""

import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Query
from pydantic import BaseModel, Field

from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/learning", tags=["learning"])


# ============================================================================
# Pydantic Models
# ============================================================================

class LearningGoalCreate(BaseModel):
    """Create a new learning goal."""
    title: str
    description: Optional[str] = None
    level: str = "user"  # user or project
    project_id: Optional[str] = None
    priority: str = "medium"
    target_date: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class LearningGoalUpdate(BaseModel):
    """Update an existing learning goal."""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    target_date: Optional[str] = None
    progress_percent: Optional[float] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class LearningGoal(BaseModel):
    """Learning goal response model."""
    id: str
    title: str
    description: Optional[str] = None
    level: str
    project_id: Optional[str] = None
    user_id: Optional[str] = None
    status: str
    priority: str
    target_date: Optional[str] = None
    completed_at: Optional[str] = None
    progress_percent: float
    created_at: str
    updated_at: str
    tags: List[str]
    metadata: Dict[str, Any]


class LearningTopicCreate(BaseModel):
    """Create a new learning topic."""
    name: str
    description: Optional[str] = None
    goal_id: Optional[str] = None
    project_id: Optional[str] = None
    source_type: str = "manual"
    source_reference: Optional[str] = None
    difficulty_level: str = "intermediate"
    estimated_hours: Optional[float] = None
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class LearningTopicUpdate(BaseModel):
    """Update an existing learning topic."""
    name: Optional[str] = None
    description: Optional[str] = None
    goal_id: Optional[str] = None
    status: Optional[str] = None
    progress_percent: Optional[float] = None
    difficulty_level: Optional[str] = None
    estimated_hours: Optional[float] = None
    actual_hours: Optional[float] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class LearningTopic(BaseModel):
    """Learning topic response model."""
    id: str
    name: str
    description: Optional[str] = None
    goal_id: Optional[str] = None
    project_id: Optional[str] = None
    status: str
    progress_percent: float
    source_type: str
    source_reference: Optional[str] = None
    lesson_plan_id: Optional[str] = None
    difficulty_level: str
    estimated_hours: Optional[float] = None
    actual_hours: float
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    created_at: str
    updated_at: str
    tags: List[str]
    metadata: Dict[str, Any]


class LessonPlanSection(BaseModel):
    """Lesson plan section model."""
    id: str
    title: str
    content: Optional[str] = None
    summary: Optional[str] = None
    section_order: int
    parent_section_id: Optional[str] = None
    section_type: str
    is_completed: bool
    completed_at: Optional[str] = None
    estimated_minutes: Optional[int] = None
    actual_minutes: Optional[int] = None
    resources: List[Dict[str, Any]]
    exercises: List[Dict[str, Any]]
    created_at: str
    updated_at: str
    metadata: Dict[str, Any]


class LessonPlan(BaseModel):
    """Lesson plan response model."""
    id: str
    topic_id: str
    title: str
    overview: Optional[str] = None
    objectives: List[str]
    prerequisites: List[str]
    generated_by: Optional[str] = None
    status: str
    version: int
    total_sections: int
    completed_sections: int
    estimated_duration_minutes: Optional[int] = None
    created_at: str
    updated_at: str
    metadata: Dict[str, Any]
    sections: List[LessonPlanSection] = Field(default_factory=list)


class GeneratePlanRequest(BaseModel):
    """Request to generate a lesson plan."""
    model: Optional[str] = None
    additional_context: Optional[str] = None
    difficulty_preference: Optional[str] = None
    include_exercises: bool = True
    include_resources: bool = True


class SectionUpdateRequest(BaseModel):
    """Update a lesson plan section."""
    is_completed: Optional[bool] = None
    actual_minutes: Optional[int] = None
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class LearningChatRequest(BaseModel):
    """Request for learning chat."""
    topic_id: str
    message: str
    session_id: Optional[str] = None
    include_lesson_context: bool = True


class LearningChatResponse(BaseModel):
    """Response from learning chat."""
    session_id: str
    message: Dict[str, str]  # role and content
    topic_context: Optional[str] = None


class ImportPaperRequest(BaseModel):
    """Request to import a research paper."""
    url: Optional[str] = None
    title: Optional[str] = None
    goal_id: Optional[str] = None
    project_id: Optional[str] = None
    auto_generate_plans: bool = False


class ImportPaperResponse(BaseModel):
    """Response from paper import."""
    artifact_id: str
    extracted_topics: List[Dict[str, Any]]
    summary: Optional[str] = None
    status: str


class LearningAnnotationCreate(BaseModel):
    """Create a learning annotation."""
    resource_type: str
    resource_id: str
    content: str
    annotation_type: str = "note"
    position: Optional[Dict[str, Any]] = None
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class LearningAnnotation(BaseModel):
    """Learning annotation response model."""
    id: str
    resource_type: str
    resource_id: str
    content: str
    annotation_type: str
    position: Optional[Dict[str, Any]] = None
    role: Optional[str] = None
    user_id: Optional[str] = None
    is_private: bool
    created_at: str
    updated_at: str
    tags: List[str]
    metadata: Dict[str, Any]


# ============================================================================
# Database Helper Functions
# ============================================================================

_tables_initialized = False


def _init_learning_tables(conn):
    """Create all learning framework tables if they don't already exist."""
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS learning_goals (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            level TEXT NOT NULL DEFAULT 'user',
            project_id TEXT,
            user_id TEXT,
            status TEXT NOT NULL DEFAULT 'active',
            priority TEXT DEFAULT 'medium',
            target_date TEXT,
            completed_at TEXT,
            progress_percent REAL DEFAULT 0.0,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now')),
            tags TEXT DEFAULT '[]',
            metadata TEXT DEFAULT '{}'
        );
        CREATE INDEX IF NOT EXISTS idx_learning_goals_level ON learning_goals(level);
        CREATE INDEX IF NOT EXISTS idx_learning_goals_project ON learning_goals(project_id);
        CREATE INDEX IF NOT EXISTS idx_learning_goals_status ON learning_goals(status);
        CREATE INDEX IF NOT EXISTS idx_learning_goals_user ON learning_goals(user_id);

        CREATE TABLE IF NOT EXISTS learning_topics (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            goal_id TEXT REFERENCES learning_goals(id) ON DELETE SET NULL,
            project_id TEXT,
            status TEXT NOT NULL DEFAULT 'not_started',
            progress_percent REAL DEFAULT 0.0,
            source_type TEXT DEFAULT 'manual',
            source_reference TEXT,
            lesson_plan_id TEXT,
            difficulty_level TEXT DEFAULT 'intermediate',
            estimated_hours REAL,
            actual_hours REAL DEFAULT 0.0,
            started_at TEXT,
            completed_at TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now')),
            tags TEXT DEFAULT '[]',
            metadata TEXT DEFAULT '{}'
        );
        CREATE INDEX IF NOT EXISTS idx_learning_topics_goal ON learning_topics(goal_id);
        CREATE INDEX IF NOT EXISTS idx_learning_topics_project ON learning_topics(project_id);
        CREATE INDEX IF NOT EXISTS idx_learning_topics_status ON learning_topics(status);
        CREATE INDEX IF NOT EXISTS idx_learning_topics_source ON learning_topics(source_type);

        CREATE TABLE IF NOT EXISTS lesson_plans (
            id TEXT PRIMARY KEY,
            topic_id TEXT NOT NULL REFERENCES learning_topics(id) ON DELETE CASCADE,
            title TEXT NOT NULL,
            overview TEXT,
            objectives TEXT,
            prerequisites TEXT,
            generated_by TEXT,
            generation_prompt TEXT,
            generation_config TEXT,
            status TEXT DEFAULT 'draft',
            version INTEGER DEFAULT 1,
            total_sections INTEGER DEFAULT 0,
            completed_sections INTEGER DEFAULT 0,
            estimated_duration_minutes INTEGER,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now')),
            metadata TEXT DEFAULT '{}'
        );
        CREATE INDEX IF NOT EXISTS idx_lesson_plans_topic ON lesson_plans(topic_id);
        CREATE INDEX IF NOT EXISTS idx_lesson_plans_status ON lesson_plans(status);

        CREATE TABLE IF NOT EXISTS lesson_plan_sections (
            id TEXT PRIMARY KEY,
            lesson_plan_id TEXT NOT NULL REFERENCES lesson_plans(id) ON DELETE CASCADE,
            title TEXT NOT NULL,
            content TEXT,
            summary TEXT,
            section_order INTEGER NOT NULL DEFAULT 0,
            parent_section_id TEXT REFERENCES lesson_plan_sections(id) ON DELETE CASCADE,
            section_type TEXT DEFAULT 'content',
            is_completed BOOLEAN DEFAULT FALSE,
            completed_at TEXT,
            estimated_minutes INTEGER,
            actual_minutes INTEGER,
            resources TEXT DEFAULT '[]',
            exercises TEXT DEFAULT '[]',
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now')),
            metadata TEXT DEFAULT '{}'
        );
        CREATE INDEX IF NOT EXISTS idx_lesson_sections_plan ON lesson_plan_sections(lesson_plan_id);
        CREATE INDEX IF NOT EXISTS idx_lesson_sections_order ON lesson_plan_sections(lesson_plan_id, section_order);
        CREATE INDEX IF NOT EXISTS idx_lesson_sections_parent ON lesson_plan_sections(parent_section_id);

        CREATE TABLE IF NOT EXISTS learning_annotations (
            id TEXT PRIMARY KEY,
            resource_type TEXT NOT NULL,
            resource_id TEXT NOT NULL,
            content TEXT NOT NULL,
            annotation_type TEXT NOT NULL DEFAULT 'note',
            position TEXT,
            role TEXT,
            user_id TEXT,
            is_private BOOLEAN DEFAULT TRUE,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now')),
            tags TEXT DEFAULT '[]',
            metadata TEXT DEFAULT '{}'
        );
        CREATE INDEX IF NOT EXISTS idx_learning_annotations_resource ON learning_annotations(resource_type, resource_id);
        CREATE INDEX IF NOT EXISTS idx_learning_annotations_type ON learning_annotations(annotation_type);
        CREATE INDEX IF NOT EXISTS idx_learning_annotations_user ON learning_annotations(user_id);

        CREATE TABLE IF NOT EXISTS learning_evaluations (
            id TEXT PRIMARY KEY,
            topic_id TEXT REFERENCES learning_topics(id) ON DELETE SET NULL,
            lesson_plan_id TEXT REFERENCES lesson_plans(id) ON DELETE SET NULL,
            section_id TEXT REFERENCES lesson_plan_sections(id) ON DELETE SET NULL,
            evaluation_type TEXT DEFAULT 'comprehension',
            question TEXT NOT NULL,
            user_response TEXT NOT NULL,
            score REAL,
            grade TEXT,
            feedback TEXT,
            evaluation_result TEXT,
            evaluated_by TEXT,
            evaluation_prompt TEXT,
            status TEXT DEFAULT 'pending',
            submitted_at TEXT NOT NULL DEFAULT (datetime('now')),
            evaluated_at TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            user_id TEXT,
            metadata TEXT DEFAULT '{}'
        );
        CREATE INDEX IF NOT EXISTS idx_learning_evaluations_topic ON learning_evaluations(topic_id);
        CREATE INDEX IF NOT EXISTS idx_learning_evaluations_plan ON learning_evaluations(lesson_plan_id);
        CREATE INDEX IF NOT EXISTS idx_learning_evaluations_user ON learning_evaluations(user_id);
        CREATE INDEX IF NOT EXISTS idx_learning_evaluations_status ON learning_evaluations(status);

        CREATE TABLE IF NOT EXISTS learning_artifacts (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            file_path TEXT,
            file_type TEXT,
            file_size INTEGER,
            original_filename TEXT,
            source_url TEXT,
            extracted_text TEXT,
            summary TEXT,
            vector_collection TEXT,
            chunk_count INTEGER DEFAULT 0,
            topic_id TEXT REFERENCES learning_topics(id) ON DELETE SET NULL,
            goal_id TEXT REFERENCES learning_goals(id) ON DELETE SET NULL,
            project_id TEXT,
            processing_status TEXT DEFAULT 'pending',
            processing_error TEXT,
            uploaded_by TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now')),
            processed_at TEXT,
            tags TEXT DEFAULT '[]',
            metadata TEXT DEFAULT '{}'
        );
        CREATE INDEX IF NOT EXISTS idx_learning_artifacts_topic ON learning_artifacts(topic_id);
        CREATE INDEX IF NOT EXISTS idx_learning_artifacts_goal ON learning_artifacts(goal_id);
        CREATE INDEX IF NOT EXISTS idx_learning_artifacts_project ON learning_artifacts(project_id);
        CREATE INDEX IF NOT EXISTS idx_learning_artifacts_status ON learning_artifacts(processing_status);

        CREATE TABLE IF NOT EXISTS learning_chat_sessions (
            id TEXT PRIMARY KEY,
            topic_id TEXT REFERENCES learning_topics(id) ON DELETE CASCADE,
            lesson_plan_id TEXT REFERENCES lesson_plans(id) ON DELETE SET NULL,
            section_id TEXT REFERENCES lesson_plan_sections(id) ON DELETE SET NULL,
            title TEXT,
            system_prompt TEXT,
            model TEXT,
            message_count INTEGER DEFAULT 0,
            status TEXT DEFAULT 'active',
            user_id TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now')),
            last_message_at TEXT,
            metadata TEXT DEFAULT '{}'
        );
        CREATE INDEX IF NOT EXISTS idx_learning_chat_sessions_topic ON learning_chat_sessions(topic_id);
        CREATE INDEX IF NOT EXISTS idx_learning_chat_sessions_user ON learning_chat_sessions(user_id);

        CREATE TABLE IF NOT EXISTS learning_progress_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_type TEXT NOT NULL,
            entity_id TEXT NOT NULL,
            progress_percent REAL,
            status TEXT,
            completed_items INTEGER,
            total_items INTEGER,
            time_spent_minutes INTEGER,
            snapshot_at TEXT NOT NULL DEFAULT (datetime('now')),
            user_id TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_learning_progress_entity ON learning_progress_snapshots(entity_type, entity_id);
        CREATE INDEX IF NOT EXISTS idx_learning_progress_time ON learning_progress_snapshots(snapshot_at);
    """)


def _get_db_connection():
    """Get database connection - uses existing app database."""
    global _tables_initialized
    import sqlite3
    from agentic_assistants.config import AgenticConfig
    
    config = AgenticConfig()
    db_path = config.data_dir / "agentic.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    if not _tables_initialized:
        _init_learning_tables(conn)
        _tables_initialized = True
    return conn


def _row_to_dict(row) -> Dict[str, Any]:
    """Convert a sqlite Row to a dictionary."""
    if row is None:
        return None
    return dict(row)


def _parse_json_field(value: str, default=None):
    """Parse a JSON field from the database."""
    if value is None:
        return default if default is not None else {}
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return default if default is not None else {}


# ============================================================================
# Learning Goals Endpoints
# ============================================================================

@router.get("/goals", response_model=Dict[str, Any])
async def list_learning_goals(
    level: Optional[str] = None,
    project_id: Optional[str] = None,
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    """List learning goals with optional filters."""
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Build query
        query = "SELECT * FROM learning_goals WHERE 1=1"
        params = []
        
        if level:
            query += " AND level = ?"
            params.append(level)
        if project_id:
            query += " AND project_id = ?"
            params.append(project_id)
        if status:
            query += " AND status = ?"
            params.append(status)
        
        # Count total
        count_query = query.replace("SELECT *", "SELECT COUNT(*)")
        cursor.execute(count_query, params)
        total = cursor.fetchone()[0]
        
        # Get paginated results
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, (page - 1) * limit])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        goals = []
        for row in rows:
            goal = _row_to_dict(row)
            goal["tags"] = _parse_json_field(goal.get("tags"), [])
            goal["metadata"] = _parse_json_field(goal.get("metadata"), {})
            goals.append(goal)
        
        return {
            "items": goals,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit,
        }
    finally:
        conn.close()


@router.post("/goals", response_model=LearningGoal)
async def create_learning_goal(goal: LearningGoalCreate):
    """Create a new learning goal."""
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        
        goal_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        cursor.execute(
            """
            INSERT INTO learning_goals (
                id, title, description, level, project_id, priority,
                target_date, status, progress_percent, tags, metadata,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                goal_id,
                goal.title,
                goal.description,
                goal.level,
                goal.project_id,
                goal.priority,
                goal.target_date,
                "active",
                0.0,
                json.dumps(goal.tags),
                json.dumps(goal.metadata),
                now,
                now,
            ),
        )
        conn.commit()
        
        # Fetch the created goal
        cursor.execute("SELECT * FROM learning_goals WHERE id = ?", (goal_id,))
        row = cursor.fetchone()
        result = _row_to_dict(row)
        result["tags"] = _parse_json_field(result.get("tags"), [])
        result["metadata"] = _parse_json_field(result.get("metadata"), {})
        
        return result
    finally:
        conn.close()


@router.get("/goals/{goal_id}", response_model=LearningGoal)
async def get_learning_goal(goal_id: str):
    """Get a specific learning goal."""
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM learning_goals WHERE id = ?", (goal_id,))
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Learning goal not found")
        
        result = _row_to_dict(row)
        result["tags"] = _parse_json_field(result.get("tags"), [])
        result["metadata"] = _parse_json_field(result.get("metadata"), {})
        
        return result
    finally:
        conn.close()


@router.put("/goals/{goal_id}", response_model=LearningGoal)
async def update_learning_goal(goal_id: str, goal: LearningGoalUpdate):
    """Update a learning goal."""
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Check if goal exists
        cursor.execute("SELECT * FROM learning_goals WHERE id = ?", (goal_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Learning goal not found")
        
        # Build update query
        updates = []
        params = []
        
        if goal.title is not None:
            updates.append("title = ?")
            params.append(goal.title)
        if goal.description is not None:
            updates.append("description = ?")
            params.append(goal.description)
        if goal.status is not None:
            updates.append("status = ?")
            params.append(goal.status)
            if goal.status == "completed":
                updates.append("completed_at = ?")
                params.append(datetime.utcnow().isoformat())
        if goal.priority is not None:
            updates.append("priority = ?")
            params.append(goal.priority)
        if goal.target_date is not None:
            updates.append("target_date = ?")
            params.append(goal.target_date)
        if goal.progress_percent is not None:
            updates.append("progress_percent = ?")
            params.append(goal.progress_percent)
        if goal.tags is not None:
            updates.append("tags = ?")
            params.append(json.dumps(goal.tags))
        if goal.metadata is not None:
            updates.append("metadata = ?")
            params.append(json.dumps(goal.metadata))
        
        if updates:
            updates.append("updated_at = ?")
            params.append(datetime.utcnow().isoformat())
            params.append(goal_id)
            
            cursor.execute(
                f"UPDATE learning_goals SET {', '.join(updates)} WHERE id = ?",
                params,
            )
            conn.commit()
        
        # Fetch updated goal
        cursor.execute("SELECT * FROM learning_goals WHERE id = ?", (goal_id,))
        row = cursor.fetchone()
        result = _row_to_dict(row)
        result["tags"] = _parse_json_field(result.get("tags"), [])
        result["metadata"] = _parse_json_field(result.get("metadata"), {})
        
        return result
    finally:
        conn.close()


@router.delete("/goals/{goal_id}")
async def delete_learning_goal(goal_id: str):
    """Delete a learning goal."""
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM learning_goals WHERE id = ?", (goal_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Learning goal not found")
        
        cursor.execute("DELETE FROM learning_goals WHERE id = ?", (goal_id,))
        conn.commit()
        
        return {"status": "deleted", "id": goal_id}
    finally:
        conn.close()


# ============================================================================
# Learning Topics Endpoints
# ============================================================================

@router.get("/topics", response_model=Dict[str, Any])
async def list_learning_topics(
    goal_id: Optional[str] = None,
    project_id: Optional[str] = None,
    status: Optional[str] = None,
    source_type: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    """List learning topics with optional filters."""
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        
        query = "SELECT * FROM learning_topics WHERE 1=1"
        params = []
        
        if goal_id:
            query += " AND goal_id = ?"
            params.append(goal_id)
        if project_id:
            query += " AND project_id = ?"
            params.append(project_id)
        if status:
            query += " AND status = ?"
            params.append(status)
        if source_type:
            query += " AND source_type = ?"
            params.append(source_type)
        
        # Count total
        count_query = query.replace("SELECT *", "SELECT COUNT(*)")
        cursor.execute(count_query, params)
        total = cursor.fetchone()[0]
        
        # Get paginated results
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, (page - 1) * limit])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        topics = []
        for row in rows:
            topic = _row_to_dict(row)
            topic["tags"] = _parse_json_field(topic.get("tags"), [])
            topic["metadata"] = _parse_json_field(topic.get("metadata"), {})
            topics.append(topic)
        
        return {
            "items": topics,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit,
        }
    finally:
        conn.close()


@router.post("/topics", response_model=LearningTopic)
async def create_learning_topic(topic: LearningTopicCreate):
    """Create a new learning topic."""
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        
        topic_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        cursor.execute(
            """
            INSERT INTO learning_topics (
                id, name, description, goal_id, project_id, status,
                progress_percent, source_type, source_reference,
                difficulty_level, estimated_hours, actual_hours,
                tags, metadata, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                topic_id,
                topic.name,
                topic.description,
                topic.goal_id,
                topic.project_id,
                "not_started",
                0.0,
                topic.source_type,
                topic.source_reference,
                topic.difficulty_level,
                topic.estimated_hours,
                0.0,
                json.dumps(topic.tags),
                json.dumps(topic.metadata),
                now,
                now,
            ),
        )
        conn.commit()
        
        cursor.execute("SELECT * FROM learning_topics WHERE id = ?", (topic_id,))
        row = cursor.fetchone()
        result = _row_to_dict(row)
        result["tags"] = _parse_json_field(result.get("tags"), [])
        result["metadata"] = _parse_json_field(result.get("metadata"), {})
        
        return result
    finally:
        conn.close()


@router.get("/topics/{topic_id}", response_model=LearningTopic)
async def get_learning_topic(topic_id: str):
    """Get a specific learning topic."""
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM learning_topics WHERE id = ?", (topic_id,))
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Learning topic not found")
        
        result = _row_to_dict(row)
        result["tags"] = _parse_json_field(result.get("tags"), [])
        result["metadata"] = _parse_json_field(result.get("metadata"), {})
        
        return result
    finally:
        conn.close()


@router.put("/topics/{topic_id}", response_model=LearningTopic)
async def update_learning_topic(topic_id: str, topic: LearningTopicUpdate):
    """Update a learning topic."""
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM learning_topics WHERE id = ?", (topic_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Learning topic not found")
        
        updates = []
        params = []
        
        if topic.name is not None:
            updates.append("name = ?")
            params.append(topic.name)
        if topic.description is not None:
            updates.append("description = ?")
            params.append(topic.description)
        if topic.goal_id is not None:
            updates.append("goal_id = ?")
            params.append(topic.goal_id)
        if topic.status is not None:
            updates.append("status = ?")
            params.append(topic.status)
            if topic.status == "in_progress":
                updates.append("started_at = COALESCE(started_at, ?)")
                params.append(datetime.utcnow().isoformat())
            elif topic.status == "completed":
                updates.append("completed_at = ?")
                params.append(datetime.utcnow().isoformat())
        if topic.progress_percent is not None:
            updates.append("progress_percent = ?")
            params.append(topic.progress_percent)
        if topic.difficulty_level is not None:
            updates.append("difficulty_level = ?")
            params.append(topic.difficulty_level)
        if topic.estimated_hours is not None:
            updates.append("estimated_hours = ?")
            params.append(topic.estimated_hours)
        if topic.actual_hours is not None:
            updates.append("actual_hours = ?")
            params.append(topic.actual_hours)
        if topic.tags is not None:
            updates.append("tags = ?")
            params.append(json.dumps(topic.tags))
        if topic.metadata is not None:
            updates.append("metadata = ?")
            params.append(json.dumps(topic.metadata))
        
        if updates:
            updates.append("updated_at = ?")
            params.append(datetime.utcnow().isoformat())
            params.append(topic_id)
            
            cursor.execute(
                f"UPDATE learning_topics SET {', '.join(updates)} WHERE id = ?",
                params,
            )
            conn.commit()
        
        cursor.execute("SELECT * FROM learning_topics WHERE id = ?", (topic_id,))
        row = cursor.fetchone()
        result = _row_to_dict(row)
        result["tags"] = _parse_json_field(result.get("tags"), [])
        result["metadata"] = _parse_json_field(result.get("metadata"), {})
        
        return result
    finally:
        conn.close()


@router.delete("/topics/{topic_id}")
async def delete_learning_topic(topic_id: str):
    """Delete a learning topic."""
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM learning_topics WHERE id = ?", (topic_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Learning topic not found")
        
        cursor.execute("DELETE FROM learning_topics WHERE id = ?", (topic_id,))
        conn.commit()
        
        return {"status": "deleted", "id": topic_id}
    finally:
        conn.close()


# ============================================================================
# Lesson Plan Generation & Management
# ============================================================================

@router.post("/topics/{topic_id}/generate-plan", response_model=LessonPlan)
async def generate_lesson_plan(topic_id: str, request: GeneratePlanRequest):
    """Generate a lesson plan for a topic using Ollama."""
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Get the topic
        cursor.execute("SELECT * FROM learning_topics WHERE id = ?", (topic_id,))
        topic_row = cursor.fetchone()
        if not topic_row:
            raise HTTPException(status_code=404, detail="Learning topic not found")
        
        topic = _row_to_dict(topic_row)
        
        # Import and use lesson planner agent
        try:
            from agentic_assistants.agents.lesson_planner import LessonPlannerAgent
            
            planner = LessonPlannerAgent(model=request.model)
            plan_data = planner.generate_plan(
                topic_name=topic["name"],
                topic_description=topic.get("description", ""),
                difficulty_level=topic.get("difficulty_level", "intermediate"),
                additional_context=request.additional_context,
                include_exercises=request.include_exercises,
                include_resources=request.include_resources,
            )
        except ImportError:
            # Fallback to basic plan generation
            logger.warning("LessonPlannerAgent not available, using basic generation")
            plan_data = _generate_basic_plan(topic)
        
        # Create lesson plan in database
        plan_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        cursor.execute(
            """
            INSERT INTO lesson_plans (
                id, topic_id, title, overview, objectives, prerequisites,
                generated_by, generation_prompt, status, version,
                total_sections, completed_sections, estimated_duration_minutes,
                created_at, updated_at, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                plan_id,
                topic_id,
                plan_data.get("title", f"Lesson Plan: {topic['name']}"),
                plan_data.get("overview", ""),
                json.dumps(plan_data.get("objectives", [])),
                json.dumps(plan_data.get("prerequisites", [])),
                request.model or "llama3.2",
                plan_data.get("generation_prompt", ""),
                "draft",
                1,
                len(plan_data.get("sections", [])),
                0,
                plan_data.get("estimated_duration_minutes"),
                now,
                now,
                json.dumps({}),
            ),
        )
        
        # Create sections
        sections = []
        for idx, section_data in enumerate(plan_data.get("sections", [])):
            section_id = str(uuid.uuid4())
            cursor.execute(
                """
                INSERT INTO lesson_plan_sections (
                    id, lesson_plan_id, title, content, summary,
                    section_order, section_type, is_completed,
                    estimated_minutes, resources, exercises,
                    created_at, updated_at, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    section_id,
                    plan_id,
                    section_data.get("title", f"Section {idx + 1}"),
                    section_data.get("content", ""),
                    section_data.get("summary", ""),
                    idx,
                    section_data.get("section_type", "content"),
                    False,
                    section_data.get("estimated_minutes"),
                    json.dumps(section_data.get("resources", [])),
                    json.dumps(section_data.get("exercises", [])),
                    now,
                    now,
                    json.dumps({}),
                ),
            )
            sections.append({
                "id": section_id,
                "title": section_data.get("title", f"Section {idx + 1}"),
                "content": section_data.get("content", ""),
                "summary": section_data.get("summary", ""),
                "section_order": idx,
                "section_type": section_data.get("section_type", "content"),
                "is_completed": False,
                "estimated_minutes": section_data.get("estimated_minutes"),
                "resources": section_data.get("resources", []),
                "exercises": section_data.get("exercises", []),
                "created_at": now,
                "updated_at": now,
                "metadata": {},
            })
        
        # Update topic with lesson plan reference
        cursor.execute(
            "UPDATE learning_topics SET lesson_plan_id = ?, updated_at = ? WHERE id = ?",
            (plan_id, now, topic_id),
        )
        
        conn.commit()
        
        return {
            "id": plan_id,
            "topic_id": topic_id,
            "title": plan_data.get("title", f"Lesson Plan: {topic['name']}"),
            "overview": plan_data.get("overview", ""),
            "objectives": plan_data.get("objectives", []),
            "prerequisites": plan_data.get("prerequisites", []),
            "generated_by": request.model or "llama3.2",
            "status": "draft",
            "version": 1,
            "total_sections": len(sections),
            "completed_sections": 0,
            "estimated_duration_minutes": plan_data.get("estimated_duration_minutes"),
            "created_at": now,
            "updated_at": now,
            "metadata": {},
            "sections": sections,
        }
    finally:
        conn.close()


def _generate_basic_plan(topic: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a basic lesson plan structure without LLM."""
    return {
        "title": f"Lesson Plan: {topic['name']}",
        "overview": f"A comprehensive guide to learning {topic['name']}.",
        "objectives": [
            f"Understand the fundamentals of {topic['name']}",
            "Apply concepts through practical exercises",
            "Evaluate understanding through self-assessment",
        ],
        "prerequisites": [],
        "sections": [
            {
                "title": "Introduction",
                "content": f"Introduction to {topic['name']}",
                "section_type": "content",
                "estimated_minutes": 15,
            },
            {
                "title": "Core Concepts",
                "content": f"Key concepts and principles of {topic['name']}",
                "section_type": "content",
                "estimated_minutes": 30,
            },
            {
                "title": "Practical Exercises",
                "content": "Hands-on exercises to reinforce learning",
                "section_type": "exercise",
                "estimated_minutes": 45,
            },
            {
                "title": "Summary & Review",
                "content": "Review of key takeaways",
                "section_type": "content",
                "estimated_minutes": 10,
            },
        ],
        "estimated_duration_minutes": 100,
    }


@router.get("/plans/{plan_id}", response_model=LessonPlan)
async def get_lesson_plan(plan_id: str):
    """Get a lesson plan with its sections."""
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM lesson_plans WHERE id = ?", (plan_id,))
        plan_row = cursor.fetchone()
        if not plan_row:
            raise HTTPException(status_code=404, detail="Lesson plan not found")
        
        plan = _row_to_dict(plan_row)
        plan["objectives"] = _parse_json_field(plan.get("objectives"), [])
        plan["prerequisites"] = _parse_json_field(plan.get("prerequisites"), [])
        plan["metadata"] = _parse_json_field(plan.get("metadata"), {})
        
        # Get sections
        cursor.execute(
            "SELECT * FROM lesson_plan_sections WHERE lesson_plan_id = ? ORDER BY section_order",
            (plan_id,),
        )
        section_rows = cursor.fetchall()
        
        sections = []
        for row in section_rows:
            section = _row_to_dict(row)
            section["resources"] = _parse_json_field(section.get("resources"), [])
            section["exercises"] = _parse_json_field(section.get("exercises"), [])
            section["metadata"] = _parse_json_field(section.get("metadata"), {})
            sections.append(section)
        
        plan["sections"] = sections
        
        return plan
    finally:
        conn.close()


@router.put("/plans/{plan_id}/sections/{section_id}")
async def update_lesson_section(plan_id: str, section_id: str, request: SectionUpdateRequest):
    """Update a lesson plan section (e.g., mark as completed)."""
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Verify section exists and belongs to plan
        cursor.execute(
            "SELECT * FROM lesson_plan_sections WHERE id = ? AND lesson_plan_id = ?",
            (section_id, plan_id),
        )
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Section not found")
        
        updates = []
        params = []
        
        if request.is_completed is not None:
            updates.append("is_completed = ?")
            params.append(request.is_completed)
            if request.is_completed:
                updates.append("completed_at = ?")
                params.append(datetime.utcnow().isoformat())
        if request.actual_minutes is not None:
            updates.append("actual_minutes = ?")
            params.append(request.actual_minutes)
        if request.content is not None:
            updates.append("content = ?")
            params.append(request.content)
        if request.metadata is not None:
            updates.append("metadata = ?")
            params.append(json.dumps(request.metadata))
        
        if updates:
            updates.append("updated_at = ?")
            params.append(datetime.utcnow().isoformat())
            params.extend([section_id, plan_id])
            
            cursor.execute(
                f"UPDATE lesson_plan_sections SET {', '.join(updates)} WHERE id = ? AND lesson_plan_id = ?",
                params,
            )
            
            # Update completed_sections count in lesson_plans
            cursor.execute(
                """
                UPDATE lesson_plans 
                SET completed_sections = (
                    SELECT COUNT(*) FROM lesson_plan_sections 
                    WHERE lesson_plan_id = ? AND is_completed = 1
                ),
                updated_at = ?
                WHERE id = ?
                """,
                (plan_id, datetime.utcnow().isoformat(), plan_id),
            )
            
            conn.commit()
        
        # Return updated section
        cursor.execute(
            "SELECT * FROM lesson_plan_sections WHERE id = ?",
            (section_id,),
        )
        row = cursor.fetchone()
        result = _row_to_dict(row)
        result["resources"] = _parse_json_field(result.get("resources"), [])
        result["exercises"] = _parse_json_field(result.get("exercises"), [])
        result["metadata"] = _parse_json_field(result.get("metadata"), {})
        
        return result
    finally:
        conn.close()


# ============================================================================
# Paper Import
# ============================================================================

@router.post("/import/paper", response_model=ImportPaperResponse)
async def import_paper(
    file: Optional[UploadFile] = File(None),
    url: Optional[str] = Form(None),
    title: Optional[str] = Form(None),
    goal_id: Optional[str] = Form(None),
    project_id: Optional[str] = Form(None),
    auto_generate_plans: bool = Form(False),
):
    """Import a research paper and extract learning topics."""
    if not file and not url:
        raise HTTPException(
            status_code=400,
            detail="Either file or URL must be provided",
        )
    
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        
        artifact_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        # Process file or URL
        extracted_text = ""
        file_path = None
        file_type = None
        original_filename = None
        
        if file:
            # Save uploaded file
            from agentic_assistants.config import AgenticConfig
            config = AgenticConfig()
            
            artifacts_dir = config.data_dir / "learning_artifacts"
            artifacts_dir.mkdir(parents=True, exist_ok=True)
            
            original_filename = file.filename
            file_type = file.content_type or "application/octet-stream"
            file_path = str(artifacts_dir / f"{artifact_id}_{original_filename}")
            
            content = await file.read()
            with open(file_path, "wb") as f:
                f.write(content)
            
            # Extract text based on file type
            if file_type == "application/pdf" or original_filename.endswith(".pdf"):
                try:
                    import pypdf
                    reader = pypdf.PdfReader(file_path)
                    extracted_text = "\n".join(
                        page.extract_text() for page in reader.pages
                    )
                except ImportError:
                    logger.warning("pypdf not available for PDF extraction")
                    extracted_text = "[PDF content - extraction not available]"
            else:
                # Assume text file
                extracted_text = content.decode("utf-8", errors="ignore")
        
        elif url:
            # Fetch content from URL
            import httpx
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(url, follow_redirects=True)
                    extracted_text = response.text
                    file_type = "url"
            except Exception as e:
                logger.error(f"Failed to fetch URL: {e}")
                raise HTTPException(status_code=400, detail=f"Failed to fetch URL: {e}")
        
        # Extract topics using paper parser agent
        extracted_topics = []
        summary = None
        
        try:
            from agentic_assistants.agents.paper_parser import PaperParserAgent
            
            parser = PaperParserAgent()
            result = parser.parse(
                text=extracted_text,
                title=title or original_filename,
            )
            extracted_topics = result.get("topics", [])
            summary = result.get("summary")
        except ImportError:
            logger.warning("PaperParserAgent not available, using basic extraction")
            # Basic topic extraction fallback
            extracted_topics = [
                {
                    "name": title or "Imported Topic",
                    "description": summary or "Topic extracted from imported paper",
                    "confidence": 0.5,
                }
            ]
            summary = extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text
        
        # Save artifact to database
        cursor.execute(
            """
            INSERT INTO learning_artifacts (
                id, name, description, file_path, file_type, original_filename,
                source_url, extracted_text, summary, goal_id, project_id,
                processing_status, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                artifact_id,
                title or original_filename or "Imported Paper",
                f"Imported from {'file' if file else 'URL'}",
                file_path,
                file_type,
                original_filename,
                url,
                extracted_text[:50000] if extracted_text else None,  # Limit stored text
                summary,
                goal_id,
                project_id,
                "completed",
                now,
                now,
            ),
        )
        
        # Create topics if auto_generate_plans is enabled
        if auto_generate_plans:
            for topic_data in extracted_topics:
                topic_id = str(uuid.uuid4())
                cursor.execute(
                    """
                    INSERT INTO learning_topics (
                        id, name, description, goal_id, project_id, status,
                        progress_percent, source_type, source_reference,
                        difficulty_level, tags, metadata, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        topic_id,
                        topic_data.get("name", "Extracted Topic"),
                        topic_data.get("description", ""),
                        goal_id,
                        project_id,
                        "not_started",
                        0.0,
                        "paper",
                        artifact_id,
                        topic_data.get("difficulty", "intermediate"),
                        json.dumps([]),
                        json.dumps({"artifact_id": artifact_id}),
                        now,
                        now,
                    ),
                )
                topic_data["id"] = topic_id
        
        conn.commit()
        
        return {
            "artifact_id": artifact_id,
            "extracted_topics": extracted_topics,
            "summary": summary,
            "status": "completed",
        }
    finally:
        conn.close()


# ============================================================================
# Learning Chat
# ============================================================================

@router.post("/chat", response_model=LearningChatResponse)
async def learning_chat(request: LearningChatRequest):
    """Interactive chat about a learning topic."""
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Get topic
        cursor.execute("SELECT * FROM learning_topics WHERE id = ?", (request.topic_id,))
        topic_row = cursor.fetchone()
        if not topic_row:
            raise HTTPException(status_code=404, detail="Learning topic not found")
        
        topic = _row_to_dict(topic_row)
        
        # Get lesson plan context if available and requested
        topic_context = None
        if request.include_lesson_context and topic.get("lesson_plan_id"):
            cursor.execute(
                "SELECT * FROM lesson_plans WHERE id = ?",
                (topic["lesson_plan_id"],),
            )
            plan_row = cursor.fetchone()
            if plan_row:
                plan = _row_to_dict(plan_row)
                topic_context = f"Topic: {topic['name']}\nOverview: {plan.get('overview', '')}"
        
        # Get or create chat session
        session_id = request.session_id
        if not session_id:
            session_id = str(uuid.uuid4())
            cursor.execute(
                """
                INSERT INTO learning_chat_sessions (
                    id, topic_id, lesson_plan_id, title, status, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session_id,
                    request.topic_id,
                    topic.get("lesson_plan_id"),
                    f"Chat: {topic['name']}",
                    "active",
                    datetime.utcnow().isoformat(),
                    datetime.utcnow().isoformat(),
                ),
            )
        
        # Store user message as annotation
        user_annotation_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        cursor.execute(
            """
            INSERT INTO learning_annotations (
                id, resource_type, resource_id, content, annotation_type,
                role, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_annotation_id,
                "chat_session",
                session_id,
                request.message,
                "chat",
                "user",
                now,
                now,
            ),
        )
        
        # Generate response using Ollama
        try:
            from agentic_assistants.core.ollama import OllamaManager
            
            ollama = OllamaManager()
            
            system_prompt = f"""You are a helpful learning assistant helping the user understand the topic: {topic['name']}.
{f'Context: {topic_context}' if topic_context else ''}

Provide clear, educational responses. Use examples when helpful. If the user seems confused, 
offer to break down concepts further or provide alternative explanations."""
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.message},
            ]
            
            response = ollama.chat(messages=messages)
            assistant_message = response.get("message", {}).get("content", "I'm sorry, I couldn't generate a response.")
        except Exception as e:
            logger.error(f"Ollama chat failed: {e}")
            assistant_message = "I'm having trouble connecting to the language model. Please try again later."
        
        # Store assistant response
        assistant_annotation_id = str(uuid.uuid4())
        cursor.execute(
            """
            INSERT INTO learning_annotations (
                id, resource_type, resource_id, content, annotation_type,
                role, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                assistant_annotation_id,
                "chat_session",
                session_id,
                assistant_message,
                "chat",
                "assistant",
                now,
                now,
            ),
        )
        
        # Update session message count
        cursor.execute(
            """
            UPDATE learning_chat_sessions 
            SET message_count = message_count + 2, last_message_at = ?, updated_at = ?
            WHERE id = ?
            """,
            (now, now, session_id),
        )
        
        conn.commit()
        
        return {
            "session_id": session_id,
            "message": {"role": "assistant", "content": assistant_message},
            "topic_context": topic_context,
        }
    finally:
        conn.close()


# ============================================================================
# Annotations Endpoints
# ============================================================================

@router.get("/annotations", response_model=Dict[str, Any])
async def list_annotations(
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    annotation_type: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
):
    """List learning annotations with optional filters."""
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        
        query = "SELECT * FROM learning_annotations WHERE 1=1"
        params = []
        
        if resource_type:
            query += " AND resource_type = ?"
            params.append(resource_type)
        if resource_id:
            query += " AND resource_id = ?"
            params.append(resource_id)
        if annotation_type:
            query += " AND annotation_type = ?"
            params.append(annotation_type)
        
        # Count total
        count_query = query.replace("SELECT *", "SELECT COUNT(*)")
        cursor.execute(count_query, params)
        total = cursor.fetchone()[0]
        
        # Get paginated results
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, (page - 1) * limit])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        annotations = []
        for row in rows:
            annotation = _row_to_dict(row)
            annotation["position"] = _parse_json_field(annotation.get("position"))
            annotation["tags"] = _parse_json_field(annotation.get("tags"), [])
            annotation["metadata"] = _parse_json_field(annotation.get("metadata"), {})
            annotations.append(annotation)
        
        return {
            "items": annotations,
            "total": total,
            "page": page,
            "limit": limit,
        }
    finally:
        conn.close()


@router.post("/annotations", response_model=LearningAnnotation)
async def create_annotation(annotation: LearningAnnotationCreate):
    """Create a learning annotation."""
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        
        annotation_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        cursor.execute(
            """
            INSERT INTO learning_annotations (
                id, resource_type, resource_id, content, annotation_type,
                position, is_private, tags, metadata, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                annotation_id,
                annotation.resource_type,
                annotation.resource_id,
                annotation.content,
                annotation.annotation_type,
                json.dumps(annotation.position) if annotation.position else None,
                True,
                json.dumps(annotation.tags),
                json.dumps(annotation.metadata),
                now,
                now,
            ),
        )
        conn.commit()
        
        cursor.execute("SELECT * FROM learning_annotations WHERE id = ?", (annotation_id,))
        row = cursor.fetchone()
        result = _row_to_dict(row)
        result["position"] = _parse_json_field(result.get("position"))
        result["tags"] = _parse_json_field(result.get("tags"), [])
        result["metadata"] = _parse_json_field(result.get("metadata"), {})
        
        return result
    finally:
        conn.close()


@router.delete("/annotations/{annotation_id}")
async def delete_annotation(annotation_id: str):
    """Delete a learning annotation."""
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM learning_annotations WHERE id = ?", (annotation_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Annotation not found")
        
        cursor.execute("DELETE FROM learning_annotations WHERE id = ?", (annotation_id,))
        conn.commit()
        
        return {"status": "deleted", "id": annotation_id}
    finally:
        conn.close()


# ============================================================================
# Learning Artifacts Endpoints
# ============================================================================

@router.get("/artifacts", response_model=Dict[str, Any])
async def list_artifacts(
    topic_id: Optional[str] = None,
    goal_id: Optional[str] = None,
    project_id: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    """List learning artifacts."""
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        
        query = "SELECT * FROM learning_artifacts WHERE 1=1"
        params = []
        
        if topic_id:
            query += " AND topic_id = ?"
            params.append(topic_id)
        if goal_id:
            query += " AND goal_id = ?"
            params.append(goal_id)
        if project_id:
            query += " AND project_id = ?"
            params.append(project_id)
        
        count_query = query.replace("SELECT *", "SELECT COUNT(*)")
        cursor.execute(count_query, params)
        total = cursor.fetchone()[0]
        
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, (page - 1) * limit])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        artifacts = []
        for row in rows:
            artifact = _row_to_dict(row)
            artifact["tags"] = _parse_json_field(artifact.get("tags"), [])
            artifact["metadata"] = _parse_json_field(artifact.get("metadata"), {})
            # Don't include full extracted_text in list view
            if artifact.get("extracted_text"):
                artifact["extracted_text"] = artifact["extracted_text"][:200] + "..."
            artifacts.append(artifact)
        
        return {
            "items": artifacts,
            "total": total,
            "page": page,
            "limit": limit,
        }
    finally:
        conn.close()


@router.get("/artifacts/{artifact_id}")
async def get_artifact(artifact_id: str):
    """Get a specific artifact."""
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM learning_artifacts WHERE id = ?", (artifact_id,))
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Artifact not found")
        
        result = _row_to_dict(row)
        result["tags"] = _parse_json_field(result.get("tags"), [])
        result["metadata"] = _parse_json_field(result.get("metadata"), {})
        
        return result
    finally:
        conn.close()


@router.delete("/artifacts/{artifact_id}")
async def delete_artifact(artifact_id: str):
    """Delete an artifact."""
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM learning_artifacts WHERE id = ?", (artifact_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Artifact not found")
        
        artifact = _row_to_dict(row)
        
        # Delete file if exists
        if artifact.get("file_path"):
            import os
            try:
                os.remove(artifact["file_path"])
            except OSError:
                pass
        
        cursor.execute("DELETE FROM learning_artifacts WHERE id = ?", (artifact_id,))
        conn.commit()
        
        return {"status": "deleted", "id": artifact_id}
    finally:
        conn.close()
