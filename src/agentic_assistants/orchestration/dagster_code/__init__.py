"""
Dagster code location for the Agentic Assistants framework.

This package serves as the Dagster user code server entry point.
It exports a ``Definitions`` object that Dagster discovers automatically.

Usage (local dev):
    dagster dev -f src/agentic_assistants/orchestration/dagster_code/__init__.py

Usage (deployed):
    Pointed to by workspace.yaml as a code location.
"""

from agentic_assistants.orchestration.dagster_code.repository import get_definitions

defs = get_definitions()

__all__ = ["defs"]
