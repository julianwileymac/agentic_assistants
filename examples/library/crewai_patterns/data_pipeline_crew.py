# requires: crewai pydantic
"""CrewAI ETL-style data pipeline crew.

Demonstrates:
- Data collection, transformation, validation agents
- Task dependencies for ETL pipeline
- Structured data quality report
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout

from pydantic import BaseModel, Field

_KICKOFF_TIMEOUT_SEC = 90


class DataQualityReport(BaseModel):
    records_processed: int = 0
    records_valid: int = 0
    records_invalid: int = 0
    quality_score: float = Field(ge=0, le=1, default=0)
    issues_found: list[str] = Field(default_factory=list)
    transformations_applied: list[str] = Field(default_factory=list)


def create_data_pipeline_crew():
    try:
        from crewai import Agent, Crew, Task, Process

        collector = Agent(
            role="Data Collector",
            goal="Gather and extract data from specified sources",
            backstory="Data engineer specialized in multi-source data extraction.",
        )

        transformer = Agent(
            role="Data Transformer",
            goal="Clean, normalize, and transform raw data",
            backstory="ETL specialist who ensures data consistency and quality.",
        )

        validator = Agent(
            role="Data Validator",
            goal="Validate transformed data against business rules",
            backstory="Quality assurance analyst ensuring data integrity.",
        )

        collect_task = Task(
            description="Collect data from source: {source}. Extract relevant records.",
            expected_output="Raw extracted records with metadata.",
            agent=collector,
        )

        transform_task = Task(
            description="Clean and transform the collected data. Normalize formats.",
            expected_output="Transformed dataset with applied transformations log.",
            agent=transformer,
        )

        validate_task = Task(
            description="Validate the transformed data. Report quality metrics.",
            expected_output="Data quality report with validation results.",
            agent=validator,
            output_json=DataQualityReport,
        )

        crew = Crew(
            agents=[collector, transformer, validator],
            tasks=[collect_task, transform_task, validate_task],
            process=Process.sequential,
        )

        print("Data pipeline crew: Collector -> Transformer -> Validator")
        return crew

    except ImportError:
        print("Install crewai: pip install crewai")
        return None


def _print_crew_structure(crew) -> None:
    print("\n--- Agent roles ---")
    for agent in crew.agents:
        print(f"  Role: {agent.role}")
        print(f"    Goal: {agent.goal}")
    print("\n--- Tasks (description & expected output) ---")
    for i, task in enumerate(crew.tasks, 1):
        agent_role = getattr(task.agent, "role", "?")
        print(f"  Task {i} (agent: {agent_role})")
        print(f"    Description: {task.description}")
        print(f"    Expected output: {task.expected_output}")


def main() -> None:
    crew = create_data_pipeline_crew()
    if crew is None:
        return
    _print_crew_structure(crew)
    print("\n--- Attempting crew.kickoff() ---")
    print(f"(Aborting after {_KICKOFF_TIMEOUT_SEC}s if the run does not return.)")
    try:
        with ThreadPoolExecutor(max_workers=1) as pool:
            fut = pool.submit(
                crew.kickoff,
                inputs={"source": "s3://example-bucket/customers/year=2024/*.parquet"},
            )
            result = fut.result(timeout=_KICKOFF_TIMEOUT_SEC)
        print("Kickoff finished successfully.")
        print(result)
    except FuturesTimeout:
        print(
            f"Kickoff timed out after {_KICKOFF_TIMEOUT_SEC}s (slow or unreachable LLM)."
        )
        print(
            "With a responsive LLM, the crew would simulate an ETL narrative: collect from "
            "the source, transform, then return a DataQualityReport (Pydantic)."
        )
    except Exception as exc:
        print(
            "Kickoff could not run. Typical causes: no LLM API key, provider misconfiguration, "
            "or environment limits."
        )
        print(f"Error type: {type(exc).__name__}: {exc}")
        print(
            "With a working LLM, the crew would simulate an ETL narrative: collect from the source, "
            "transform, then return a DataQualityReport (Pydantic)."
        )


if __name__ == "__main__":
    main()
