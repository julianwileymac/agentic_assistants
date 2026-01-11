# Chunk: f37fd3aa00da_0

- source: `src/agentic_assistants/pipelines/runners/__init__.py`
- lines: 1-31
- chunk: 1/1

```
"""
Pipeline runners for different execution strategies.

This module provides various runners for executing pipelines:
- SequentialRunner: Execute nodes one at a time
- ParallelRunner: Execute independent nodes in parallel (multiprocessing)
- ThreadRunner: Execute nodes using threads (for I/O bound tasks)
- KubernetesRunner: Execute nodes as Kubernetes Jobs

Example:
    >>> from agentic_assistants.pipelines.runners import SequentialRunner
    >>> 
    >>> runner = SequentialRunner()
    >>> result = runner.run(pipeline, catalog)
"""

from agentic_assistants.pipelines.runners.base import AbstractRunner, RunnerError
from agentic_assistants.pipelines.runners.sequential import SequentialRunner
from agentic_assistants.pipelines.runners.parallel import ParallelRunner
from agentic_assistants.pipelines.runners.thread import ThreadRunner
from agentic_assistants.pipelines.runners.kubernetes import KubernetesRunner

__all__ = [
    "AbstractRunner",
    "RunnerError",
    "SequentialRunner",
    "ParallelRunner",
    "ThreadRunner",
    "KubernetesRunner",
]
```
