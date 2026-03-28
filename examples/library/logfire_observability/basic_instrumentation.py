# requires: logfire
"""Logfire basic instrumentation: spans, logs, structured attributes.

Demonstrates:
- logfire.configure()
- logfire.span() context manager
- logfire.info(), logfire.warn(), logfire.error()
- Structured attributes on spans
"""

from __future__ import annotations


def demo_basic():
    try:
        import logfire

        logfire.configure(send_to_logfire=False)

        logfire.info("Application started", version="1.0.0")

        with logfire.span("data-processing", records=100, source="api"):
            logfire.info("Processing batch", batch_size=50)
            # Simulate work
            for i in range(3):
                with logfire.span(f"process-chunk-{i}", chunk_index=i):
                    logfire.info(f"Chunk {i} processed", items=33)

        logfire.warn("Cache miss rate high", miss_rate=0.45)
        logfire.info("Application shutdown")

        print("Logfire basic instrumentation complete.")
        print("  Spans: data-processing > process-chunk-{0,1,2}")
        print("  Logs: info, warn with structured attributes")

    except ImportError:
        print("Install: pip install logfire")
        print()
        print("Logfire API:")
        print("  logfire.configure()         - Initialize")
        print("  logfire.span(name, **kw)    - Create tracing span")
        print("  logfire.info(msg, **kw)     - Structured info log")
        print("  logfire.warn(msg, **kw)     - Structured warning")
        print("  logfire.error(msg, **kw)    - Structured error")


if __name__ == "__main__":
    demo_basic()
