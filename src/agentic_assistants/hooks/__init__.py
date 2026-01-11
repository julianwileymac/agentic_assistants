"""
Hook system for pipeline and dataset lifecycle events.

This module provides a pluggy-based hook system for extending pipeline
and dataset behavior with custom callbacks.

Available hook specifications:
- PipelineHookSpec: Pipeline lifecycle events
- DatasetHookSpec: Dataset load/save events
- NodeHookSpec: Node execution events

Example:
    >>> from agentic_assistants.hooks import HookManager
    >>> from agentic_assistants.hooks.specs import PipelineHookSpec
    >>> 
    >>> class MyHook:
    ...     @hookimpl
    ...     def before_pipeline_run(self, pipeline, catalog):
    ...         print(f"Starting pipeline with {len(pipeline)} nodes")
    >>> 
    >>> manager = HookManager()
    >>> manager.register(MyHook())
"""

from agentic_assistants.hooks.manager import HookManager, get_hook_manager, set_hook_manager
from agentic_assistants.hooks.specs import (
    PipelineHookSpec,
    DatasetHookSpec,
    NodeHookSpec,
    hookimpl,
    hookspec,
)

__all__ = [
    "HookManager",
    "get_hook_manager",
    "set_hook_manager",
    "PipelineHookSpec",
    "DatasetHookSpec",
    "NodeHookSpec",
    "hookimpl",
    "hookspec",
]
