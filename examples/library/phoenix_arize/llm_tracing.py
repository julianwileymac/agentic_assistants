# requires: arize-phoenix

"""
OpenTelemetry + OpenInference-style spans for mock LLM, retrieval, and tool steps.

Registers a Phoenix-compatible tracer provider (in-process / OTLP per your Phoenix setup),
builds a small parent/child trace with mock payloads, and prints span names and attribute keys.
"""

from __future__ import annotations


def _attr_keys() -> dict[str, str]:
    try:
        from openinference.semconv.trace import SpanAttributes as SA

        return {
            "kind_key": SA.OPENINFERENCE_SPAN_KIND,
            "input_key": SA.INPUT_VALUE,
            "output_key": SA.OUTPUT_VALUE,
            "model_key": SA.LLM_MODEL_NAME,
            "tool_name_key": getattr(SA, "TOOL_NAME", "tool.name"),
        }
    except ImportError:  # pragma: no cover
        return {
            "kind_key": "openinference.span.kind",
            "input_key": "input.value",
            "output_key": "output.value",
            "model_key": "llm.model_name",
            "tool_name_key": "tool.name",
        }


def main() -> None:
    try:
        from opentelemetry import trace
        from opentelemetry.trace import Status, StatusCode
        from phoenix.otel import register
    except ImportError as exc:  # pragma: no cover
        print("Install arize-phoenix (and OpenTelemetry deps) to run this example:", exc)
        return

    keys = _attr_keys()
    tracer_provider = register(
        project_name="examples-llm-tracing",
        auto_instrument=False,
    )
    tracer = trace.get_tracer("examples.library.phoenix_arize.llm_tracing")

    print("=" * 60)
    print("Mock RAG-style trace (parent + retrieval + tool + LLM children)")
    print("=" * 60)

    with tracer.start_as_current_span(
        "rag.request",
        attributes={keys["kind_key"]: "CHAIN"},
    ) as root:
        root.set_attribute(keys["input_key"], "What is the capital of France?")

        with tracer.start_as_current_span(
            "retrieval.vector_search",
            attributes={keys["kind_key"]: "RETRIEVER"},
        ) as retr:
            mock_docs = [
                "France is a country in Western Europe.",
                "Paris is the capital and largest city of France.",
            ]
            retr.set_attribute(keys["output_key"], str(mock_docs))
            retr.set_status(Status(StatusCode.OK))

        with tracer.start_as_current_span(
            "tool.geocode",
            attributes={
                keys["kind_key"]: "TOOL",
                keys["tool_name_key"]: "geocode",
            },
        ) as tool:
            tool.set_attribute(keys["input_key"], "Paris")
            tool.set_attribute(keys["output_key"], '{"lat": 48.8566, "lon": 2.3522}')
            tool.set_status(Status(StatusCode.OK))

        with tracer.start_as_current_span(
            "llm.generate",
            attributes={
                keys["kind_key"]: "LLM",
                keys["model_key"]: "mock-llm-1",
            },
        ) as llm:
            llm.set_attribute(keys["input_key"], "Context:\n" + "\n".join(mock_docs))
            answer = "The capital of France is Paris."
            llm.set_attribute(keys["output_key"], answer)
            llm.set_status(Status(StatusCode.OK))

        root.set_attribute(keys["output_key"], answer)
        root.set_status(Status(StatusCode.OK))

        span_ctx = root.get_span_context()
        print(f"  Root trace_id: {format(span_ctx.trace_id, '032x')}")
        print(f"  Root span_id:  {format(span_ctx.span_id, '016x')}")

    print()
    print("Trace structure (conceptual):")
    print("  rag.request (CHAIN)")
    print("    |- retrieval.vector_search (RETRIEVER)")
    print("    |- tool.geocode (TOOL)")
    print("    |- llm.generate (LLM)")
    print()
    print("Export: point PHOENIX_COLLECTOR_ENDPOINT / run `phoenix serve` per Phoenix docs")
    print("to view spans in the UI; this script only constructs spans locally.")

    shutdown = getattr(tracer_provider, "shutdown", None)
    if callable(shutdown):
        shutdown()


if __name__ == "__main__":
    main()
