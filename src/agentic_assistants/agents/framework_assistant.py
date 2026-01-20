"""
Framework Assistant Agent - The built-in AI assistant for Agentic Assistants.

This agent provides comprehensive assistance including:
- Coding help with RAG-enhanced context
- Framework guidance and documentation
- Meta-analysis for self-improvement

The Framework Assistant is designed to help users work with the framework
effectively while also tracking usage patterns for continuous improvement.

Example:
    >>> from agentic_assistants.agents import FrameworkAssistantAgent
    >>> 
    >>> assistant = FrameworkAssistantAgent()
    >>> 
    >>> # Chat with the assistant
    >>> response = assistant.chat("How do I create a CrewAI agent?")
    >>> 
    >>> # Get coding help
    >>> code = assistant.generate_code("Create a data validation function")
    >>> 
    >>> # Get improvement suggestions
    >>> suggestions = assistant.get_improvement_suggestions()
"""

import time
from datetime import datetime
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from agentic_assistants.config import AgenticConfig
from agentic_assistants.agents.modules.coding_helper import CodingHelperModule
from agentic_assistants.agents.modules.framework_guide import FrameworkGuideModule
from agentic_assistants.agents.modules.meta_analyzer_module import MetaAnalyzerModule
from agentic_assistants.utils.logging import get_logger

if TYPE_CHECKING:
    from agentic_assistants.knowledge import KnowledgeBase
    from agentic_assistants.memory import AgentMemory
    from agentic_assistants.observability import UsageTracker

logger = get_logger(__name__)


class FrameworkAssistantAgent:
    """
    The built-in Framework Assistant Agent.
    
    This is the default agent in the framework that helps users with:
    - Coding tasks (code generation, review, debugging)
    - Framework guidance (documentation, configuration, deployment)
    - Self-improvement (meta-analysis, suggestions, optimization)
    
    The assistant integrates with:
    - RAG knowledge bases for context-aware responses
    - Persistent memory for conversation continuity
    - Usage tracking for analytics and meta-analysis
    
    Attributes:
        config: Framework configuration
        coding_helper: Module for coding assistance
        framework_guide: Module for framework guidance
        meta_analyzer: Module for self-improvement analysis
    """
    
    DEFAULT_SYSTEM_PROMPT = """You are the Framework Assistant for Agentic Assistants.
You help users work with the framework effectively, providing assistance with:

1. **Coding**: Code generation, review, debugging, and refactoring
2. **Framework Guidance**: Understanding features, configuration, and best practices
3. **Deployment**: Deploying agents and flows to various targets
4. **Troubleshooting**: Helping resolve issues and errors

Be helpful, accurate, and provide practical examples when relevant.
When you don't know something, say so and suggest where to find the answer."""

    def __init__(
        self,
        config: Optional[AgenticConfig] = None,
        code_knowledge_base: Optional["KnowledgeBase"] = None,
        docs_knowledge_base: Optional["KnowledgeBase"] = None,
        memory: Optional["AgentMemory"] = None,
        usage_tracker: Optional["UsageTracker"] = None,
    ):
        """
        Initialize the Framework Assistant Agent.
        
        Args:
            config: Configuration instance
            code_knowledge_base: Knowledge base for code context
            docs_knowledge_base: Knowledge base for documentation
            memory: Memory store for conversation history
            usage_tracker: Usage tracker for analytics
        """
        self.config = config or AgenticConfig()
        self._code_kb = code_knowledge_base
        self._docs_kb = docs_knowledge_base
        self._memory = memory
        self._usage_tracker = usage_tracker
        
        # Initialize modules
        self.coding_helper = CodingHelperModule(
            config=self.config,
            knowledge_base=self._code_kb,
            memory=self._memory,
            usage_tracker=self._usage_tracker,
        )
        
        self.framework_guide = FrameworkGuideModule(
            config=self.config,
            knowledge_base=self._docs_kb,
            memory=self._memory,
            usage_tracker=self._usage_tracker,
        )
        
        self.meta_analyzer = MetaAnalyzerModule(
            config=self.config,
            usage_tracker=self._usage_tracker,
        )
        
        # Conversation state
        self._conversation_history: List[Dict[str, str]] = []
        self._session_start = datetime.utcnow()
    
    @property
    def usage_tracker(self) -> Optional["UsageTracker"]:
        """Get or create the usage tracker."""
        if self._usage_tracker is None and self.config.assistant.usage_tracking_enabled:
            try:
                from agentic_assistants.observability import UsageTracker
                self._usage_tracker = UsageTracker(self.config)
                # Update modules with tracker
                self.coding_helper.usage_tracker = self._usage_tracker
                self.framework_guide.usage_tracker = self._usage_tracker
                self.meta_analyzer._usage_tracker = self._usage_tracker
            except ImportError:
                pass
        return self._usage_tracker
    
    def _get_model(self) -> str:
        """Get the model to use."""
        return self.config.assistant.model or self.config.ollama.default_model
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt."""
        return self.config.assistant.system_prompt or self.DEFAULT_SYSTEM_PROMPT
    
    def _call_llm(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: float = 0.7,
    ) -> str:
        """Make an LLM call."""
        import httpx
        
        system = system_message or self._get_system_prompt()
        
        # Build messages with history
        messages = [{"role": "system", "content": system}]
        
        # Add conversation history (limited to max_context_messages)
        max_history = self.config.assistant.max_context_messages
        messages.extend(self._conversation_history[-max_history:])
        
        messages.append({"role": "user", "content": prompt})
        
        start_time = time.time()
        
        response = httpx.post(
            f"{self.config.ollama.host}/api/chat",
            json={
                "model": self._get_model(),
                "messages": messages,
                "stream": False,
                "options": {"temperature": temperature},
            },
            timeout=self.config.ollama.timeout,
        )
        response.raise_for_status()
        
        duration_ms = (time.time() - start_time) * 1000
        result = response.json()
        content = result.get("message", {}).get("content", "")
        
        # Update conversation history
        self._conversation_history.append({"role": "user", "content": prompt})
        self._conversation_history.append({"role": "assistant", "content": content})
        
        # Track usage
        if self.usage_tracker:
            self.usage_tracker.track_model_inference(
                model=self._get_model(),
                duration_ms=duration_ms,
                prompt_tokens=result.get("prompt_eval_count", 0),
                completion_tokens=result.get("eval_count", 0),
            )
            
            self.usage_tracker.track_user_interaction(
                interaction_type="chat",
                feature_used="framework_assistant",
                input_length=len(prompt),
                response_length=len(content),
                duration_ms=duration_ms,
            )
        
        # Store in memory if enabled
        if self._memory and self.config.assistant.memory_enabled:
            try:
                self._memory.add_memory(
                    f"User: {prompt[:200]}\nAssistant: {content[:500]}",
                    {"type": "conversation", "timestamp": datetime.utcnow().isoformat()},
                )
            except Exception as e:
                logger.warning(f"Failed to store memory: {e}")
        
        return content
    
    def chat(
        self,
        message: str,
        include_rag: bool = True,
    ) -> str:
        """
        Chat with the assistant.
        
        Args:
            message: User message
            include_rag: Whether to include RAG context
            
        Returns:
            Assistant response
        """
        # Determine the type of request
        request_type = self._classify_request(message)
        
        # Route to appropriate module or handle directly
        if request_type == "coding" and self.config.assistant.enable_coding_helper:
            return self._handle_coding_request(message)
        elif request_type == "framework" and self.config.assistant.enable_framework_guide:
            return self.framework_guide.get_help(message)
        else:
            # General chat
            return self._handle_general_chat(message, include_rag)
    
    def _classify_request(self, message: str) -> str:
        """Classify the type of request."""
        message_lower = message.lower()
        
        # Coding indicators
        coding_keywords = [
            "code", "function", "class", "debug", "error", "fix",
            "implement", "write", "create a", "generate", "refactor",
            "review", "explain this code", "```"
        ]
        if any(kw in message_lower for kw in coding_keywords):
            return "coding"
        
        # Framework indicators
        framework_keywords = [
            "how do i", "how to", "configure", "setup", "deploy",
            "adapter", "crewai", "langgraph", "kubernetes", "mlflow",
            "documentation", "guide", "help with"
        ]
        if any(kw in message_lower for kw in framework_keywords):
            return "framework"
        
        return "general"
    
    def _handle_coding_request(self, message: str) -> str:
        """Handle a coding-related request."""
        message_lower = message.lower()
        
        # Check for specific coding tasks
        if "review" in message_lower and "code" in message_lower:
            # Extract code if present
            if "```" in message:
                code = self._extract_code(message)
                if code:
                    review = self.coding_helper.review_code(code)
                    return review.get("review", "Could not review the code.")
        
        if "debug" in message_lower or "fix" in message_lower:
            code = self._extract_code(message)
            if code:
                debug = self.coding_helper.debug_code(code, expected_behavior=message)
                return debug.get("analysis", "Could not analyze the code.")
        
        if "explain" in message_lower:
            code = self._extract_code(message)
            if code:
                return self.coding_helper.explain_code(code)
        
        if "refactor" in message_lower:
            code = self._extract_code(message)
            if code:
                result = self.coding_helper.suggest_refactoring(code)
                return result.get("suggestions", "Could not generate refactoring suggestions.")
        
        # Default to code generation
        return self.coding_helper.generate_code(message)
    
    def _extract_code(self, message: str) -> Optional[str]:
        """Extract code from a message."""
        if "```" in message:
            parts = message.split("```")
            if len(parts) >= 3:
                code_block = parts[1]
                # Remove language identifier if present
                lines = code_block.split("\n")
                if lines and not lines[0].strip().startswith(("def ", "class ", "import ", "#")):
                    code_block = "\n".join(lines[1:])
                return code_block.strip()
        return None
    
    def _handle_general_chat(self, message: str, include_rag: bool) -> str:
        """Handle a general chat message."""
        prompt = message
        
        # Add RAG context if enabled
        if include_rag and self.config.assistant.rag_enabled:
            context_parts = []
            
            # Get code context if code KB available
            if self._code_kb:
                try:
                    results = self._code_kb.search(message, top_k=3)
                    if results:
                        context_parts.append("Relevant code:\n" + "\n".join(
                            f"- {r.content[:300]}" for r in results[:2]
                        ))
                except Exception as e:
                    logger.debug(f"Code KB search failed: {e}")
            
            # Get docs context if docs KB available
            if self._docs_kb:
                try:
                    results = self._docs_kb.search(message, top_k=3)
                    if results:
                        context_parts.append("Relevant documentation:\n" + "\n".join(
                            f"- {r.content[:300]}" for r in results[:2]
                        ))
                except Exception as e:
                    logger.debug(f"Docs KB search failed: {e}")
            
            # Get memory context if available
            if self._memory and self.config.assistant.memory_enabled:
                try:
                    memories = self._memory.search_memories(message, limit=3)
                    if memories:
                        context_parts.append("Relevant memories:\n" + "\n".join(
                            f"- {m.get('content', '')[:200]}" for m in memories[:2]
                        ))
                except Exception as e:
                    logger.debug(f"Memory search failed: {e}")
            
            if context_parts:
                prompt = f"Context:\n{chr(10).join(context_parts)}\n\nUser: {message}"
        
        return self._call_llm(prompt)
    
    # === Coding Helper Methods ===
    
    def generate_code(
        self,
        request: str,
        language: Optional[str] = None,
    ) -> str:
        """Generate code based on a request."""
        if not self.config.assistant.enable_coding_helper:
            return "Coding helper is disabled in configuration."
        return self.coding_helper.generate_code(request, language)
    
    def review_code(self, code: str) -> Dict[str, Any]:
        """Review code and provide feedback."""
        if not self.config.assistant.enable_coding_helper:
            return {"review": "Coding helper is disabled in configuration."}
        return self.coding_helper.review_code(code)
    
    def debug_code(
        self,
        code: str,
        error_message: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Help debug code."""
        if not self.config.assistant.enable_coding_helper:
            return {"analysis": "Coding helper is disabled in configuration."}
        return self.coding_helper.debug_code(code, error_message)
    
    # === Framework Guide Methods ===
    
    def get_help(self, question: str) -> str:
        """Get help with a framework question."""
        if not self.config.assistant.enable_framework_guide:
            return "Framework guide is disabled in configuration."
        return self.framework_guide.get_help(question)
    
    def get_configuration_help(self, section: str) -> str:
        """Get help with configuration."""
        if not self.config.assistant.enable_framework_guide:
            return "Framework guide is disabled in configuration."
        return self.framework_guide.get_configuration_help(section)
    
    def get_deployment_guide(self, deployment_type: str) -> str:
        """Get deployment guidance."""
        if not self.config.assistant.enable_framework_guide:
            return "Framework guide is disabled in configuration."
        return self.framework_guide.get_deployment_guide(deployment_type)
    
    # === Meta Analysis Methods ===
    
    def get_improvement_suggestions(
        self,
        days: int = 7,
    ) -> List[Dict[str, Any]]:
        """Get improvement suggestions from meta-analysis."""
        if not self.config.assistant.enable_meta_analysis:
            return []
        return self.meta_analyzer.get_suggestions(limit=10)
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get framework health summary."""
        if not self.config.assistant.enable_meta_analysis:
            return {"status": "meta_analysis_disabled"}
        return self.meta_analyzer.get_health_summary()
    
    def generate_improvement_plan(self) -> str:
        """Generate an improvement plan."""
        if not self.config.assistant.enable_meta_analysis:
            return "Meta-analysis is disabled in configuration."
        return self.meta_analyzer.generate_improvement_plan()
    
    # === Session Management ===
    
    def reset_conversation(self) -> None:
        """Reset the conversation history."""
        self._conversation_history = []
        self.coding_helper.reset_conversation()
        self.framework_guide.reset_conversation()
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get the conversation history."""
        return self._conversation_history.copy()
    
    def get_session_info(self) -> Dict[str, Any]:
        """Get information about the current session."""
        return {
            "session_start": self._session_start.isoformat(),
            "message_count": len(self._conversation_history),
            "model": self._get_model(),
            "features_enabled": {
                "coding_helper": self.config.assistant.enable_coding_helper,
                "framework_guide": self.config.assistant.enable_framework_guide,
                "meta_analysis": self.config.assistant.enable_meta_analysis,
                "rag": self.config.assistant.rag_enabled,
                "memory": self.config.assistant.memory_enabled,
                "usage_tracking": self.config.assistant.usage_tracking_enabled,
            },
            "knowledge_bases": {
                "code": self._code_kb is not None,
                "docs": self._docs_kb is not None,
            },
        }
    
    # === Knowledge Base Management ===
    
    def connect_code_kb(self, kb: "KnowledgeBase") -> None:
        """Connect a code knowledge base."""
        self._code_kb = kb
        self.coding_helper.knowledge_base = kb
    
    def connect_docs_kb(self, kb: "KnowledgeBase") -> None:
        """Connect a documentation knowledge base."""
        self._docs_kb = kb
        self.framework_guide.knowledge_base = kb
    
    def connect_memory(self, memory: "AgentMemory") -> None:
        """Connect a memory store."""
        self._memory = memory
        self.coding_helper.memory = memory
        self.framework_guide.memory = memory


# Factory function
def create_framework_assistant(
    config: Optional[AgenticConfig] = None,
    **kwargs,
) -> FrameworkAssistantAgent:
    """
    Create a Framework Assistant Agent with default configuration.
    
    Args:
        config: Optional configuration
        **kwargs: Additional arguments
        
    Returns:
        Configured Framework Assistant Agent
    """
    config = config or AgenticConfig()
    
    # Try to set up knowledge bases if configured
    code_kb = None
    docs_kb = None
    
    if config.assistant.code_kb_project_id:
        try:
            from agentic_assistants.knowledge import get_knowledge_base
            code_kb = get_knowledge_base(config.assistant.code_kb_project_id)
        except Exception as e:
            logger.warning(f"Failed to load code knowledge base: {e}")
    
    if config.assistant.docs_kb_name:
        try:
            from agentic_assistants.knowledge import get_knowledge_base
            docs_kb = get_knowledge_base(config.assistant.docs_kb_name)
        except Exception as e:
            logger.debug(f"Docs knowledge base not found: {e}")
    
    # Try to set up memory if configured
    memory = None
    if config.assistant.memory_enabled:
        try:
            from agentic_assistants.memory import get_memory_store
            memory = get_memory_store(backend="mem0")
        except Exception as e:
            logger.debug(f"Memory store not available: {e}")
    
    return FrameworkAssistantAgent(
        config=config,
        code_knowledge_base=code_kb,
        docs_knowledge_base=docs_kb,
        memory=memory,
        **kwargs,
    )
