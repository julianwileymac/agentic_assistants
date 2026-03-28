# requires: prefect
"""Prefect deployment with schedules and work pools.

Demonstrates:
- Creating deployments for flows
- CronSchedule and IntervalSchedule
- Work pool configuration
"""

from __future__ import annotations

import os

os.environ["PREFECT_SERVER_EPHEMERAL_ENABLED"] = "true"


def demo_deployment():
    try:
        from prefect import flow

        @flow(log_prints=True)
        def scheduled_etl(source: str = "default"):
            print(f"Running scheduled ETL from {source}")
            return {"records_processed": 100}

        print("Prefect Deployment Patterns:")
        print()
        print("  # Deploy with cron schedule (via CLI or Python):")
        print("  prefect deploy scheduled_etl --name prod-etl \\")
        print('      --cron "0 */6 * * *" \\')
        print("      --pool default-agent-pool")
        print()
        print("  # Or via Python API:")
        print("  scheduled_etl.serve(")
        print("      name='prod-etl',")
        print("      cron='0 */6 * * *',")
        print("      tags=['production', 'etl'],")
        print("  )")
        print()
        try:
            out = scheduled_etl("local-demo")
            print(f"Local flow run (no server required): {out!r}")
        except Exception as exc:
            print(f"Flow run error: {exc}")

    except ImportError:
        print("Install: pip install prefect")


if __name__ == "__main__":
    demo_deployment()
