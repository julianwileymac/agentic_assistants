"""
Framework Guide Module for the Framework Assistant.

This module provides framework guidance including:
- Interactive help for framework features
- Configuration assistance
- Deployment guidance
- Best practices and documentation

Example:
    >>> guide = FrameworkGuideModule(config, docs_knowledge_base)
    >>> help_text = guide.get_help("How do I create a CrewAI agent?")
    >>> config_help = guide.get_configuration_help("kubernetes")
"""

import time
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from agentic_assistants.config import AgenticConfig
from agentic_assistants.llms import LLMProvider
from agentic_assistants.utils.logging import get_logger

if TYPE_CHECKING:
    from agentic_assistants.knowledge import KnowledgeBase
    from agentic_assistants.memory import AgentMemory
    from agentic_assistants.observability import UsageTracker

logger = get_logger(__name__)


class FrameworkGuideModule:
    """
    Provides framework guidance and help.
    
    Features:
    - Framework feature documentation
    - Configuration assistance
    - Deployment guidance
    - Best practices
    - Troubleshooting help
    
    Attributes:
        config: Framework configuration
        knowledge_base: RAG knowledge base with framework docs
        memory: Optional memory store
        usage_tracker: Optional usage tracker
    """
    
    DEFAULT_GUIDE_SYSTEM_PROMPT = """You are a helpful framework guide assistant for Agentic Assistants.
You help users understand and use the framework effectively, including:
- Agent creation and configuration
- Framework adapters (CrewAI, LangGraph, AutoGen, etc.)
- Knowledge bases and RAG
- Model training and deployment
- Kubernetes integration
- MLFlow experiment tracking

Always provide clear, accurate information based on the framework documentation.
Include code examples when helpful. Be friendly and supportive."""

    # Framework feature documentation snippets (built-in knowledge)
    FRAMEWORK_DOCS = {
        "adapters": """
The framework supports multiple agent frameworks through adapters:
- CrewAI: Multi-agent orchestration with crews and tasks
- LangGraph: Graph-based workflow orchestration
- AutoGen: Microsoft's multi-agent conversation framework
- Google ADK: Google's Agent Development Kit
- Agno: Modern framework with reasoning modes
- LangFlow: Visual workflow builder

Each adapter provides:
- Observability (MLFlow tracking, OpenTelemetry tracing)
- Usage tracking for analytics
- RAG integration
- Memory support
""",
        "knowledge_base": """
Knowledge bases provide RAG (Retrieval-Augmented Generation) support:
- VectorKnowledgeBase: Pure vector search
- RAGKnowledgeBase: Vector search + LLM generation
- HybridKnowledgeBase: Combined approach

Usage:
```python
from agentic_assistants.knowledge import get_knowledge_base

kb = get_knowledge_base("my_project", kb_type="hybrid")
kb.add_documents(["Document content..."])
results = kb.search("query")
answer = kb.query("What is...?")
```
""",
        "agents": """
Creating agents in the framework:

1. Using CrewAI:
```python
from agentic_assistants.adapters import CrewAIAdapter

adapter = CrewAIAdapter()
agent = adapter.create_ollama_agent(
    role="Researcher",
    goal="Find information",
    backstory="Expert researcher",
)
```

2. Using LangGraph:
```python
from agentic_assistants.adapters import LangGraphAdapter

adapter = LangGraphAdapter()
graph = adapter.create_state_graph(MyState)
```
""",
        "configuration": """
Configuration is managed through AgenticConfig:

```python
from agentic_assistants.config import AgenticConfig

config = AgenticConfig()
config.ollama.host  # Ollama server URL
config.assistant.model  # Framework assistant model
config.kubernetes.enabled  # K8s integration
```

Configuration files:
- config/global.yaml - Server-wide settings
- users/{user}/config.yaml - User preferences
- projects/{project}/config.yaml - Project settings
""",
        "training": """
Model training and fine-tuning:

```python
from agentic_assistants.training import TrainingConfig, TrainingJobManager

config = TrainingConfig(
    base_model="meta-llama/Llama-3.2-1B",
    method="lora",
    dataset_id="my-dataset",
)

job_manager = TrainingJobManager()
job = job_manager.create_job(config)
job_manager.start_job(job.id)
```

Supported methods: LoRA, QLoRA, Full fine-tuning
""",
        "deployment": """
Deploying agents and flows to Kubernetes:

```python
# Deploy a CrewAI crew
deployment = await adapter.deploy_crew(
    crew_id="my-crew",
    name="research-crew",
    model_endpoint="http://ollama.model-serving:11434",
)

# Deploy a LangGraph flow
deployment = await adapter.deploy_graph(
    flow_id="my-flow",
    name="chat-flow",
)
```

Prerequisites:
- Kubernetes cluster configured
- Model serving endpoint available
""",
    }

    def __init__(
        self,
        config: Optional[AgenticConfig] = None,
        knowledge_base: Optional["KnowledgeBase"] = None,
        memory: Optional["AgentMemory"] = None,
        usage_tracker: Optional["UsageTracker"] = None,
    ):
        """
        Initialize the framework guide module.
        
        Args:
            config: Configuration instance
            knowledge_base: RAG knowledge base with framework docs
            memory: Memory store
            usage_tracker: Usage tracker
        """
        self.config = config or AgenticConfig()
        self.knowledge_base = knowledge_base
        self.memory = memory
        self.usage_tracker = usage_tracker
        self._conversation_history: List[Dict[str, str]] = []
    
    def _get_model(self) -> str:
        """Get the model to use."""
        return self.config.assistant.model or self.config.llm.model or self.config.ollama.default_model
    
    def _call_llm(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: float = 0.5,
    ) -> str:
        """Make an LLM call."""
        system = system_message or self.DEFAULT_GUIDE_SYSTEM_PROMPT
        
        messages = [{"role": "system", "content": system}]
        messages.extend(self._conversation_history[-10:])
        messages.append({"role": "user", "content": prompt})
        
        provider_client = LLMProvider.from_config(
            self.config,
            provider=self.config.assistant.provider,
            model=self._get_model(),
            endpoint=self.config.assistant.endpoint,
            api_key_env=self.config.assistant.openai_api_key_env,
        )
        result = provider_client.chat(
            messages=messages,
            model=self._get_model(),
            temperature=temperature,
        )
        duration_ms = result.duration_ms
        content = result.content
        
        # Update conversation history
        self._conversation_history.append({"role": "user", "content": prompt})
        self._conversation_history.append({"role": "assistant", "content": content})
        
        # Track usage
        if self.usage_tracker:
            self.usage_tracker.track_model_inference(
                model=self._get_model(),
                duration_ms=duration_ms,
                prompt_tokens=result.prompt_tokens or 0,
                completion_tokens=result.completion_tokens or 0,
            )
        
        return content
    
    def _get_docs_context(self, query: str, top_k: int = 5) -> str:
        """Get relevant documentation context."""
        context_parts = []
        
        # First check built-in docs
        query_lower = query.lower()
        for topic, content in self.FRAMEWORK_DOCS.items():
            if topic in query_lower or any(
                kw in query_lower for kw in topic.split("_")
            ):
                context_parts.append(f"### {topic.replace('_', ' ').title()}\n{content}")
        
        # Then check RAG knowledge base
        if self.knowledge_base:
            try:
                start_time = time.time()
                results = self.knowledge_base.search(query, top_k=top_k)
                duration_ms = (time.time() - start_time) * 1000
                
                if results:
                    for r in results:
                        source = r.source or "Documentation"
                        context_parts.append(f"### {source}\n{r.content}")
                    
                    # Track RAG query
                    if self.usage_tracker:
                        self.usage_tracker.track_rag_query(
                            knowledge_base=self.config.assistant.docs_kb_name,
                            query=query[:200],
                            num_results=len(results),
                            duration_ms=duration_ms,
                            top_score=results[0].score if results else None,
                            used_for_generation=True,
                        )
            except Exception as e:
                logger.warning(f"Failed to get docs context: {e}")
        
        return "\n\n".join(context_parts)
    
    def get_help(
        self,
        question: str,
        include_examples: bool = True,
    ) -> str:
        """
        Get help for a framework-related question.
        
        Args:
            question: The help question
            include_examples: Whether to include code examples
            
        Returns:
            Help response
        """
        # Get relevant documentation
        docs_context = self._get_docs_context(question)
        
        prompt_parts = [f"User question: {question}"]
        
        if docs_context:
            prompt_parts.append(f"\nRelevant documentation:\n{docs_context}")
        
        if include_examples:
            prompt_parts.append("\nPlease include code examples where helpful.")
        
        prompt_parts.append("\nProvide a clear, helpful response.")
        
        prompt = "\n".join(prompt_parts)
        
        # Track user interaction
        if self.usage_tracker:
            self.usage_tracker.track_user_interaction(
                interaction_type="help_query",
                feature_used="framework_guide",
                input_length=len(question),
            )
        
        return self._call_llm(prompt)
    
    def get_configuration_help(
        self,
        section: str,
        specific_setting: Optional[str] = None,
    ) -> str:
        """
        Get help with configuration.
        
        Args:
            section: Configuration section (e.g., "kubernetes", "ollama")
            specific_setting: Specific setting to explain
            
        Returns:
            Configuration help
        """
        # Get current configuration for context
        config_dict = self.config.to_dict()
        section_config = config_dict.get(section, {})
        
        prompt = f"""Help the user understand and configure the '{section}' settings.

Current configuration for {section}:
{section_config}
"""
        
        if specific_setting:
            prompt += f"\nSpecifically explain the '{specific_setting}' setting."
        
        prompt += """

Please explain:
1. What this configuration section does
2. Key settings and their purposes
3. How to configure them properly
4. Common use cases and examples"""

        # Track user interaction
        if self.usage_tracker:
            self.usage_tracker.track_user_interaction(
                interaction_type="config_help",
                feature_used="framework_guide",
                input_length=len(section),
            )
        
        return self._call_llm(prompt)
    
    def get_deployment_guide(
        self,
        deployment_type: str,
        target: str = "kubernetes",
    ) -> str:
        """
        Get deployment guidance.
        
        Args:
            deployment_type: What to deploy (agent, flow, model)
            target: Deployment target (kubernetes, local)
            
        Returns:
            Deployment guide
        """
        docs_context = self._get_docs_context(f"deploy {deployment_type} {target}")
        
        prompt = f"""Provide a step-by-step guide for deploying a {deployment_type} to {target}.

{docs_context if docs_context else ''}

Include:
1. Prerequisites and requirements
2. Step-by-step instructions
3. Configuration examples
4. Common issues and solutions
5. Best practices"""

        # Track user interaction
        if self.usage_tracker:
            self.usage_tracker.track_user_interaction(
                interaction_type="deployment_guide",
                feature_used="framework_guide",
                input_length=len(deployment_type),
            )
        
        return self._call_llm(prompt)
    
    def get_adapter_guide(
        self,
        framework: str,
    ) -> str:
        """
        Get guide for using a specific framework adapter.
        
        Args:
            framework: Framework name (crewai, langgraph, etc.)
            
        Returns:
            Adapter usage guide
        """
        docs_context = self._get_docs_context(f"{framework} adapter agent")
        
        prompt = f"""Provide a comprehensive guide for using the {framework} adapter.

{docs_context if docs_context else ''}

Include:
1. Overview of the framework and its strengths
2. How to set up and configure the adapter
3. Creating agents/flows with the adapter
4. Using RAG and memory with the adapter
5. Deployment options
6. Code examples for common use cases"""

        # Track user interaction
        if self.usage_tracker:
            self.usage_tracker.track_user_interaction(
                interaction_type="adapter_guide",
                feature_used="framework_guide",
                input_length=len(framework),
            )
        
        return self._call_llm(prompt)
    
    def troubleshoot(
        self,
        issue: str,
        error_message: Optional[str] = None,
        context: Optional[str] = None,
    ) -> str:
        """
        Help troubleshoot an issue.
        
        Args:
            issue: Description of the issue
            error_message: Error message if any
            context: Additional context
            
        Returns:
            Troubleshooting guidance
        """
        prompt_parts = [f"Help troubleshoot this issue: {issue}"]
        
        if error_message:
            prompt_parts.append(f"\nError message:\n{error_message}")
        
        if context:
            prompt_parts.append(f"\nContext:\n{context}")
        
        prompt_parts.append("""

Please provide:
1. Likely cause of the issue
2. Step-by-step troubleshooting steps
3. Potential solutions
4. How to prevent this in the future""")
        
        prompt = "\n".join(prompt_parts)
        
        # Track user interaction
        if self.usage_tracker:
            self.usage_tracker.track_user_interaction(
                interaction_type="troubleshooting",
                feature_used="framework_guide",
                input_length=len(issue),
            )
        
        return self._call_llm(prompt)
    
    def get_best_practices(
        self,
        topic: str,
    ) -> str:
        """
        Get best practices for a topic.
        
        Args:
            topic: Topic to get best practices for
            
        Returns:
            Best practices guide
        """
        docs_context = self._get_docs_context(f"{topic} best practices")
        
        prompt = f"""Provide best practices for {topic} in the Agentic Assistants framework.

{docs_context if docs_context else ''}

Include:
1. Key principles
2. Recommended patterns
3. Common mistakes to avoid
4. Performance considerations
5. Security considerations
6. Example implementations"""

        # Track user interaction
        if self.usage_tracker:
            self.usage_tracker.track_user_interaction(
                interaction_type="best_practices",
                feature_used="framework_guide",
                input_length=len(topic),
            )
        
        return self._call_llm(prompt)
    
    def list_features(self) -> Dict[str, str]:
        """
        List available framework features.
        
        Returns:
            Dictionary of features and descriptions
        """
        return {
            "adapters": "Framework adapters for CrewAI, LangGraph, AutoGen, Google ADK, Agno, LangFlow",
            "knowledge_bases": "RAG-enabled knowledge bases for context-aware responses",
            "memory": "Persistent memory with mem0 integration",
            "training": "LLM training and fine-tuning with LoRA/QLoRA",
            "deployment": "Kubernetes deployment for agents and flows",
            "observability": "MLFlow tracking and OpenTelemetry tracing",
            "usage_analytics": "Usage tracking and meta-analysis for improvements",
            "pipelines": "Data pipelines for ingestion and processing",
        }
    
    def reset_conversation(self) -> None:
        """Reset the conversation history."""
        self._conversation_history = []
