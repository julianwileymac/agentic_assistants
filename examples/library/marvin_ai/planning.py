# requires: marvin pydantic openai
"""Marvin task decomposition and planning.

Demonstrates:
- Breaking complex objectives into subtasks
- Each subtask modeled with Pydantic
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class SubTask(BaseModel):
    title: str
    description: str
    estimated_hours: float = Field(ge=0, default=1.0)
    priority: int = Field(ge=1, le=5, default=3)
    dependencies: list[str] = Field(default_factory=list)


class ProjectPlan(BaseModel):
    objective: str
    subtasks: list[SubTask] = Field(default_factory=list)
    total_estimated_hours: float = 0.0
    risk_factors: list[str] = Field(default_factory=list)


def _offline_example_plan() -> ProjectPlan:
    return ProjectPlan(
        objective="REST todo API with auth, persistence, and Kubernetes deployment",
        subtasks=[
            SubTask(
                title="Auth and API skeleton",
                description="JWT or OAuth2 login; FastAPI routes; OpenAPI docs",
                estimated_hours=12.0,
                priority=1,
                dependencies=[],
            ),
            SubTask(
                title="Database layer",
                description="Models, migrations, CRUD for todos",
                estimated_hours=10.0,
                priority=2,
                dependencies=["Auth and API skeleton"],
            ),
            SubTask(
                title="Deploy to Kubernetes",
                description="Docker image, Helm or manifests, health checks",
                estimated_hours=8.0,
                priority=3,
                dependencies=["Database layer"],
            ),
        ],
        total_estimated_hours=30.0,
        risk_factors=["Secret management", "DB backup strategy"],
    )


def demo_planning():
    """Decompose an objective with marvin.cast -> ProjectPlan."""
    try:
        import marvin
    except ImportError:
        print("Install: pip install marvin openai")
        print()
        print("Marvin can decompose complex objectives into structured plans.")
        print("Schema:", ProjectPlan.model_json_schema())
        return

    objective = (
        "Build a REST API for a todo application with authentication, "
        "database storage, and deployment to Kubernetes"
    )
    print(f"Trying marvin.cast(..., target=ProjectPlan) for:\n  {objective!r}\n")
    try:
        plan = marvin.cast(objective, target=ProjectPlan)
        print(f"Plan objective: {plan.objective}")
        print(f"Total hours (model): {plan.total_estimated_hours}")
        for task in plan.subtasks:
            print(f"  [{task.priority}] {task.title} ({task.estimated_hours}h)")
        if plan.risk_factors:
            print("Risks:", plan.risk_factors)
    except Exception as exc:
        print(f"Cast failed ({type(exc).__name__}: {exc}).")
        print(
            "With OPENAI_API_KEY and a working provider, Marvin would infer subtasks "
            "matching the ProjectPlan schema."
        )
        print("\nPrinted offline example plan:")
        ex = _offline_example_plan()
        print(f"  Objective: {ex.objective}")
        for task in ex.subtasks:
            print(f"  [{task.priority}] {task.title} ({task.estimated_hours}h)")


def main() -> None:
    """Decompose an objective via marvin.cast -> ProjectPlan (or print offline plan)."""
    demo_planning()


if __name__ == "__main__":
    main()
