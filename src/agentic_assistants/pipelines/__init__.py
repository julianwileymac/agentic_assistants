"""
Pipeline system for the Agentic Assistants framework.

This module provides Kedro-inspired pipeline abstractions for building
data processing and ML workflows with pure function nodes.

Example:
    >>> from agentic_assistants.pipelines import Pipeline, node
    >>> 
    >>> # Define nodes
    >>> def preprocess(raw_data):
    ...     return raw_data.dropna()
    >>> 
    >>> def train_model(processed_data, params):
    ...     # Training logic
    ...     return model
    >>> 
    >>> # Create pipeline
    >>> pipeline = Pipeline([
    ...     node(preprocess, inputs="raw_data", outputs="processed_data"),
    ...     node(train_model, inputs=["processed_data", "params:model"], outputs="model"),
    ... ])
    >>> 
    >>> # Run pipeline
    >>> from agentic_assistants.pipelines.runners import SequentialRunner
    >>> runner = SequentialRunner()
    >>> result = runner.run(pipeline, catalog)
"""

from agentic_assistants.pipelines.node import Node, node
from agentic_assistants.pipelines.pipeline import Pipeline, pipeline

__all__ = [
    "Node",
    "node",
    "Pipeline",
    "pipeline",
]
