# requires: deepeval
"""DeepEval LLMTestCase, assert_test, and pytest-style structure."""

from __future__ import annotations


def main() -> None:
    print("DeepEval: LLMTestCase + assert_test (+ pytest sketch)")
    print("-" * 60)
    try:
        from deepeval import assert_test
        from deepeval.test_case import LLMTestCase
    except ImportError:
        print(
            "Missing dependency. Install with:\n"
            "  pip install deepeval"
        )
        return

    case = LLMTestCase(
        input="What is 2+2?",
        actual_output="The sum is 4.",
        expected_output="4",
    )
    print("LLMTestCase fields:")
    print(f"  input={case.input!r}")
    print(f"  actual_output={case.actual_output!r}")
    print(f"  expected_output={case.expected_output!r}")

    print(
        "\nPytest integration sketch:\n"
        "  import pytest\n"
        "  from deepeval import assert_test\n"
        "  from deepeval.metrics import EqualityMetric  # or another metric\n"
        "\n"
        "  def test_math_answer():\n"
        "      assert_test(case, [EqualityMetric()])\n"
    )

    metric = None
    for candidate in ("ExactMatchMetric", "EqualityMetric"):
        try:
            mod = __import__("deepeval.metrics", fromlist=[candidate])
            cls = getattr(mod, candidate, None)
            if cls is not None:
                metric = cls()
                break
        except (ImportError, AttributeError, TypeError):
            continue

    if metric is not None:
        try:
            assert_test(case, [metric])
            print(f"\nassert_test completed with {type(metric).__name__}.")
        except Exception as exc:
            print(f"\nassert_test raised: {exc}")
    else:
        print("\nNo simple deterministic metric found; assert_test pattern is shown above only.")


if __name__ == "__main__":
    main()
