"""
Evaluations API Router for Agentic Assistants.

Provides endpoints for:
- Creating and managing learning evaluations
- Submitting responses for grading
- Viewing evaluation history and analytics
"""

import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/evaluations", tags=["evaluations"])


# ============================================================================
# Pydantic Models
# ============================================================================

class EvaluationCreate(BaseModel):
    """Create a new evaluation."""
    topic_id: Optional[str] = None
    lesson_plan_id: Optional[str] = None
    section_id: Optional[str] = None
    evaluation_type: str = "comprehension"  # comprehension, application, synthesis, quiz
    question: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class EvaluationSubmit(BaseModel):
    """Submit a response for evaluation."""
    evaluation_id: str
    user_response: str
    model: Optional[str] = None  # Model to use for evaluation


class EvaluationResponse(BaseModel):
    """Evaluation response model."""
    id: str
    topic_id: Optional[str] = None
    lesson_plan_id: Optional[str] = None
    section_id: Optional[str] = None
    evaluation_type: str
    question: str
    user_response: Optional[str] = None
    score: Optional[float] = None
    grade: Optional[str] = None
    feedback: Optional[str] = None
    evaluation_result: Optional[Dict[str, Any]] = None
    evaluated_by: Optional[str] = None
    status: str
    submitted_at: str
    evaluated_at: Optional[str] = None
    created_at: str
    user_id: Optional[str] = None
    metadata: Dict[str, Any]


class QuizQuestion(BaseModel):
    """A quiz question."""
    id: str
    question: str
    question_type: str  # multiple_choice, short_answer, true_false
    options: Optional[List[str]] = None  # For multiple choice
    correct_answer: Optional[str] = None  # For auto-grading
    points: int = 1
    explanation: Optional[str] = None


class QuizCreate(BaseModel):
    """Create a quiz for a topic/section."""
    topic_id: Optional[str] = None
    lesson_plan_id: Optional[str] = None
    section_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    questions: List[QuizQuestion] = Field(default_factory=list)
    time_limit_minutes: Optional[int] = None
    passing_score: float = 70.0


class QuizSubmission(BaseModel):
    """Submit quiz answers."""
    quiz_id: str
    answers: Dict[str, str]  # question_id -> answer


class EvaluationStats(BaseModel):
    """Evaluation statistics."""
    total_evaluations: int
    completed_evaluations: int
    average_score: Optional[float] = None
    highest_score: Optional[float] = None
    lowest_score: Optional[float] = None
    evaluations_by_type: Dict[str, int]
    recent_evaluations: List[Dict[str, Any]]


# ============================================================================
# Database Helper Functions
# ============================================================================

def _get_db_connection():
    """Get database connection."""
    import sqlite3
    from agentic_assistants.config import AgenticConfig
    
    config = AgenticConfig()
    db_path = config.workspace_path / "data" / "agentic.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
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
# Evaluation Endpoints
# ============================================================================

@router.get("", response_model=Dict[str, Any])
async def list_evaluations(
    topic_id: Optional[str] = None,
    lesson_plan_id: Optional[str] = None,
    evaluation_type: Optional[str] = None,
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    """List evaluations with optional filters."""
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        
        query = "SELECT * FROM learning_evaluations WHERE 1=1"
        params = []
        
        if topic_id:
            query += " AND topic_id = ?"
            params.append(topic_id)
        if lesson_plan_id:
            query += " AND lesson_plan_id = ?"
            params.append(lesson_plan_id)
        if evaluation_type:
            query += " AND evaluation_type = ?"
            params.append(evaluation_type)
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
        
        evaluations = []
        for row in rows:
            evaluation = _row_to_dict(row)
            evaluation["evaluation_result"] = _parse_json_field(
                evaluation.get("evaluation_result")
            )
            evaluation["metadata"] = _parse_json_field(evaluation.get("metadata"), {})
            evaluations.append(evaluation)
        
        return {
            "items": evaluations,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit,
        }
    finally:
        conn.close()


@router.post("", response_model=EvaluationResponse)
async def create_evaluation(evaluation: EvaluationCreate):
    """Create a new evaluation (question for the user to answer)."""
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        
        evaluation_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        cursor.execute(
            """
            INSERT INTO learning_evaluations (
                id, topic_id, lesson_plan_id, section_id, evaluation_type,
                question, status, submitted_at, created_at, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                evaluation_id,
                evaluation.topic_id,
                evaluation.lesson_plan_id,
                evaluation.section_id,
                evaluation.evaluation_type,
                evaluation.question,
                "pending",
                now,
                now,
                json.dumps(evaluation.metadata),
            ),
        )
        conn.commit()
        
        cursor.execute("SELECT * FROM learning_evaluations WHERE id = ?", (evaluation_id,))
        row = cursor.fetchone()
        result = _row_to_dict(row)
        result["evaluation_result"] = _parse_json_field(result.get("evaluation_result"))
        result["metadata"] = _parse_json_field(result.get("metadata"), {})
        
        return result
    finally:
        conn.close()


@router.get("/{evaluation_id}", response_model=EvaluationResponse)
async def get_evaluation(evaluation_id: str):
    """Get a specific evaluation."""
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM learning_evaluations WHERE id = ?", (evaluation_id,))
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Evaluation not found")
        
        result = _row_to_dict(row)
        result["evaluation_result"] = _parse_json_field(result.get("evaluation_result"))
        result["metadata"] = _parse_json_field(result.get("metadata"), {})
        
        return result
    finally:
        conn.close()


@router.post("/submit", response_model=EvaluationResponse)
async def submit_evaluation(submission: EvaluationSubmit):
    """Submit a response for grading."""
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Get the evaluation
        cursor.execute(
            "SELECT * FROM learning_evaluations WHERE id = ?",
            (submission.evaluation_id,),
        )
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Evaluation not found")
        
        evaluation = _row_to_dict(row)
        
        # Get context for grading
        context = ""
        if evaluation.get("topic_id"):
            cursor.execute(
                "SELECT name, description FROM learning_topics WHERE id = ?",
                (evaluation["topic_id"],),
            )
            topic_row = cursor.fetchone()
            if topic_row:
                topic = _row_to_dict(topic_row)
                context += f"Topic: {topic['name']}\n"
                if topic.get("description"):
                    context += f"Description: {topic['description']}\n"
        
        if evaluation.get("lesson_plan_id"):
            cursor.execute(
                "SELECT title, overview, objectives FROM lesson_plans WHERE id = ?",
                (evaluation["lesson_plan_id"],),
            )
            plan_row = cursor.fetchone()
            if plan_row:
                plan = _row_to_dict(plan_row)
                context += f"\nLesson: {plan['title']}\n"
                if plan.get("overview"):
                    context += f"Overview: {plan['overview']}\n"
        
        # Grade the response using evaluation agent
        try:
            from agentic_assistants.agents.evaluation_agent import EvaluationAgent
            
            agent = EvaluationAgent(model=submission.model)
            result = agent.evaluate(
                question=evaluation["question"],
                response=submission.user_response,
                evaluation_type=evaluation["evaluation_type"],
                context=context,
            )
            
            score = result.get("score", 0)
            grade = result.get("grade", "N/A")
            feedback = result.get("feedback", "")
            evaluation_result = result
            evaluated_by = submission.model or "llama3.2"
        except ImportError:
            logger.warning("EvaluationAgent not available, using basic grading")
            # Basic grading fallback
            score = 70.0 if len(submission.user_response) > 50 else 50.0
            grade = "B" if score >= 70 else "C"
            feedback = "Response recorded. Detailed feedback requires the evaluation agent."
            evaluation_result = {"basic_grading": True}
            evaluated_by = "basic"
        except Exception as e:
            logger.error(f"Evaluation failed: {e}")
            score = None
            grade = None
            feedback = "Evaluation could not be completed. Please try again."
            evaluation_result = {"error": str(e)}
            evaluated_by = None
        
        # Update evaluation in database
        now = datetime.utcnow().isoformat()
        cursor.execute(
            """
            UPDATE learning_evaluations SET
                user_response = ?,
                score = ?,
                grade = ?,
                feedback = ?,
                evaluation_result = ?,
                evaluated_by = ?,
                evaluated_at = ?,
                status = ?
            WHERE id = ?
            """,
            (
                submission.user_response,
                score,
                grade,
                feedback,
                json.dumps(evaluation_result),
                evaluated_by,
                now,
                "completed" if score is not None else "failed",
                submission.evaluation_id,
            ),
        )
        conn.commit()
        
        # Fetch updated evaluation
        cursor.execute(
            "SELECT * FROM learning_evaluations WHERE id = ?",
            (submission.evaluation_id,),
        )
        row = cursor.fetchone()
        result = _row_to_dict(row)
        result["evaluation_result"] = _parse_json_field(result.get("evaluation_result"))
        result["metadata"] = _parse_json_field(result.get("metadata"), {})
        
        return result
    finally:
        conn.close()


@router.get("/history/stats", response_model=EvaluationStats)
async def get_evaluation_stats(
    topic_id: Optional[str] = None,
    user_id: Optional[str] = None,
):
    """Get evaluation statistics."""
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Build base query
        base_where = "WHERE 1=1"
        params = []
        if topic_id:
            base_where += " AND topic_id = ?"
            params.append(topic_id)
        if user_id:
            base_where += " AND user_id = ?"
            params.append(user_id)
        
        # Total evaluations
        cursor.execute(
            f"SELECT COUNT(*) FROM learning_evaluations {base_where}",
            params,
        )
        total_evaluations = cursor.fetchone()[0]
        
        # Completed evaluations
        cursor.execute(
            f"SELECT COUNT(*) FROM learning_evaluations {base_where} AND status = 'completed'",
            params,
        )
        completed_evaluations = cursor.fetchone()[0]
        
        # Score statistics
        cursor.execute(
            f"""
            SELECT AVG(score), MAX(score), MIN(score) 
            FROM learning_evaluations {base_where} AND score IS NOT NULL
            """,
            params,
        )
        score_row = cursor.fetchone()
        average_score = score_row[0]
        highest_score = score_row[1]
        lowest_score = score_row[2]
        
        # Evaluations by type
        cursor.execute(
            f"""
            SELECT evaluation_type, COUNT(*) 
            FROM learning_evaluations {base_where}
            GROUP BY evaluation_type
            """,
            params,
        )
        type_rows = cursor.fetchall()
        evaluations_by_type = {row[0]: row[1] for row in type_rows}
        
        # Recent evaluations
        cursor.execute(
            f"""
            SELECT id, question, score, grade, status, created_at, evaluation_type
            FROM learning_evaluations {base_where}
            ORDER BY created_at DESC LIMIT 10
            """,
            params,
        )
        recent_rows = cursor.fetchall()
        recent_evaluations = [
            {
                "id": row[0],
                "question": row[1][:100] + "..." if len(row[1]) > 100 else row[1],
                "score": row[2],
                "grade": row[3],
                "status": row[4],
                "created_at": row[5],
                "evaluation_type": row[6],
            }
            for row in recent_rows
        ]
        
        return {
            "total_evaluations": total_evaluations,
            "completed_evaluations": completed_evaluations,
            "average_score": average_score,
            "highest_score": highest_score,
            "lowest_score": lowest_score,
            "evaluations_by_type": evaluations_by_type,
            "recent_evaluations": recent_evaluations,
        }
    finally:
        conn.close()


@router.delete("/{evaluation_id}")
async def delete_evaluation(evaluation_id: str):
    """Delete an evaluation."""
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM learning_evaluations WHERE id = ?",
            (evaluation_id,),
        )
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Evaluation not found")
        
        cursor.execute(
            "DELETE FROM learning_evaluations WHERE id = ?",
            (evaluation_id,),
        )
        conn.commit()
        
        return {"status": "deleted", "id": evaluation_id}
    finally:
        conn.close()


# ============================================================================
# Quiz Endpoints
# ============================================================================

@router.post("/quiz/generate")
async def generate_quiz(
    topic_id: Optional[str] = None,
    lesson_plan_id: Optional[str] = None,
    section_id: Optional[str] = None,
    num_questions: int = Query(5, ge=1, le=20),
    question_types: List[str] = Query(["multiple_choice", "short_answer"]),
    model: Optional[str] = None,
):
    """Generate a quiz for a topic or lesson section using LLM."""
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Get context
        context = ""
        title = "Quiz"
        
        if topic_id:
            cursor.execute(
                "SELECT name, description FROM learning_topics WHERE id = ?",
                (topic_id,),
            )
            topic_row = cursor.fetchone()
            if topic_row:
                topic = _row_to_dict(topic_row)
                context += f"Topic: {topic['name']}\n{topic.get('description', '')}\n"
                title = f"Quiz: {topic['name']}"
        
        if lesson_plan_id:
            cursor.execute(
                "SELECT title, overview, objectives FROM lesson_plans WHERE id = ?",
                (lesson_plan_id,),
            )
            plan_row = cursor.fetchone()
            if plan_row:
                plan = _row_to_dict(plan_row)
                context += f"\nLesson: {plan['title']}\n{plan.get('overview', '')}\n"
                objectives = _parse_json_field(plan.get("objectives"), [])
                if objectives:
                    context += f"Objectives: {', '.join(objectives)}\n"
        
        if section_id:
            cursor.execute(
                "SELECT title, content, summary FROM lesson_plan_sections WHERE id = ?",
                (section_id,),
            )
            section_row = cursor.fetchone()
            if section_row:
                section = _row_to_dict(section_row)
                context += f"\nSection: {section['title']}\n{section.get('content', '')}\n"
        
        if not context:
            raise HTTPException(
                status_code=400,
                detail="At least one of topic_id, lesson_plan_id, or section_id is required",
            )
        
        # Generate quiz questions using LLM
        try:
            from agentic_assistants.core.ollama import OllamaManager
            
            ollama = OllamaManager()
            
            prompt = f"""Generate {num_questions} quiz questions based on the following content.
            
{context}

Question types to include: {', '.join(question_types)}

Return the questions in JSON format with this structure:
{{
    "questions": [
        {{
            "id": "q1",
            "question": "Question text",
            "question_type": "multiple_choice",
            "options": ["A", "B", "C", "D"],  // only for multiple_choice
            "correct_answer": "A",
            "points": 1,
            "explanation": "Why this is the correct answer"
        }}
    ]
}}

Make questions that test understanding, not just memorization. Include a mix of difficulty levels."""

            messages = [
                {"role": "system", "content": "You are an educational assessment expert. Generate clear, fair quiz questions."},
                {"role": "user", "content": prompt},
            ]
            
            response = ollama.chat(messages=messages, model=model)
            response_text = response.get("message", {}).get("content", "")
            
            # Parse JSON from response
            import re
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                quiz_data = json.loads(json_match.group())
                questions = quiz_data.get("questions", [])
            else:
                questions = []
        except Exception as e:
            logger.error(f"Quiz generation failed: {e}")
            # Fallback to basic questions
            questions = [
                {
                    "id": f"q{i+1}",
                    "question": f"Sample question {i+1} about the topic",
                    "question_type": "short_answer",
                    "points": 1,
                }
                for i in range(min(num_questions, 3))
            ]
        
        return {
            "title": title,
            "topic_id": topic_id,
            "lesson_plan_id": lesson_plan_id,
            "section_id": section_id,
            "questions": questions,
            "total_points": sum(q.get("points", 1) for q in questions),
        }
    finally:
        conn.close()


@router.post("/quiz/grade")
async def grade_quiz(submission: QuizSubmission):
    """Grade a quiz submission."""
    # For now, this creates individual evaluations for each question
    # In a full implementation, you'd have a quiz table and track the whole quiz
    
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        
        results = []
        total_score = 0
        total_points = 0
        
        for question_id, answer in submission.answers.items():
            # Create an evaluation for this question
            evaluation_id = str(uuid.uuid4())
            now = datetime.utcnow().isoformat()
            
            # We'd need the actual question data here - for now, store basic info
            cursor.execute(
                """
                INSERT INTO learning_evaluations (
                    id, evaluation_type, question, user_response,
                    status, submitted_at, created_at, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    evaluation_id,
                    "quiz",
                    f"Quiz question {question_id}",
                    answer,
                    "completed",
                    now,
                    now,
                    json.dumps({"quiz_id": submission.quiz_id, "question_id": question_id}),
                ),
            )
            
            # For demo purposes, assign a score
            # In production, you'd check against correct answers or use LLM grading
            points = 1
            earned = 1 if len(answer) > 10 else 0.5
            total_points += points
            total_score += earned
            
            results.append({
                "question_id": question_id,
                "points_earned": earned,
                "points_possible": points,
            })
        
        conn.commit()
        
        percentage = (total_score / total_points * 100) if total_points > 0 else 0
        
        return {
            "quiz_id": submission.quiz_id,
            "results": results,
            "total_score": total_score,
            "total_points": total_points,
            "percentage": percentage,
            "grade": _score_to_grade(percentage),
            "passed": percentage >= 70,
        }
    finally:
        conn.close()


def _score_to_grade(score: float) -> str:
    """Convert a percentage score to a letter grade."""
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"


# ============================================================================
# Evaluation Generation
# ============================================================================

@router.post("/generate")
async def generate_evaluation_questions(
    topic_id: Optional[str] = None,
    lesson_plan_id: Optional[str] = None,
    section_id: Optional[str] = None,
    evaluation_type: str = "comprehension",
    num_questions: int = Query(3, ge=1, le=10),
    model: Optional[str] = None,
):
    """Generate evaluation questions for a topic or section."""
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Build context
        context = ""
        
        if topic_id:
            cursor.execute(
                "SELECT name, description FROM learning_topics WHERE id = ?",
                (topic_id,),
            )
            row = cursor.fetchone()
            if row:
                topic = _row_to_dict(row)
                context += f"Topic: {topic['name']}\n{topic.get('description', '')}\n"
        
        if section_id:
            cursor.execute(
                "SELECT title, content FROM lesson_plan_sections WHERE id = ?",
                (section_id,),
            )
            row = cursor.fetchone()
            if row:
                section = _row_to_dict(row)
                context += f"\nSection: {section['title']}\n{section.get('content', '')}\n"
        
        if not context:
            raise HTTPException(
                status_code=400,
                detail="At least one of topic_id or section_id is required",
            )
        
        # Generate questions using LLM
        try:
            from agentic_assistants.core.ollama import OllamaManager
            
            ollama = OllamaManager()
            
            type_descriptions = {
                "comprehension": "Test understanding of concepts and facts",
                "application": "Test ability to apply concepts to new situations",
                "synthesis": "Test ability to combine ideas and create new understanding",
                "analysis": "Test ability to break down and examine components",
            }
            
            prompt = f"""Generate {num_questions} {evaluation_type} evaluation questions.
            
Type: {evaluation_type} - {type_descriptions.get(evaluation_type, 'General assessment')}

Content to evaluate:
{context}

Return questions as a JSON array:
[
    {{"question": "Question text", "expected_depth": "What a good answer should include"}}
]

Make questions open-ended and thought-provoking."""

            messages = [
                {"role": "system", "content": "You are an expert educator creating assessment questions."},
                {"role": "user", "content": prompt},
            ]
            
            response = ollama.chat(messages=messages, model=model)
            response_text = response.get("message", {}).get("content", "")
            
            # Parse JSON
            import re
            json_match = re.search(r'\[[\s\S]*\]', response_text)
            if json_match:
                questions = json.loads(json_match.group())
            else:
                questions = []
        except Exception as e:
            logger.error(f"Question generation failed: {e}")
            questions = [
                {"question": f"Explain the key concepts of this topic.", "expected_depth": "Cover main ideas"}
            ]
        
        # Create evaluations in database
        created_evaluations = []
        now = datetime.utcnow().isoformat()
        
        for q in questions:
            evaluation_id = str(uuid.uuid4())
            cursor.execute(
                """
                INSERT INTO learning_evaluations (
                    id, topic_id, lesson_plan_id, section_id, evaluation_type,
                    question, status, submitted_at, created_at, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    evaluation_id,
                    topic_id,
                    lesson_plan_id,
                    section_id,
                    evaluation_type,
                    q.get("question", ""),
                    "pending",
                    now,
                    now,
                    json.dumps({"expected_depth": q.get("expected_depth", "")}),
                ),
            )
            created_evaluations.append({
                "id": evaluation_id,
                "question": q.get("question", ""),
                "evaluation_type": evaluation_type,
                "status": "pending",
            })
        
        conn.commit()
        
        return {
            "evaluations": created_evaluations,
            "count": len(created_evaluations),
            "topic_id": topic_id,
            "section_id": section_id,
        }
    finally:
        conn.close()
