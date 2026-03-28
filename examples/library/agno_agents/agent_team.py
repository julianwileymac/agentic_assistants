# requires: agno
"""Agno: Team with a leader-style coordinator and worker agents.

Shows delegation-oriented roles; prints team structure without a live model run.
"""

from __future__ import annotations

from typing import Any


def main() -> None:
    try:
        from agno.agent import Agent

        try:
            from agno.team import Team, TeamMode
        except ImportError:
            Team = None  # type: ignore[misc, assignment]
            TeamMode = None  # type: ignore[misc, assignment]
    except ImportError:
        print(
            "Install agno to run this example: pip install agno\n\n"
            "Team sketch:\n"
            "  from agno.team import Team, TeamMode\n"
            "  from agno.agent import Agent\n"
            "  leader = Agent(name='Lead', role='You break work into steps', ...)\n"
            "  worker = Agent(name='Builder', role='You implement', ...)\n"
            "  team = Team(name='Sprint', members=[leader, worker], mode=TeamMode.coordinate)\n"
        )
        return

    if Team is None:
        print("Your agno install does not expose agno.team.Team (check agno version >= 1.x).")
        return

    def estimate_effort(task: str) -> str:
        """Return a fake effort estimate for a task description."""
        return f"estimate: {8 + (len(task) % 5)}h for {task!r}"

    leader = Agent(
        name="team_lead",
        role="You delegate: split goals into concrete subtasks for specialists.",
        description="Coordinates workers and merges their outputs.",
        instructions=[
            "Assign research vs implementation clearly.",
            "Ask for one deliverable per worker turn.",
        ],
        tools=[estimate_effort],
        model=None,
    )

    researcher = Agent(
        name="research_worker",
        role="You produce bullet-point findings and risks.",
        description="Gathers context; no external browsing in this demo.",
        instructions=["Cite assumptions explicitly.", "Keep under 5 bullets."],
        model=None,
    )

    builder = Agent(
        name="builder_worker",
        role="You draft code or pseudocode to satisfy the task.",
        description="Implements from the research brief.",
        instructions=["Prefer small functions.", "Include a usage example."],
        model=None,
    )

    mode = TeamMode.coordinate if TeamMode else None
    team_kwargs: dict[str, Any] = {
        "name": "delivery_team",
        "members": [leader, researcher, builder],
        "description": "Leader delegates research and implementation work.",
    }
    if mode is not None:
        team_kwargs["mode"] = mode

    team = Team(**team_kwargs)

    print("=== Agno — multi-agent team ===")
    print(f"\nTeam name: {getattr(team, 'name', 'n/a')}")
    if mode is not None:
        print(f"TeamMode: {mode}")

    print("\nMembers (name / role / tools):")
    for m in team.members:
        tlen = len(getattr(m, "tools", []) or [])
        print(f"  • {m.name}: role={getattr(m, 'role', '')!r} | tools={tlen}")

    print(
        """
--- Task delegation pattern ---
1. User sends a goal to the Team run API (e.g. team.run(...)).
2. The leader agent's instructions bias it toward splitting work.
3. Team mode (e.g. coordinate / route / broadcast) decides how member agents participate.
4. Workers focus on narrow roles; leader synthesizes or assigns follow-ups.

--- Live execution ---
  Assign real models on each Agent (e.g. OpenAIChat) then:
    response = team.run("Ship a read-only /health JSON endpoint spec.")
  Inspect response.messages or the team's debug output depending on version.
"""
    )

    print("\n--- Direct tool demo (leader tool, no team run) ---")
    print(estimate_effort("add OAuth2 to API"))


if __name__ == "__main__":
    main()
