# requires: crewai pydantic
"""CrewAI multi-agent research crew with structured Pydantic outputs.

Demonstrates:
- Agent creation with roles and goals
- Task chaining with expected_output
- Pydantic output models for structured results
- Sequential process execution
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout

from pydantic import BaseModel, Field

_KICKOFF_TIMEOUT_SEC = 90


class ResearchFinding(BaseModel):
    """Structured research finding."""
    topic: str
    key_insights: list[str] = Field(default_factory=list)
    sources: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1, default=0.5)


class ResearchReport(BaseModel):
    """Complete research report."""
    title: str
    summary: str
    findings: list[ResearchFinding] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    methodology: str = ""


def create_research_crew():
    """Create a multi-agent research crew."""
    try:
        from crewai import Agent, Crew, Task, Process

        researcher = Agent(
            role="Senior Research Analyst",
            goal="Conduct thorough research on the given topic",
            backstory="Expert researcher with 20 years of academic experience.",
            verbose=True,
            allow_delegation=False,
        )

        analyst = Agent(
            role="Data Analyst",
            goal="Analyze research findings and identify patterns",
            backstory="Statistical expert who finds insights in complex data.",
            verbose=True,
            allow_delegation=False,
        )

        writer = Agent(
            role="Report Writer",
            goal="Produce a clear, comprehensive research report",
            backstory="Technical writer who communicates complex ideas simply.",
            verbose=True,
            allow_delegation=False,
        )

        research_task = Task(
            description="Research the topic: {topic}. Gather key findings from multiple angles.",
            expected_output="A list of research findings with sources.",
            agent=researcher,
        )

        analysis_task = Task(
            description="Analyze the research findings. Identify patterns and insights.",
            expected_output="Analytical summary with key insights and recommendations.",
            agent=analyst,
        )

        report_task = Task(
            description="Write a comprehensive research report synthesizing all findings.",
            expected_output="Complete research report with title, summary, findings, and recommendations.",
            agent=writer,
            output_json=ResearchReport,
        )

        crew = Crew(
            agents=[researcher, analyst, writer],
            tasks=[research_task, analysis_task, report_task],
            process=Process.sequential,
            verbose=True,
        )

        print("Research crew created:")
        print(f"  Agents: {[a.role for a in crew.agents]}")
        print(f"  Tasks: {len(crew.tasks)}")
        print(f"  Process: sequential")
        print(f"  Output model: ResearchReport")
        return crew

    except ImportError:
        print("Install crewai: pip install crewai")
        return None


def _print_crew_structure(crew) -> None:
    """Print agent roles, goals, and task descriptions for learning."""
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
    crew = create_research_crew()
    if crew is None:
        return
    _print_crew_structure(crew)
    print("\n--- Attempting crew.kickoff() ---")
    print(f"(Aborting after {_KICKOFF_TIMEOUT_SEC}s if the run does not return.)")
    try:
        with ThreadPoolExecutor(max_workers=1) as pool:
            fut = pool.submit(
                crew.kickoff,
                inputs={"topic": "quantum computing applications in drug discovery"},
            )
            result = fut.result(timeout=_KICKOFF_TIMEOUT_SEC)
        print("Kickoff finished successfully.")
        print(result)
    except FuturesTimeout:
        print(
            f"Kickoff timed out after {_KICKOFF_TIMEOUT_SEC}s (slow or unreachable LLM, "
            "or blocked network)."
        )
        print(
            "With a responsive LLM, this crew would run sequentially: research the topic, "
            "analyze findings, then produce a structured ResearchReport (Pydantic)."
        )
    except Exception as exc:
        print(
            "Kickoff could not run. Typical causes: no LLM API key (e.g. OPENAI_API_KEY), "
            "provider misconfiguration, missing crewai-tools, or network errors."
        )
        print(f"Error type: {type(exc).__name__}: {exc}")
        print(
            "With a working LLM, this crew would run sequentially: research the topic, "
            "analyze findings, then produce a structured ResearchReport (Pydantic)."
        )


if __name__ == "__main__":
    main()
