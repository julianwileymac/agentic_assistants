# requires: pydantic-ai pydantic
"""PydanticAI self-correction: validation errors fed back to LLM for retry.

Demonstrates:
- Strict Pydantic constraints on output_type
- Automatic retry when LLM output fails validation
- Exponential backoff pattern
"""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class StrictFinancialReport(BaseModel):
    """Output model with strict validation constraints."""

    company_name: str = Field(min_length=2, max_length=100)
    ticker: str = Field(pattern=r"^[A-Z]{1,5}$", description="NYSE/NASDAQ ticker symbol")
    revenue_millions: float = Field(gt=0, description="Annual revenue in millions USD")
    profit_margin_pct: float = Field(ge=-100, le=100)
    recommendation: str = Field(description="buy, hold, or sell")
    confidence: float = Field(ge=0.0, le=1.0)

    @field_validator("recommendation")
    @classmethod
    def validate_recommendation(cls, v: str) -> str:
        allowed = {"buy", "hold", "sell"}
        v_lower = v.lower().strip()
        if v_lower not in allowed:
            raise ValueError(f"Must be one of {allowed}, got '{v}'")
        return v_lower

    @field_validator("ticker")
    @classmethod
    def validate_ticker_uppercase(cls, v: str) -> str:
        return v.upper()


def demo_self_correction():
    """Show how PydanticAI automatically retries on validation failure."""
    try:
        from pydantic_ai import Agent

        agent: Agent[None, StrictFinancialReport] = Agent(
            "openai:gpt-4o-mini",
            output_type=StrictFinancialReport,
            retries=3,
            system_prompt=(
                "You are a financial analyst. Provide accurate financial data. "
                "The ticker must be a valid 1-5 letter uppercase symbol. "
                "Recommendation must be exactly: buy, hold, or sell."
            ),
            defer_model_check=True,
        )

        print("Agent configured with retries=3 for self-correction")
        print("Output schema enforces:")
        print("  - ticker: 1-5 uppercase letters only")
        print("  - revenue_millions: must be > 0")
        print("  - profit_margin_pct: between -100 and 100")
        print("  - recommendation: exactly buy/hold/sell")
        print("  - confidence: between 0.0 and 1.0")
        print()
        print("Schema:", StrictFinancialReport.model_json_schema())

        print("\n--- Manual validation (what the agent rejects before retrying) ---")
        try:
            StrictFinancialReport.model_validate(
                {
                    "company_name": "Z",
                    "ticker": "TOOLONG",
                    "revenue_millions": -1,
                    "profit_margin_pct": 50,
                    "recommendation": "maybe",
                    "confidence": 2,
                }
            )
        except Exception as e:
            print("Expected validation failure:", type(e).__name__, str(e)[:200])

        print("\n--- Agent retries: FunctionModel returns invalid output tool, then valid ---")
        try:
            from pydantic_ai import ModelResponse, ToolCallPart
            from pydantic_ai.messages import ModelMessage
            from pydantic_ai.models.function import AgentInfo, FunctionModel

            def _output_tool_call(tool_name: str, args: dict[str, object]) -> ToolCallPart:
                """Construct ToolCallPart across pydantic-ai versions (positional vs keyword)."""
                try:
                    return ToolCallPart(tool_name, args)
                except TypeError:
                    return ToolCallPart(tool_name=tool_name, args=args)

            calls = {"n": 0}

            def flaky_financial(messages: list[ModelMessage], info: AgentInfo) -> ModelResponse:
                calls["n"] += 1
                tool_name = info.output_tools[0].name
                if calls["n"] == 1:
                    return ModelResponse(
                        parts=[
                            _output_tool_call(
                                tool_name,
                                {
                                    "company_name": "Z",
                                    "ticker": "TOOLONG",
                                    "revenue_millions": -1,
                                    "profit_margin_pct": 50,
                                    "recommendation": "maybe",
                                    "confidence": 2,
                                },
                            )
                        ]
                    )
                return ModelResponse(
                    parts=[
                        _output_tool_call(
                            tool_name,
                            {
                                "company_name": "Acme Corp",
                                "ticker": "ACME",
                                "revenue_millions": 100.0,
                                "profit_margin_pct": 12.0,
                                "recommendation": "hold",
                                "confidence": 0.85,
                            },
                        )
                    ]
                )

            with agent.override(model=FunctionModel(flaky_financial)):
                result = agent.run_sync("Produce a financial snapshot for ACME Inc.")
            print("Validated output after retries:", result.output)
            print("Simulated model turns used:", calls["n"])
            print(
                "First turn fails StrictFinancialReport validation; PydanticAI surfaces errors to the "
                "model and retries until the output validates (up to retries=3)."
            )
        except Exception as e:
            print(f"FunctionModel retry demo failed ({type(e).__name__}: {e}).")
            print("With pydantic-ai installed, this block simulates a bad structured output, then a valid one.")

    except ImportError:
        print("Install pydantic-ai: pip install pydantic-ai")


def main() -> None:
    """Run the self-correction / validation retry example."""
    demo_self_correction()


if __name__ == "__main__":
    main()
