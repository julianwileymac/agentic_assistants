# requires: openai
"""OpenAI Swarm: triage agent routes to sales, support, or billing via handoff functions."""

from __future__ import annotations


def main() -> None:
    try:
        from swarm import Agent
    except ImportError:
        print(
            "Install Swarm (uses openai under the hood):\n"
            "  pip install git+https://github.com/openai/swarm.git\n\n"
            "Triage sketch:\n"
            "  sales = Agent(name='sales', instructions='...')\n"
            "  def transfer_to_sales(): return sales\n"
            "  triage = Agent(name='triage', functions=[transfer_to_sales, ...])\n"
        )
        return

    sales_agent = Agent(
        name="SalesAgent",
        instructions="You handle pricing, demos, and upgrades. Be friendly and concise.",
    )
    support_agent = Agent(
        name="SupportAgent",
        instructions="You troubleshoot product issues. Ask clarifying questions.",
    )
    billing_agent = Agent(
        name="BillingAgent",
        instructions="You handle invoices, refunds, and payment failures.",
    )

    def transfer_to_sales() -> Agent:
        """Send the user to the sales specialist."""
        return sales_agent

    def transfer_to_support() -> Agent:
        """Send the user to technical support."""
        return support_agent

    def transfer_to_billing() -> Agent:
        """Send the user to billing."""
        return billing_agent

    triage_agent = Agent(
        name="TriageAgent",
        instructions=(
            "You route the user:\n"
            "- Buying, plans, or demos -> transfer_to_sales\n"
            "- Bugs, errors, 'not working' -> transfer_to_support\n"
            "- Invoices, charges, refunds -> transfer_to_billing\n"
            "Call exactly one transfer function once intent is clear."
        ),
        functions=[transfer_to_sales, transfer_to_support, transfer_to_billing],
    )

    print("=== Swarm — triage routing ===")
    print(f"\nTriage: {triage_agent.name}")
    print("Available handoffs:")
    for fn in triage_agent.functions:
        print(f"  - {fn.__name__}: {fn.__doc__.strip() if fn.__doc__ else ''}")

    print("\nSpecialists:")
    for a in (sales_agent, support_agent, billing_agent):
        print(f"  - {a.name}: {a.instructions[:70]}...")

    print(
        """
--- Routing logic (runtime) ---
1. User message hits TriageAgent first.
2. Model chooses a tool call matching intent (sales / support / billing).
3. The matching function returns the target Agent; Swarm activates it.
4. Only the specialist's instructions are used for the next model turns.

--- Example traces (expected tool choice) ---
  "Can I get a demo?" -> transfer_to_sales
  "The app crashes on launch" -> transfer_to_support
  "I was double charged" -> transfer_to_billing
"""
    )

    scenarios = [
        "I'd like to see pricing for the enterprise tier.",
        "Login fails with error 500 after MFA.",
        "Please refund my last invoice.",
    ]
    print("\n--- Scenario rehearsal (human-readable; no LLM) ---")
    for text in scenarios:
        print(f"  user: {text}")
        if "pricing" in text.lower() or "enterprise" in text.lower():
            target = transfer_to_sales()
        elif "login" in text.lower() or "error" in text.lower():
            target = transfer_to_support()
        elif "refund" in text.lower() or "invoice" in text.lower():
            target = transfer_to_billing()
        else:
            target = triage_agent
        label = target.name if hasattr(target, "name") else repr(target)
        print(f"    -> would hand off to {label}")


if __name__ == "__main__":
    main()
