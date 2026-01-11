"""
Node abstraction for pipeline execution.

A Node represents a single unit of computation in a pipeline, wrapping a
pure Python function with declared inputs and outputs.

Example:
    >>> from agentic_assistants.pipelines import node
    >>> 
    >>> def add_numbers(a, b):
    ...     return a + b
    >>> 
    >>> my_node = node(
    ...     func=add_numbers,
    ...     inputs=["input_a", "input_b"],
    ...     outputs="result",
    ...     name="add_numbers_node",
    ... )
"""

import inspect
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Set, Union
import hashlib

from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


class NodeError(Exception):
    """Exception raised for node-related errors."""
    pass


@dataclass(frozen=True)
class Node:
    """
    A node in a pipeline representing a single computation step.
    
    Nodes wrap pure Python functions and declare their data dependencies
    through inputs and outputs. This enables automatic dependency resolution
    and parallel execution.
    
    Attributes:
        func: The function to execute
        inputs: List of input dataset names (or dict for named args)
        outputs: List of output dataset names
        name: Node name (auto-generated if not provided)
        tags: Set of tags for filtering/selection
        confirms: List of datasets this node confirms/checkpoints
        namespace: Optional namespace prefix for inputs/outputs
    
    Example:
        >>> def clean_data(raw_df):
        ...     return raw_df.dropna()
        >>> 
        >>> node = Node(
        ...     func=clean_data,
        ...     inputs=["raw_data"],
        ...     outputs=["cleaned_data"],
        ...     name="clean_data_node",
        ...     tags={"preprocessing"},
        ... )
    """
    
    func: Callable
    inputs: Union[List[str], Dict[str, str], str, None]
    outputs: Union[List[str], str, None]
    name: str = ""
    tags: Set[str] = field(default_factory=set)
    confirms: List[str] = field(default_factory=list)
    namespace: Optional[str] = None
    
    def __post_init__(self):
        """Validate and normalize node configuration."""
        # Normalize inputs to list
        if self.inputs is None:
            object.__setattr__(self, "inputs", [])
        elif isinstance(self.inputs, str):
            object.__setattr__(self, "inputs", [self.inputs])
        elif isinstance(self.inputs, dict):
            # Keep as dict for named arguments
            pass
        
        # Normalize outputs to list
        if self.outputs is None:
            object.__setattr__(self, "outputs", [])
        elif isinstance(self.outputs, str):
            object.__setattr__(self, "outputs", [self.outputs])
        
        # Normalize tags to set
        if not isinstance(self.tags, set):
            object.__setattr__(self, "tags", set(self.tags))
        
        # Generate name if not provided
        if not self.name:
            name = self._generate_name()
            object.__setattr__(self, "name", name)
        
        # Validate
        self._validate()
    
    def _generate_name(self) -> str:
        """Generate a unique name for the node."""
        func_name = self.func.__name__ if hasattr(self.func, "__name__") else "lambda"
        
        # Create a hash from inputs/outputs for uniqueness
        inputs_str = str(sorted(self.input_names))
        outputs_str = str(sorted(self.output_names))
        hash_input = f"{func_name}:{inputs_str}:{outputs_str}"
        hash_suffix = hashlib.md5(hash_input.encode()).hexdigest()[:8]
        
        return f"{func_name}_{hash_suffix}"
    
    def _validate(self) -> None:
        """Validate node configuration."""
        # Check function is callable
        if not callable(self.func):
            raise NodeError(f"Node function must be callable, got {type(self.func)}")
        
        # Validate inputs match function signature
        sig = inspect.signature(self.func)
        params = list(sig.parameters.keys())
        
        # Skip validation for *args/**kwargs functions
        has_var_positional = any(
            p.kind == inspect.Parameter.VAR_POSITIONAL
            for p in sig.parameters.values()
        )
        has_var_keyword = any(
            p.kind == inspect.Parameter.VAR_KEYWORD
            for p in sig.parameters.values()
        )
        
        if not has_var_positional and not has_var_keyword:
            # Count required parameters
            required_count = sum(
                1 for p in sig.parameters.values()
                if p.default == inspect.Parameter.empty
                and p.kind not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
            )
            
            input_count = len(self.input_names)
            if input_count < required_count:
                raise NodeError(
                    f"Node '{self.name}' has {input_count} inputs but function "
                    f"requires at least {required_count} arguments"
                )
    
    @property
    def input_names(self) -> List[str]:
        """Get list of input dataset names."""
        if isinstance(self.inputs, dict):
            return list(self.inputs.values())
        return list(self.inputs) if self.inputs else []
    
    @property
    def output_names(self) -> List[str]:
        """Get list of output dataset names."""
        return list(self.outputs) if self.outputs else []
    
    @property
    def all_inputs(self) -> Set[str]:
        """Get all input names including namespaced versions."""
        inputs = set(self.input_names)
        if self.namespace:
            inputs = {f"{self.namespace}.{i}" for i in inputs}
        return inputs
    
    @property
    def all_outputs(self) -> Set[str]:
        """Get all output names including namespaced versions."""
        outputs = set(self.output_names)
        if self.namespace:
            outputs = {f"{self.namespace}.{o}" for o in outputs}
        return outputs
    
    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the node with the given inputs.
        
        Args:
            inputs: Dictionary mapping input names to values
            
        Returns:
            Dictionary mapping output names to values
        """
        # Prepare function arguments
        if isinstance(self.inputs, dict):
            # Named arguments
            kwargs = {
                arg_name: inputs[dataset_name]
                for arg_name, dataset_name in self.inputs.items()
            }
            result = self.func(**kwargs)
        else:
            # Positional arguments
            args = [inputs[name] for name in self.input_names]
            result = self.func(*args)
        
        # Package outputs
        if len(self.output_names) == 0:
            return {}
        elif len(self.output_names) == 1:
            return {self.output_names[0]: result}
        else:
            # Multiple outputs - expect tuple/list
            if not isinstance(result, (tuple, list)):
                raise NodeError(
                    f"Node '{self.name}' has {len(self.output_names)} outputs "
                    f"but function returned {type(result)}, expected tuple/list"
                )
            if len(result) != len(self.output_names):
                raise NodeError(
                    f"Node '{self.name}' has {len(self.output_names)} outputs "
                    f"but function returned {len(result)} values"
                )
            return dict(zip(self.output_names, result))
    
    def tag(self, tags: Union[Set[str], List[str], str]) -> "Node":
        """
        Create a copy of the node with additional tags.
        
        Args:
            tags: Tags to add
            
        Returns:
            New Node with tags added
        """
        if isinstance(tags, str):
            tags = {tags}
        elif isinstance(tags, list):
            tags = set(tags)
        
        return Node(
            func=self.func,
            inputs=self.inputs,
            outputs=self.outputs,
            name=self.name,
            tags=self.tags | tags,
            confirms=self.confirms,
            namespace=self.namespace,
        )
    
    def with_namespace(self, namespace: str) -> "Node":
        """
        Create a copy of the node with a namespace prefix.
        
        Args:
            namespace: Namespace prefix
            
        Returns:
            New Node with namespace set
        """
        return Node(
            func=self.func,
            inputs=self.inputs,
            outputs=self.outputs,
            name=self.name,
            tags=self.tags,
            confirms=self.confirms,
            namespace=namespace,
        )
    
    def __repr__(self) -> str:
        inputs = self.input_names
        outputs = self.output_names
        return f"Node({self.name!r}, inputs={inputs}, outputs={outputs})"
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Node):
            return False
        return (
            self.name == other.name
            and self.input_names == other.input_names
            and self.output_names == other.output_names
        )
    
    def __hash__(self) -> int:
        return hash((
            self.name,
            tuple(self.input_names),
            tuple(self.output_names),
        ))


def node(
    func: Callable,
    inputs: Union[List[str], Dict[str, str], str, None] = None,
    outputs: Union[List[str], str, None] = None,
    *,
    name: Optional[str] = None,
    tags: Optional[Union[Set[str], List[str]]] = None,
    confirms: Optional[List[str]] = None,
    namespace: Optional[str] = None,
) -> Node:
    """
    Create a Node from a function.
    
    This is the primary way to create nodes for use in pipelines.
    
    Args:
        func: The function to wrap
        inputs: Input dataset names (list, dict for named args, or string)
        outputs: Output dataset names (list or string)
        name: Optional node name (auto-generated if not provided)
        tags: Optional tags for filtering
        confirms: Optional list of datasets to confirm/checkpoint
        namespace: Optional namespace prefix
        
    Returns:
        Node instance
        
    Example:
        >>> def clean_data(df):
        ...     return df.dropna()
        >>> 
        >>> # Simple node
        >>> n = node(clean_data, "raw_data", "clean_data")
        >>> 
        >>> # Node with tags
        >>> n = node(clean_data, "raw_data", "clean_data", tags=["preprocessing"])
        >>> 
        >>> # Node with named inputs
        >>> n = node(
        ...     train_model,
        ...     inputs={"data": "training_data", "params": "params:model"},
        ...     outputs="trained_model",
        ... )
    """
    return Node(
        func=func,
        inputs=inputs,
        outputs=outputs,
        name=name or "",
        tags=set(tags) if tags else set(),
        confirms=confirms or [],
        namespace=namespace,
    )


def _node_decorator(
    inputs: Union[List[str], Dict[str, str], str, None] = None,
    outputs: Union[List[str], str, None] = None,
    name: Optional[str] = None,
    tags: Optional[Union[Set[str], List[str]]] = None,
) -> Callable[[Callable], Node]:
    """
    Decorator to create a node from a function.
    
    Example:
        >>> @_node_decorator(inputs="raw_data", outputs="clean_data")
        ... def clean_data(df):
        ...     return df.dropna()
    """
    def decorator(func: Callable) -> Node:
        return node(func, inputs, outputs, name=name, tags=tags)
    return decorator
