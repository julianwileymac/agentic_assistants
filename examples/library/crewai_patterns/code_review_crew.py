# requires: crewai pydantic
"""CrewAI code review pipeline with chained agent outputs.

Demonstrates:
- Specialized agents for different review aspects
- Task output chaining
- Structured review reports
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout

from pydantic import BaseModel, Field

_KICKOFF_TIMEOUT_SEC = 90


class CodeIssue(BaseModel):
    file: str = ""
    line: int = 0
    severity: str = "info"
    message: str = ""
    suggestion: str = ""


class CodeReviewReport(BaseModel):
    overall_quality: int = Field(ge=1, le=10, default=5)
    issues: list[CodeIssue] = Field(default_factory=list)
    security_concerns: list[str] = Field(default_factory=list)
    performance_notes: list[str] = Field(default_factory=list)
    summary: str = ""


def create_code_review_crew():
    """Create a code review crew with specialized agents."""
    try:
        from crewai import Agent, Crew, Task, Process

        analyzer = Agent(
            role="Code Analyzer",
            goal="Identify code quality issues, anti-patterns, and bugs",
            backstory="Senior developer with expertise in code quality and best practices.",
            verbose=True,
        )

        security_reviewer = Agent(
            role="Security Reviewer",
            goal="Find security vulnerabilities and suggest mitigations",
            backstory="Application security specialist focused on secure coding.",
            verbose=True,
        )

        report_writer = Agent(
            role="Review Report Writer",
            goal="Compile all findings into a clear, actionable review report",
            backstory="Technical lead who writes clear code review summaries.",
            verbose=True,
        )

        analyze_task = Task(
            description="Analyze the following code for quality issues:\n{code}",
            expected_output="List of code quality issues with severity levels.",
            agent=analyzer,
        )

        security_task = Task(
            description="Review the code for security vulnerabilities.",
            expected_output="List of security concerns with remediation advice.",
            agent=security_reviewer,
        )

        report_task = Task(
            description="Compile all review findings into a structured report.",
            expected_output="Complete code review report.",
            agent=report_writer,
            output_json=CodeReviewReport,
        )

        crew = Crew(
            agents=[analyzer, security_reviewer, report_writer],
            tasks=[analyze_task, security_task, report_task],
            process=Process.sequential,
        )

        print("Code review crew created with 3 agents:")
        print("  1. Code Analyzer - quality issues")
        print("  2. Security Reviewer - vulnerabilities")
        print("  3. Report Writer - structured output")
        return crew

    except ImportError:
        print("Install crewai: pip install crewai")
        return None


_SAMPLE_CODE = '''
def authenticate(user, password):
    query = "SELECT * FROM users WHERE name='" + user + "' AND pass='" + password + "'"
    return db.execute(query)
'''


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
    crew = create_code_review_crew()
    if crew is None:
        return
    _print_crew_structure(crew)
    print("\n--- Attempting crew.kickoff() ---")
    print(f"(Aborting after {_KICKOFF_TIMEOUT_SEC}s if the run does not return.)")
    try:
        with ThreadPoolExecutor(max_workers=1) as pool:
            fut = pool.submit(crew.kickoff, inputs={"code": _SAMPLE_CODE})
            result = fut.result(timeout=_KICKOFF_TIMEOUT_SEC)
        print("Kickoff finished successfully.")
        print(result)
    except FuturesTimeout:
        print(
            f"Kickoff timed out after {_KICKOFF_TIMEOUT_SEC}s (slow or unreachable LLM)."
        )
        print(
            "With a responsive LLM, agents would review the sample code for quality, "
            "security, then emit a structured CodeReviewReport."
        )
    except Exception as exc:
        print(
            "Kickoff could not run. Typical causes: no LLM API key, provider settings, "
            "or missing optional CrewAI tool dependencies."
        )
        print(f"Error type: {type(exc).__name__}: {exc}")
        print(
            "With a working LLM, agents would review the sample code for quality, "
            "security, then emit a structured CodeReviewReport."
        )


if __name__ == "__main__":
    main()
