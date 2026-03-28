# requires: logfire
"""Logfire LLM observability: tracing AI calls, token usage, latency.

Demonstrates:
- Wrapping LLM calls in Logfire spans
- Token usage tracking
- Latency measurement and cost estimation
"""

from __future__ import annotations

import time


def demo_llm_observability():
    try:
        import logfire

        logfire.configure(send_to_logfire=False)

        def mock_llm_call(prompt: str, model: str) -> dict:
            """Simulate an LLM API call."""
            time.sleep(0.1)
            return {
                "content": f"Response to: {prompt[:50]}",
                "model": model,
                "usage": {"prompt_tokens": 50, "completion_tokens": 100, "total_tokens": 150},
            }

        with logfire.span("llm-pipeline", pipeline="qa-chain"):
            with logfire.span("llm-call", model="gpt-4o", prompt_length=50) as span:
                result = mock_llm_call("What is Python?", "gpt-4o")
                usage = result["usage"]
                logfire.info(
                    "LLM response received",
                    model=result["model"],
                    prompt_tokens=usage["prompt_tokens"],
                    completion_tokens=usage["completion_tokens"],
                    total_tokens=usage["total_tokens"],
                    estimated_cost_usd=usage["total_tokens"] * 0.00003,
                )

        print("LLM Observability with Logfire:")
        print(f"  Model: {result['model']}")
        print(f"  Tokens: {usage['total_tokens']}")
        print(f"  Est. cost: ${usage['total_tokens'] * 0.00003:.4f}")
        print()
        print("  Logfire captures: model, latency, tokens, cost per call")

    except ImportError:
        print("Install: pip install logfire")


if __name__ == "__main__":
    demo_llm_observability()
