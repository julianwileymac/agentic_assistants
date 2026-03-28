# requires: crewai
"""CrewAI hierarchical delegation, task context chains, memory, and cross-crew handoff.

Demonstrates:
- Manager with allow_delegation=True and Process.hierarchical
- Task.context dependencies for passing prior outputs
- Crew memory so agents share recalled context within a run
- A second crew pattern that consumes a briefing string (cross-crew collaboration)
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout

_KICKOFF_TIMEOUT_SEC = 90


def _build_primary_crew():
    """Single crew: hierarchical manager + specialists + task DAG via context."""
    from crewai import Agent, Crew, Task, Process

    manager = Agent(
        role="Eng Manager",
        goal="Break down the initiative and delegate to the right specialist",
        backstory="You route work, resolve ambiguities, and merge team output.",
        allow_delegation=True,
        verbose=True,
    )

    architect = Agent(
        role="Staff Architect",
        goal="Produce a concise technical design",
        backstory="Designs APIs, data flows, and non-functional requirements.",
        verbose=True,
        allow_delegation=False,
    )

    engineer = Agent(
        role="Senior Engineer",
        goal="Turn the design into an implementation outline",
        backstory="Writes pragmatic steps, risks, and test hooks.",
        verbose=True,
        allow_delegation=False,
    )

    analyst = Agent(
        role="Product Analyst",
        goal="Define success metrics and rollout checks",
        backstory="Connects user outcomes to measurable signals.",
        verbose=True,
        allow_delegation=False,
    )

    design_task = Task(
        description=(
            "For initiative: {initiative}. Produce a technical design outline "
            "(components, interfaces, data stores)."
        ),
        expected_output="Structured design bullets the engineer can implement against.",
        agent=architect,
    )

    build_task = Task(
        description=(
            "Using the architect's design, propose implementation phases, owners, "
            "and key risks for: {initiative}."
        ),
        expected_output="Phased implementation plan referencing the design decisions.",
        agent=engineer,
        context=[design_task],
    )

    metrics_task = Task(
        description=(
            "From the design and implementation plan, define metrics, launch checks, "
            "and rollback signals for: {initiative}."
        ),
        expected_output="Metric definitions tied to the agreed plan.",
        agent=analyst,
        context=[design_task, build_task],
    )

    orchestrate_task = Task(
        description=(
            "Coordinate the team to deliver a single executive summary for {initiative}, "
            "incorporating design, build plan, and metrics."
        ),
        expected_output="One-page summary with decisions, open questions, and next steps.",
        agent=manager,
        context=[design_task, build_task, metrics_task],
    )

    common = dict(
        agents=[manager, architect, engineer, analyst],
        tasks=[design_task, build_task, metrics_task, orchestrate_task],
        process=Process.hierarchical,
        manager_agent=manager,
        verbose=True,
    )
    try:
        return Crew(**common, memory=True)
    except TypeError:
        return Crew(**common)


def _build_followup_crew():
    """Second crew that expects a prior briefing in inputs (cross-crew handoff)."""
    from crewai import Agent, Crew, Process, Task

    editor = Agent(
        role="Docs Editor",
        goal="Polish the briefing into release notes",
        backstory="Clarifies language and highlights customer impact.",
        verbose=True,
        allow_delegation=False,
    )

    polish_task = Task(
        description=(
            "Rewrite the following technical briefing into customer-facing release notes. "
            "Briefing:\n{briefing}\n"
        ),
        expected_output="Short release notes with highlights and known limitations.",
        agent=editor,
    )

    common = dict(
        agents=[editor],
        tasks=[polish_task],
        process=Process.sequential,
        verbose=True,
    )
    try:
        return Crew(**common, memory=True)
    except TypeError:
        return Crew(**common)


def create_crews():
    try:
        primary = _build_primary_crew()
        followup = _build_followup_crew()
        return primary, followup
    except ImportError:
        print("Install crewai: pip install crewai")
        return None, None


def _print_delegation_overview(primary, followup) -> None:
    print("\n--- Primary crew (hierarchical + shared memory) ---")
    print(f"  Agents: {[a.role for a in primary.agents]}")
    print(f"  Tasks: {len(primary.tasks)} (context edges encode dependencies)")
    for i, t in enumerate(primary.tasks, 1):
        ctx = getattr(t, "context", None) or []
        ctx_n = len(ctx) if ctx else 0
        print(f"    Task {i}: agent={getattr(t.agent, 'role', '?')}  context_from={ctx_n} prior task(s)")
    print(
        "  Memory: Crew(memory=True) when supported — agents recall prior task outputs in-session."
    )

    print("\n--- Cross-crew pattern ---")
    print(
        "  1) primary.kickoff(inputs={'initiative': '...'})  -> save str(result) as briefing."
    )
    print(
        "  2) followup.kickoff(inputs={'briefing': briefing})  -> docs crew without "
        "re-running the technical crew."
    )
    print(f"  Follow-up crew agents: {[a.role for a in followup.agents]}")


def main() -> None:
    primary, followup = create_crews()
    if primary is None or followup is None:
        return

    _print_delegation_overview(primary, followup)

    print("\n--- Attempting primary crew kickoff() ---")
    print(f"(Aborting after {_KICKOFF_TIMEOUT_SEC}s if the run does not return.)")
    try:
        with ThreadPoolExecutor(max_workers=1) as pool:
            fut = pool.submit(
                primary.kickoff,
                inputs={
                    "initiative": (
                        "Add OAuth2 login to the internal analytics dashboard with "
                        "audit logging and per-tenant feature flags."
                    ),
                },
            )
            result = fut.result(timeout=_KICKOFF_TIMEOUT_SEC)
        print("Kickoff finished successfully.")
        print(result)
        briefing = str(result)[:4000]
        print("\n--- Optional second kickoff (cross-crew); truncated briefing in inputs ---")
        with ThreadPoolExecutor(max_workers=1) as pool2:
            fut2 = pool2.submit(followup.kickoff, inputs={"briefing": briefing})
            result2 = fut2.result(timeout=_KICKOFF_TIMEOUT_SEC)
        print(result2)
    except FuturesTimeout:
        print(
            f"Kickoff timed out after {_KICKOFF_TIMEOUT_SEC}s (hierarchical runs can be slow)."
        )
        print(
            "With a responsive LLM, the manager delegates design → build → metrics, then "
            "consolidates; a second crew can consume the saved briefing for release notes."
        )
    except Exception as exc:
        print(
            "Kickoff could not run. Typical causes: missing API keys, manager LLM limits, "
            "or version-specific Crew arguments."
        )
        print(f"Error type: {type(exc).__name__}: {exc}")


if __name__ == "__main__":
    main()
