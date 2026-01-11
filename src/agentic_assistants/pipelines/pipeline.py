"""
Pipeline composition for Kedro-style workflow definition.

A Pipeline is a collection of Nodes with dependency resolution and
validation of the computation graph (DAG).

Example:
    >>> from agentic_assistants.pipelines import Pipeline, node
    >>> 
    >>> pipeline = Pipeline([
    ...     node(load_data, outputs="raw_data"),
    ...     node(clean_data, inputs="raw_data", outputs="clean_data"),
    ...     node(train_model, inputs=["clean_data", "params"], outputs="model"),
    ... ])
    >>> 
    >>> # Filter pipeline by tags
    >>> preprocessing = pipeline.only_nodes_with_tags("preprocessing")
"""

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterable, List, Optional, Set, Union
import warnings

from agentic_assistants.pipelines.node import Node, NodeError, node
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


class PipelineError(Exception):
    """Exception raised for pipeline-related errors."""
    pass


class CircularDependencyError(PipelineError):
    """Exception raised when a circular dependency is detected."""
    pass


@dataclass
class PipelineOutput:
    """Container for pipeline execution output."""
    outputs: Dict[str, Any]
    node_results: Dict[str, Dict[str, Any]]
    execution_order: List[str]
    errors: List[str] = field(default_factory=list)
    
    @property
    def success(self) -> bool:
        return len(self.errors) == 0


class Pipeline:
    """
    A collection of nodes forming a directed acyclic graph (DAG).
    
    Pipelines support:
    - Automatic dependency resolution via topological sorting
    - Tag-based node filtering
    - Pipeline composition (adding pipelines together)
    - Namespace prefixing for modular pipelines
    - Visualization of the computation graph
    
    Attributes:
        nodes: Set of nodes in the pipeline
        
    Example:
        >>> # Create a pipeline
        >>> pipe = Pipeline([
        ...     node(func1, "a", "b", name="node1"),
        ...     node(func2, "b", "c", name="node2"),
        ... ])
        >>> 
        >>> # Combine pipelines
        >>> combined = pipe1 + pipe2
        >>> 
        >>> # Filter by tags
        >>> filtered = pipe.only_nodes_with_tags("feature")
    """
    
    def __init__(
        self,
        nodes: Iterable[Node],
        *,
        tags: Optional[Set[str]] = None,
    ):
        """
        Initialize a Pipeline.
        
        Args:
            nodes: Iterable of Node objects
            tags: Optional tags to apply to all nodes
        """
        # Convert to set and apply tags if provided
        node_set = set()
        for n in nodes:
            if tags:
                n = n.tag(tags)
            node_set.add(n)
        
        self._nodes = frozenset(node_set)
        
        # Build dependency graph
        self._inputs_to_nodes: Dict[str, Set[Node]] = defaultdict(set)
        self._outputs_to_nodes: Dict[str, Set[Node]] = defaultdict(set)
        
        for n in self._nodes:
            for input_name in n.all_inputs:
                self._inputs_to_nodes[input_name].add(n)
            for output_name in n.all_outputs:
                self._outputs_to_nodes[output_name].add(n)
        
        # Validate DAG
        self._validate()
        
        logger.debug(f"Created pipeline with {len(self._nodes)} nodes")
    
    def _validate(self) -> None:
        """Validate the pipeline is a valid DAG."""
        # Check for duplicate outputs
        for output_name, producing_nodes in self._outputs_to_nodes.items():
            if len(producing_nodes) > 1:
                node_names = [n.name for n in producing_nodes]
                raise PipelineError(
                    f"Output '{output_name}' is produced by multiple nodes: {node_names}"
                )
        
        # Check for circular dependencies
        self._check_circular_dependencies()
    
    def _check_circular_dependencies(self) -> None:
        """Check for circular dependencies using DFS."""
        # Build adjacency list
        adj: Dict[str, Set[str]] = defaultdict(set)
        
        for n in self._nodes:
            for output_name in n.all_outputs:
                for input_name in n.all_inputs:
                    # Find node that produces this input
                    for producer in self._outputs_to_nodes.get(input_name, []):
                        adj[producer.name].add(n.name)
        
        # DFS to detect cycles
        WHITE, GRAY, BLACK = 0, 1, 2
        color = {n.name: WHITE for n in self._nodes}
        
        def dfs(node_name: str, path: List[str]) -> None:
            color[node_name] = GRAY
            path.append(node_name)
            
            for neighbor in adj.get(node_name, []):
                if color[neighbor] == GRAY:
                    # Found cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    raise CircularDependencyError(
                        f"Circular dependency detected: {' -> '.join(cycle)}"
                    )
                elif color[neighbor] == WHITE:
                    dfs(neighbor, path)
            
            color[node_name] = BLACK
            path.pop()
        
        for n in self._nodes:
            if color[n.name] == WHITE:
                dfs(n.name, [])
    
    @property
    def nodes(self) -> Set[Node]:
        """Get all nodes in the pipeline."""
        return set(self._nodes)
    
    @property
    def node_names(self) -> Set[str]:
        """Get all node names."""
        return {n.name for n in self._nodes}
    
    def get_node(self, name: str) -> Optional[Node]:
        """Get a node by name."""
        for n in self._nodes:
            if n.name == name:
                return n
        return None
    
    @property
    def inputs(self) -> Set[str]:
        """
        Get pipeline inputs (datasets not produced by any node).
        
        These are the datasets that must be provided to run the pipeline.
        """
        all_inputs = set()
        all_outputs = set()
        
        for n in self._nodes:
            all_inputs.update(n.all_inputs)
            all_outputs.update(n.all_outputs)
        
        # Inputs are datasets needed but not produced
        return all_inputs - all_outputs
    
    @property
    def outputs(self) -> Set[str]:
        """
        Get pipeline outputs (datasets not consumed by any node).
        
        These are the final outputs of the pipeline.
        """
        all_inputs = set()
        all_outputs = set()
        
        for n in self._nodes:
            all_inputs.update(n.all_inputs)
            all_outputs.update(n.all_outputs)
        
        # Outputs are datasets produced but not consumed
        return all_outputs - all_inputs
    
    @property
    def all_inputs(self) -> Set[str]:
        """Get all inputs across all nodes."""
        result = set()
        for n in self._nodes:
            result.update(n.all_inputs)
        return result
    
    @property
    def all_outputs(self) -> Set[str]:
        """Get all outputs across all nodes."""
        result = set()
        for n in self._nodes:
            result.update(n.all_outputs)
        return result
    
    @property
    def data_sets(self) -> Set[str]:
        """Get all dataset names (inputs and outputs)."""
        return self.all_inputs | self.all_outputs
    
    def topological_sort(self) -> List[Node]:
        """
        Return nodes in topologically sorted order.
        
        Returns:
            List of nodes in execution order
        """
        # Build adjacency list and in-degree count
        in_degree: Dict[str, int] = {n.name: 0 for n in self._nodes}
        adj: Dict[str, List[str]] = defaultdict(list)
        
        for n in self._nodes:
            for input_name in n.all_inputs:
                # Find node that produces this input
                for producer in self._outputs_to_nodes.get(input_name, []):
                    adj[producer.name].append(n.name)
                    in_degree[n.name] += 1
        
        # Kahn's algorithm
        queue = [name for name, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            # Sort for deterministic order
            queue.sort()
            node_name = queue.pop(0)
            result.append(self.get_node(node_name))
            
            for neighbor in adj[node_name]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        if len(result) != len(self._nodes):
            raise CircularDependencyError("Pipeline contains a cycle")
        
        return result
    
    def only_nodes_with_tags(self, *tags: str) -> "Pipeline":
        """
        Create a new pipeline with only nodes that have the specified tags.
        
        Args:
            *tags: Tags to filter by (OR logic - node must have any tag)
            
        Returns:
            New Pipeline with filtered nodes
        """
        tag_set = set(tags)
        filtered_nodes = [n for n in self._nodes if n.tags & tag_set]
        return Pipeline(filtered_nodes)
    
    def only_nodes_without_tags(self, *tags: str) -> "Pipeline":
        """
        Create a new pipeline excluding nodes with the specified tags.
        
        Args:
            *tags: Tags to exclude
            
        Returns:
            New Pipeline without filtered nodes
        """
        tag_set = set(tags)
        filtered_nodes = [n for n in self._nodes if not (n.tags & tag_set)]
        return Pipeline(filtered_nodes)
    
    def only_nodes_with_inputs(self, *inputs: str) -> "Pipeline":
        """
        Create a new pipeline with only nodes that consume the specified inputs.
        
        Args:
            *inputs: Input dataset names
            
        Returns:
            New Pipeline with filtered nodes
        """
        input_set = set(inputs)
        filtered_nodes = [n for n in self._nodes if n.all_inputs & input_set]
        return Pipeline(filtered_nodes)
    
    def only_nodes_with_outputs(self, *outputs: str) -> "Pipeline":
        """
        Create a new pipeline with only nodes that produce the specified outputs.
        
        Args:
            *outputs: Output dataset names
            
        Returns:
            New Pipeline with filtered nodes
        """
        output_set = set(outputs)
        filtered_nodes = [n for n in self._nodes if n.all_outputs & output_set]
        return Pipeline(filtered_nodes)
    
    def from_nodes(self, *node_names: str) -> "Pipeline":
        """
        Create a new pipeline starting from specific nodes.
        
        Includes the specified nodes and all their downstream dependencies.
        
        Args:
            *node_names: Names of starting nodes
            
        Returns:
            New Pipeline with filtered nodes
        """
        to_include = set()
        queue = list(node_names)
        
        while queue:
            name = queue.pop(0)
            if name in to_include:
                continue
            
            node = self.get_node(name)
            if node:
                to_include.add(name)
                
                # Add downstream nodes
                for output in node.all_outputs:
                    for consumer in self._inputs_to_nodes.get(output, []):
                        if consumer.name not in to_include:
                            queue.append(consumer.name)
        
        filtered_nodes = [n for n in self._nodes if n.name in to_include]
        return Pipeline(filtered_nodes)
    
    def to_nodes(self, *node_names: str) -> "Pipeline":
        """
        Create a new pipeline ending at specific nodes.
        
        Includes the specified nodes and all their upstream dependencies.
        
        Args:
            *node_names: Names of ending nodes
            
        Returns:
            New Pipeline with filtered nodes
        """
        to_include = set()
        queue = list(node_names)
        
        while queue:
            name = queue.pop(0)
            if name in to_include:
                continue
            
            node = self.get_node(name)
            if node:
                to_include.add(name)
                
                # Add upstream nodes
                for input_name in node.all_inputs:
                    for producer in self._outputs_to_nodes.get(input_name, []):
                        if producer.name not in to_include:
                            queue.append(producer.name)
        
        filtered_nodes = [n for n in self._nodes if n.name in to_include]
        return Pipeline(filtered_nodes)
    
    def tag(self, tags: Union[Set[str], List[str], str]) -> "Pipeline":
        """
        Create a new pipeline with tags added to all nodes.
        
        Args:
            tags: Tags to add
            
        Returns:
            New Pipeline with tagged nodes
        """
        if isinstance(tags, str):
            tags = {tags}
        elif isinstance(tags, list):
            tags = set(tags)
        
        return Pipeline([n.tag(tags) for n in self._nodes])
    
    def with_namespace(self, namespace: str) -> "Pipeline":
        """
        Create a new pipeline with namespace prefix on all nodes.
        
        Args:
            namespace: Namespace prefix
            
        Returns:
            New Pipeline with namespaced nodes
        """
        return Pipeline([n.with_namespace(namespace) for n in self._nodes])
    
    def describe(self) -> str:
        """
        Get a textual description of the pipeline.
        
        Returns:
            Multi-line string describing the pipeline
        """
        lines = [
            f"Pipeline with {len(self._nodes)} nodes:",
            f"  Inputs: {sorted(self.inputs)}",
            f"  Outputs: {sorted(self.outputs)}",
            "",
            "Nodes (in topological order):",
        ]
        
        for i, n in enumerate(self.topological_sort(), 1):
            tags_str = f" [tags: {', '.join(sorted(n.tags))}]" if n.tags else ""
            lines.append(f"  {i}. {n.name}: {n.input_names} -> {n.output_names}{tags_str}")
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert pipeline to a dictionary representation.
        
        Returns:
            Dictionary representation of the pipeline
        """
        return {
            "nodes": [
                {
                    "name": n.name,
                    "inputs": n.input_names,
                    "outputs": n.output_names,
                    "tags": list(n.tags),
                }
                for n in self.topological_sort()
            ],
            "inputs": list(self.inputs),
            "outputs": list(self.outputs),
        }
    
    def __add__(self, other: "Pipeline") -> "Pipeline":
        """
        Combine two pipelines.
        
        Args:
            other: Pipeline to add
            
        Returns:
            New combined Pipeline
        """
        return Pipeline(list(self._nodes) + list(other._nodes))
    
    def __radd__(self, other: Any) -> "Pipeline":
        """Support sum() of pipelines."""
        if other == 0:
            return self
        return self.__add__(other)
    
    def __len__(self) -> int:
        """Return number of nodes."""
        return len(self._nodes)
    
    def __iter__(self):
        """Iterate over nodes in topological order."""
        return iter(self.topological_sort())
    
    def __repr__(self) -> str:
        return f"Pipeline(nodes={len(self._nodes)}, inputs={len(self.inputs)}, outputs={len(self.outputs)})"
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Pipeline):
            return False
        return self._nodes == other._nodes
    
    def __hash__(self) -> int:
        return hash(self._nodes)


def pipeline(
    nodes: Iterable[Node],
    *,
    tags: Optional[Union[Set[str], List[str]]] = None,
    namespace: Optional[str] = None,
) -> Pipeline:
    """
    Create a Pipeline from nodes with optional tags and namespace.
    
    This is a convenience function for creating pipelines.
    
    Args:
        nodes: Iterable of Node objects
        tags: Optional tags to apply to all nodes
        namespace: Optional namespace prefix for all nodes
        
    Returns:
        Pipeline instance
        
    Example:
        >>> pipe = pipeline(
        ...     [
        ...         node(func1, "a", "b"),
        ...         node(func2, "b", "c"),
        ...     ],
        ...     tags=["feature_engineering"],
        ...     namespace="features",
        ... )
    """
    if isinstance(tags, list):
        tags = set(tags)
    
    node_list = list(nodes)
    
    if namespace:
        node_list = [n.with_namespace(namespace) for n in node_list]
    
    return Pipeline(node_list, tags=tags)
