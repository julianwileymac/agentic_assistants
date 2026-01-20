"""
Tool execution nodes.

This module provides flow nodes for tool/function execution:
- ToolNode: Execute a registered tool
- APICallNode: Make HTTP API requests
- CodeExecutorNode: Execute code snippets

Example:
    >>> from agentic_assistants.pipelines.nodes import APICallNode
    >>> 
    >>> api = APICallNode(config=APICallConfig(
    ...     url="https://api.example.com/data",
    ...     method="GET",
    ... ))
    >>> 
    >>> result = api.run({"params": {"query": "test"}})
    >>> print(result.outputs["response"])
"""

import json
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional

from agentic_assistants.pipelines.nodes.base import BaseFlowNode, NodeConfig
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


# =============================================================================
# Configuration Classes
# =============================================================================

@dataclass
class ToolConfig(NodeConfig):
    """Configuration for ToolNode."""
    
    # Name of the tool to execute
    tool_name: str = ""
    
    # Default arguments for the tool
    tool_args: Dict[str, Any] = field(default_factory=dict)
    
    # Timeout for tool execution
    timeout: int = 30


@dataclass
class APICallConfig(NodeConfig):
    """Configuration for APICallNode."""
    
    # API URL
    url: str = ""
    
    # HTTP method
    method: str = "GET"
    
    # Default headers
    headers: Dict[str, str] = field(default_factory=dict)
    
    # Request body (for POST/PUT)
    body: Optional[str] = None
    
    # Timeout in milliseconds
    timeout: int = 30000
    
    # Whether to verify SSL
    verify_ssl: bool = True
    
    # Authentication type: none, bearer, basic, api_key
    auth_type: str = "none"
    
    # Auth credentials (would be encrypted in production)
    auth_value: str = ""


@dataclass
class CodeExecutorConfig(NodeConfig):
    """Configuration for CodeExecutorNode."""
    
    # Programming language
    language: str = "python"
    
    # Code to execute
    code: str = ""
    
    # Whether to run in sandbox
    sandbox: bool = True
    
    # Timeout in seconds
    timeout: int = 30
    
    # Allowed imports (for Python)
    allowed_imports: list = field(default_factory=lambda: ["json", "math", "re", "datetime"])


# =============================================================================
# Tool Registry
# =============================================================================

class ToolRegistry:
    """Registry for available tools."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._tools: Dict[str, Callable] = {}
        return cls._instance
    
    def register(self, name: str, func: Callable, description: str = "") -> None:
        """Register a tool."""
        self._tools[name] = {
            "func": func,
            "description": description,
        }
    
    def get(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a tool by name."""
        return self._tools.get(name)
    
    def list_tools(self) -> list:
        """List all registered tools."""
        return list(self._tools.keys())


def get_tool_registry() -> ToolRegistry:
    """Get the tool registry instance."""
    return ToolRegistry()


# =============================================================================
# Node Implementations
# =============================================================================

class ToolNode(BaseFlowNode):
    """
    Node for executing a registered tool.
    
    Inputs:
        args: Arguments for the tool (merged with defaults)
        
    Outputs:
        result: Tool execution result
    """
    
    node_type = "tool"
    config_class = ToolConfig
    
    def __init__(self, config: Optional[ToolConfig] = None, **kwargs):
        super().__init__(config or ToolConfig(), **kwargs)
        self.config: ToolConfig
    
    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        args = inputs.get("args", {})
        
        # Merge with default args
        merged_args = {**self.config.tool_args, **args}
        
        if not self.config.tool_name:
            return {"result": None, "error": "No tool name specified"}
        
        registry = get_tool_registry()
        tool = registry.get(self.config.tool_name)
        
        if not tool:
            return {"result": None, "error": f"Tool not found: {self.config.tool_name}"}
        
        try:
            result = tool["func"](**merged_args)
            
            self.emit_metric("tool_executed", 1)
            
            return {"result": result}
            
        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            return {"result": None, "error": str(e)}
    
    @classmethod
    def get_input_schema(cls) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "args": {"type": "object"},
            },
        }
    
    @classmethod
    def get_output_schema(cls) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "result": {},
                "error": {"type": "string"},
            },
        }


class APICallNode(BaseFlowNode):
    """
    Node for making HTTP API requests.
    
    Inputs:
        url: Override URL (optional)
        params: Query parameters
        body: Request body
        headers: Additional headers
        
    Outputs:
        status_code: HTTP status code
        response: Response body
        headers: Response headers
    """
    
    node_type = "api_call"
    config_class = APICallConfig
    
    def __init__(self, config: Optional[APICallConfig] = None, **kwargs):
        super().__init__(config or APICallConfig(), **kwargs)
        self.config: APICallConfig
    
    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        url = inputs.get("url", self.config.url)
        params = inputs.get("params", {})
        body = inputs.get("body", self.config.body)
        extra_headers = inputs.get("headers", {})
        
        if not url:
            return {"status_code": 0, "response": None, "error": "No URL specified"}
        
        try:
            import httpx
            
            # Build headers
            headers = {**self.config.headers, **extra_headers}
            
            # Add authentication
            if self.config.auth_type == "bearer":
                headers["Authorization"] = f"Bearer {self.config.auth_value}"
            elif self.config.auth_type == "api_key":
                headers["X-API-Key"] = self.config.auth_value
            
            # Make request
            with httpx.Client(timeout=self.config.timeout / 1000, verify=self.config.verify_ssl) as client:
                if self.config.method.upper() == "GET":
                    response = client.get(url, params=params, headers=headers)
                elif self.config.method.upper() == "POST":
                    response = client.post(url, params=params, headers=headers, content=body)
                elif self.config.method.upper() == "PUT":
                    response = client.put(url, params=params, headers=headers, content=body)
                elif self.config.method.upper() == "DELETE":
                    response = client.delete(url, params=params, headers=headers)
                elif self.config.method.upper() == "PATCH":
                    response = client.patch(url, params=params, headers=headers, content=body)
                else:
                    return {"status_code": 0, "response": None, "error": f"Unsupported method: {self.config.method}"}
            
            # Parse response
            try:
                response_body = response.json()
            except json.JSONDecodeError:
                response_body = response.text
            
            # Emit metrics
            self.emit_metric("status_code", response.status_code)
            self.emit_metric("response_time_ms", response.elapsed.total_seconds() * 1000)
            
            return {
                "status_code": response.status_code,
                "response": response_body,
                "headers": dict(response.headers),
            }
            
        except ImportError:
            logger.warning("httpx not available")
            return {"status_code": 0, "response": None, "error": "httpx not available"}
        except Exception as e:
            logger.error(f"API call failed: {e}")
            return {"status_code": 0, "response": None, "error": str(e)}
    
    @classmethod
    def get_input_schema(cls) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "url": {"type": "string"},
                "params": {"type": "object"},
                "body": {"type": "string"},
                "headers": {"type": "object"},
            },
        }
    
    @classmethod
    def get_output_schema(cls) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "status_code": {"type": "integer"},
                "response": {},
                "headers": {"type": "object"},
                "error": {"type": "string"},
            },
        }


class CodeExecutorNode(BaseFlowNode):
    """
    Node for executing code snippets.
    
    WARNING: Code execution can be dangerous. Use sandboxing in production.
    
    Inputs:
        code: Code to execute (overrides config)
        variables: Variables to inject into execution context
        
    Outputs:
        result: Execution result
        stdout: Captured stdout
        stderr: Captured stderr
    """
    
    node_type = "code_executor"
    config_class = CodeExecutorConfig
    
    def __init__(self, config: Optional[CodeExecutorConfig] = None, **kwargs):
        super().__init__(config or CodeExecutorConfig(), **kwargs)
        self.config: CodeExecutorConfig
    
    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        code = inputs.get("code", self.config.code)
        variables = inputs.get("variables", {})
        
        if not code:
            return {"result": None, "stdout": "", "stderr": "", "error": "No code to execute"}
        
        if self.config.language.lower() != "python":
            return {"result": None, "stdout": "", "stderr": "", "error": f"Unsupported language: {self.config.language}"}
        
        try:
            import io
            import sys
            from contextlib import redirect_stdout, redirect_stderr
            
            # Capture stdout/stderr
            stdout_capture = io.StringIO()
            stderr_capture = io.StringIO()
            
            # Build restricted globals for sandbox
            if self.config.sandbox:
                allowed_builtins = {
                    "abs", "all", "any", "bool", "dict", "enumerate", "filter",
                    "float", "int", "len", "list", "map", "max", "min", "print",
                    "range", "round", "set", "sorted", "str", "sum", "tuple", "zip",
                }
                restricted_globals = {
                    "__builtins__": {k: __builtins__[k] for k in allowed_builtins if k in __builtins__}
                    if isinstance(__builtins__, dict)
                    else {k: getattr(__builtins__, k) for k in allowed_builtins if hasattr(__builtins__, k)}
                }
                
                # Add allowed imports
                for module_name in self.config.allowed_imports:
                    try:
                        restricted_globals[module_name] = __import__(module_name)
                    except ImportError:
                        pass
            else:
                restricted_globals = {"__builtins__": __builtins__}
            
            # Add input variables
            local_vars = dict(variables)
            
            # Execute code
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                exec(code, restricted_globals, local_vars)
            
            # Get result (last expression or 'result' variable)
            result = local_vars.get("result", None)
            
            # Emit metrics
            self.emit_metric("code_executed", 1)
            
            return {
                "result": result,
                "stdout": stdout_capture.getvalue(),
                "stderr": stderr_capture.getvalue(),
                "variables": {k: v for k, v in local_vars.items() if not k.startswith("_")},
            }
            
        except Exception as e:
            logger.error(f"Code execution failed: {e}")
            return {
                "result": None,
                "stdout": "",
                "stderr": str(e),
                "error": str(e),
            }
    
    @classmethod
    def get_input_schema(cls) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "code": {"type": "string"},
                "variables": {"type": "object"},
            },
        }
    
    @classmethod
    def get_output_schema(cls) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "result": {},
                "stdout": {"type": "string"},
                "stderr": {"type": "string"},
                "variables": {"type": "object"},
                "error": {"type": "string"},
            },
        }
