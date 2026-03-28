# requires: logfire pydantic
"""Logfire Pydantic instrumentation: trace model validations.

Demonstrates:
- logfire.instrument_pydantic() for automatic validation tracing
- Seeing validation success/failure in traces
"""

from __future__ import annotations

from pydantic import BaseModel, Field, ValidationError


class UserProfile(BaseModel):
    name: str = Field(min_length=2)
    age: int = Field(ge=0, le=150)
    email: str


def demo_pydantic_instrumentation():
    try:
        import logfire

        logfire.configure(send_to_logfire=False)
        logfire.instrument_pydantic()

        with logfire.span("validate-users"):
            user = UserProfile(name="Alice", age=30, email="alice@example.com")
            print(f"Valid: {user}")

            try:
                bad = UserProfile(name="", age=-5, email="bad")
            except ValidationError as e:
                print(f"Validation failed: {e.error_count()} errors")

        print()
        print("Logfire traces all Pydantic validations automatically.")
        print("Each model_validate call becomes a span with:")
        print("  - Model name, field count")
        print("  - Success/failure status")
        print("  - Validation errors (if any)")

    except ImportError:
        print("Install: pip install logfire pydantic")


if __name__ == "__main__":
    demo_pydantic_instrumentation()
