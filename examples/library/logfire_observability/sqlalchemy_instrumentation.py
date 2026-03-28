# requires: logfire sqlalchemy
"""Logfire SQLAlchemy instrumentation: query tracing.

Demonstrates:
- logfire.instrument_sqlalchemy(engine=engine)
- Query tracing and slow query detection
"""

from __future__ import annotations


def demo_sqlalchemy_instrumentation():
    try:
        import logfire
        from sqlalchemy import create_engine, text

        logfire.configure(send_to_logfire=False)

        engine = create_engine("sqlite:///:memory:")
        logfire.instrument_sqlalchemy(engine=engine)

        with engine.connect() as conn:
            conn.execute(text("CREATE TABLE test (id INTEGER, name TEXT)"))
            conn.execute(text("INSERT INTO test VALUES (1, 'hello')"))
            result = conn.execute(text("SELECT * FROM test"))
            rows = result.fetchall()
            conn.commit()

        print(f"Queries executed: 3 (create, insert, select)")
        print(f"  Results: {rows}")
        print()
        print("Logfire traces every SQL query with:")
        print("  - Query text, parameters")
        print("  - Execution duration")
        print("  - Row count")
        print("  - Slow query warnings")

    except ImportError:
        print("Install: pip install logfire sqlalchemy")


if __name__ == "__main__":
    demo_sqlalchemy_instrumentation()
