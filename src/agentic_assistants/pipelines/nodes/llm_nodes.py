"""
LLM (Large Language Model) nodes.

This module provides flow nodes for LLM operations:
- LLMNode: Generate text with an LLM
- PromptTemplateNode: Format prompts with variables
- ChatModelNode: Conversational LLM with memory

Example:
    >>> from agentic_assistants.pipelines.nodes import LLMNode
    >>> 
    >>> llm = LLMNode(config=LLMConfig(
    ...     model="llama3.2",
    ...     temperature=0.7,
    ... ))
    >>> 
    >>> result = llm.run({"prompt": "Explain RAG in one paragraph."})
    >>> print(result.outputs["response"])
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from agentic_assistants.config import AgenticConfig
from agentic_assistants.llms import LLMProvider
from agentic_assistants.pipelines.nodes.base import BaseFlowNode, NodeConfig
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


# =============================================================================
# Configuration Classes
# =============================================================================

@dataclass
class LLMConfig(NodeConfig):
    """Configuration for LLMNode."""
    
    # Model name
    model: str = "llama3.2"
    
    # Sampling temperature
    temperature: float = 0.7
    
    # Maximum tokens to generate
    max_tokens: Optional[int] = None
    
    # Top-p sampling
    top_p: float = 0.9
    
    # System prompt
    system_prompt: str = ""
    
    # Stop sequences
    stop_sequences: List[str] = field(default_factory=list)
    
    # Provider configuration
    provider: str = "ollama"
    endpoint: Optional[str] = None
    api_key_env: Optional[str] = None

    # Legacy field retained as alias for endpoint
    host: str = "http://localhost:11434"


@dataclass
class PromptTemplateConfig(NodeConfig):
    """Configuration for PromptTemplateNode."""
    
    # Template string with {variable} placeholders
    template: str = ""
    
    # Default values for variables
    defaults: Dict[str, str] = field(default_factory=dict)
    
    # Whether to strip whitespace from output
    strip_whitespace: bool = True


@dataclass
class ChatModelConfig(NodeConfig):
    """Configuration for ChatModelNode."""
    
    # Model name
    model: str = "llama3.2"
    
    # System prompt
    system_prompt: str = "You are a helpful assistant."
    
    # Temperature
    temperature: float = 0.7
    
    # Whether to maintain conversation memory
    memory_enabled: bool = True
    
    # Maximum history messages to keep
    max_history: int = 10
    
    # Provider configuration
    provider: str = "ollama"
    endpoint: Optional[str] = None
    api_key_env: Optional[str] = None

    # Legacy field retained as alias for endpoint
    host: str = "http://localhost:11434"


# =============================================================================
# Node Implementations
# =============================================================================

class LLMNode(BaseFlowNode):
    """
    Node for generating text with an LLM.
    
    Inputs:
        prompt: The prompt to send to the LLM
        context: Optional context to include
        
    Outputs:
        response: Generated text
        tokens_used: Number of tokens used
    """
    
    node_type = "llm"
    config_class = LLMConfig
    
    def __init__(self, config: Optional[LLMConfig] = None, **kwargs):
        super().__init__(config or LLMConfig(), **kwargs)
        self.config: LLMConfig
    
    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        prompt = inputs.get("prompt", "")
        context = inputs.get("context", "")
        
        if not prompt:
            return {"response": "", "tokens_used": 0}
        
        # Build full prompt with context
        full_prompt = prompt
        if context:
            full_prompt = f"Context:\n{context}\n\n{prompt}"
        
        try:
            runtime_config = AgenticConfig()
            provider_client = LLMProvider.from_config(
                runtime_config,
                provider=self.config.provider,
                model=self.config.model,
                endpoint=self.config.endpoint or self.config.host,
                api_key_env=self.config.api_key_env,
            )

            messages: List[Dict[str, str]] = []
            if self.config.system_prompt:
                messages.append({"role": "system", "content": self.config.system_prompt})
            messages.append({"role": "user", "content": full_prompt})

            llm_response = provider_client.chat(
                messages=messages,
                model=self.config.model,
                temperature=self.config.temperature,
                max_new_tokens=self.config.max_tokens,
                stop=self.config.stop_sequences or None,
            )
            response_text = llm_response.content
            tokens_used = (
                llm_response.total_tokens
                if llm_response.total_tokens is not None
                else len(full_prompt.split()) + len(response_text.split())
            )
            
            # Emit metrics
            self.emit_metric("prompt_length", len(full_prompt))
            self.emit_metric("response_length", len(response_text))
            self.emit_metric("tokens_used", tokens_used)
            
            return {
                "response": response_text,
                "tokens_used": tokens_used,
            }
            
        except ImportError:
            logger.warning("Provider dependency not available")
            return {"response": "", "tokens_used": 0, "error": "LLM not available"}
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            raise
    
    @classmethod
    def get_input_schema(cls) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "prompt": {"type": "string", "description": "The prompt to send"},
                "context": {"type": "string", "description": "Optional context"},
            },
            "required": ["prompt"],
        }
    
    @classmethod
    def get_output_schema(cls) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "response": {"type": "string"},
                "tokens_used": {"type": "integer"},
            },
        }


class PromptTemplateNode(BaseFlowNode):
    """
    Node for formatting prompts with variables.
    
    Inputs:
        variables: Dictionary of variable values
        
    Outputs:
        prompt: Formatted prompt string
    """
    
    node_type = "prompt_template"
    config_class = PromptTemplateConfig
    
    def __init__(self, config: Optional[PromptTemplateConfig] = None, **kwargs):
        super().__init__(config or PromptTemplateConfig(), **kwargs)
        self.config: PromptTemplateConfig
    
    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        variables = inputs.get("variables", {})
        
        # Merge with defaults
        all_vars = {**self.config.defaults, **variables}
        
        # Format template
        try:
            prompt = self.config.template.format(**all_vars)
        except KeyError as e:
            logger.warning(f"Missing template variable: {e}")
            prompt = self.config.template
        
        if self.config.strip_whitespace:
            prompt = prompt.strip()
        
        return {"prompt": prompt}
    
    @classmethod
    def get_input_schema(cls) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "variables": {
                    "type": "object",
                    "description": "Variable values for the template",
                },
            },
        }
    
    @classmethod
    def get_output_schema(cls) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "prompt": {"type": "string"},
            },
        }


class ChatModelNode(BaseFlowNode):
    """
    Node for conversational LLM with optional memory.
    
    Inputs:
        message: User message
        history: Optional conversation history
        
    Outputs:
        response: Assistant response
        history: Updated conversation history
    """
    
    node_type = "chat_model"
    config_class = ChatModelConfig
    
    def __init__(self, config: Optional[ChatModelConfig] = None, **kwargs):
        super().__init__(config or ChatModelConfig(), **kwargs)
        self.config: ChatModelConfig
        self._history: List[Dict[str, str]] = []
    
    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        message = inputs.get("message", "")
        history = inputs.get("history", self._history if self.config.memory_enabled else [])
        
        if not message:
            return {"response": "", "history": history}
        
        try:
            runtime_config = AgenticConfig()
            provider_client = LLMProvider.from_config(
                runtime_config,
                provider=self.config.provider,
                model=self.config.model,
                endpoint=self.config.endpoint or self.config.host,
                api_key_env=self.config.api_key_env,
            )

            messages: List[Dict[str, str]] = [{"role": "system", "content": self.config.system_prompt}]
            for entry in history[-self.config.max_history:]:
                if entry.get("role") == "user":
                    messages.append({"role": "user", "content": entry["content"]})
                elif entry.get("role") == "assistant":
                    messages.append({"role": "assistant", "content": entry["content"]})

            messages.append({"role": "user", "content": message})

            llm_response = provider_client.chat(
                messages=messages,
                model=self.config.model,
                temperature=self.config.temperature,
            )
            response_text = llm_response.content
            
            # Update history
            new_history = history + [
                {"role": "user", "content": message},
                {"role": "assistant", "content": response_text},
            ]
            
            # Trim history if needed
            if len(new_history) > self.config.max_history * 2:
                new_history = new_history[-(self.config.max_history * 2):]
            
            # Update internal history if memory enabled
            if self.config.memory_enabled:
                self._history = new_history
            
            # Emit metrics
            self.emit_metric("history_length", len(new_history))
            self.emit_metric("response_length", len(response_text))
            
            return {
                "response": response_text,
                "history": new_history,
            }
            
        except ImportError:
            logger.warning("Provider dependency not available")
            return {"response": "", "history": history, "error": "Chat model not available"}
        except Exception as e:
            logger.error(f"Chat generation failed: {e}")
            raise
    
    def clear_history(self) -> None:
        """Clear the conversation history."""
        self._history = []
    
    @classmethod
    def get_input_schema(cls) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "message": {"type": "string", "description": "User message"},
                "history": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "role": {"type": "string"},
                            "content": {"type": "string"},
                        },
                    },
                },
            },
            "required": ["message"],
        }
    
    @classmethod
    def get_output_schema(cls) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "response": {"type": "string"},
                "history": {"type": "array"},
            },
        }
