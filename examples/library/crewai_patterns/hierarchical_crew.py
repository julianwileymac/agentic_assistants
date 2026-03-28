# requires: crewai pydantic
"""CrewAI hierarchical process with manager agent delegation.

Demonstrates:
- Process.hierarchical for manager-driven delegation
- Manager agent that coordinates specialists
- Complex multi-step workflows
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout

_KICKOFF_TIMEOUT_SEC = 90


def create_hierarchical_crew():
    try:
        from crewai import Agent, Crew, Task, Process

        manager = Agent(
            role="Project Manager",
            goal="Coordinate the team to deliver a complete project plan",
            backstory="Experienced PM who delegates effectively to specialists.",
            allow_delegation=True,
        )

        architect = Agent(
            role="Solutions Architect",
            goal="Design the technical architecture",
            backstory="Senior architect with cloud and microservices expertise.",
        )

        developer = Agent(
            role="Lead Developer",
            goal="Implement the core functionality",
            backstory="Full-stack developer with extensive Python experience.",
        )

        qa_engineer = Agent(
            role="QA Engineer",
            goal="Define testing strategy and quality gates",
            backstory="QA expert focused on test automation and coverage.",
        )

        planning_task = Task(
            description="Create a comprehensive project plan for: {project_description}",
            expected_output="Project plan with architecture, implementation steps, and testing strategy.",
            agent=manager,
        )

        crew = Crew(
            agents=[manager, architect, developer, qa_engineer],
            tasks=[planning_task],
            process=Process.hierarchical,
            manager_agent=manager,
            verbose=True,
        )

        print("Hierarchical crew created:")
        print("  Manager: Project Manager (delegates to team)")
        print("  Team: Solutions Architect, Lead Developer, QA Engineer")
        print("  Process: hierarchical")
        return crew

    except ImportError:
        print("Install crewai: pip install crewai")
        return None


def _print_crew_structure(crew) -> None:
    print("\n--- Agent roles ---")
    for agent in crew.agents:
        print(f"  Role: {agent.role}")
        print(f"    Goal: {agent.goal}")
        deleg = getattr(agent, "allow_delegation", None)
        if deleg is not None:
            print(f"    allow_delegation: {deleg}")
    print("\n--- Tasks (description & expected output) ---")
    for i, task in enumerate(crew.tasks, 1):
        agent_role = getattr(task.agent, "role", "?")
        print(f"  Task {i} (agent: {agent_role})")
        print(f"    Description: {task.description}")
        print(f"    Expected output: {task.expected_output}")
    print("\n--- Process ---")
    print("  Hierarchical: the manager delegates sub-steps to architect, developer, and QA.")


def main() -> None:
    crew = create_hierarchical_crew()
    if crew is None:
        return
    _print_crew_structure(crew)
    print("\n--- Attempting crew.kickoff() ---")
    print(f"(Aborting after {_KICKOFF_TIMEOUT_SEC}s if the run does not return.)")
    try:
        with ThreadPoolExecutor(max_workers=1) as pool:
            fut = pool.submit(
                crew.kickoff,
                inputs={
                    "project_description": (
                        "Customer-facing analytics dashboard with real-time charts, "
                        "role-based access, and export to CSV."
                    ),
                },
            )
            result = fut.result(timeout=_KICKOFF_TIMEOUT_SEC)
        print("Kickoff finished successfully.")
        print(result)
    except FuturesTimeout:
        print(
            f"Kickoff timed out after {_KICKOFF_TIMEOUT_SEC}s (hierarchical runs can be slow)."
        )
        print(
            "With a responsive LLM, the manager would coordinate specialists to produce a "
            "consolidated project plan covering architecture, implementation, and QA."
        )
    except Exception as exc:
        print(
            "Kickoff could not run. Hierarchical crews often need a manager-capable LLM and "
            "correct API keys; some setups also require explicit llm= on the Crew or agents."
        )
        print(f"Error type: {type(exc).__name__}: {exc}")
        print(
            "With a working LLM, the manager would coordinate specialists to produce a "
            "consolidated project plan covering architecture, implementation, and QA."
        )


if __name__ == "__main__":
    main()
