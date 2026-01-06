"""
Specialized CrewAI agents for repository indexing.

This module provides pre-configured agents for:
- Code analysis
- Documentation generation
- Code annotation
- Workflow orchestration

Example:
    >>> from agentic_assistants.crews.agents import CodeAnalyzerAgent
    >>> 
    >>> agent = CodeAnalyzerAgent.create(model="llama3.2")
"""

from typing import Any, Optional

from agentic_assistants.config import AgenticConfig
from agentic_assistants.core.telemetry import trace_function
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


class AgentFactory:
    """
    Factory for creating specialized CrewAI agents.
    
    This factory handles:
    - LLM configuration (Ollama integration)
    - Tool assignment
    - Telemetry setup
    """
    
    def __init__(self, config: Optional[AgenticConfig] = None):
        """
        Initialize the agent factory.
        
        Args:
            config: Configuration instance
        """
        self.config = config or AgenticConfig()
    
    def _get_llm(self, model: Optional[str] = None):
        """Get configured LLM instance."""
        try:
            from langchain_ollama import ChatOllama
            
            return ChatOllama(
                model=model or self.config.ollama.default_model,
                base_url=self.config.ollama.host,
            )
        except ImportError:
            logger.warning("langchain-ollama not installed, using default LLM")
            return None
    
    @trace_function(attributes={"component": "agent_factory"})
    def create_agent(
        self,
        role: str,
        goal: str,
        backstory: str,
        tools: Optional[list] = None,
        model: Optional[str] = None,
        verbose: bool = True,
        allow_delegation: bool = False,
        **kwargs,
    ) -> Any:
        """
        Create a CrewAI agent.
        
        Args:
            role: Agent's role
            goal: Agent's goal
            backstory: Agent's backstory
            tools: List of tools for the agent
            model: LLM model name
            verbose: Enable verbose output
            allow_delegation: Allow task delegation
            **kwargs: Additional agent parameters
        
        Returns:
            Configured Agent instance
        """
        try:
            from crewai import Agent
        except ImportError as e:
            raise ImportError(
                "CrewAI is required. Install with: pip install crewai"
            ) from e
        
        llm = self._get_llm(model)
        
        agent_kwargs = {
            "role": role,
            "goal": goal,
            "backstory": backstory,
            "verbose": verbose,
            "allow_delegation": allow_delegation,
            **kwargs,
        }
        
        if llm:
            agent_kwargs["llm"] = llm
        
        if tools:
            agent_kwargs["tools"] = tools
        
        agent = Agent(**agent_kwargs)
        logger.debug(f"Created agent: {role}")
        return agent


class CodeAnalyzerAgent:
    """
    Agent specialized in analyzing code structure and quality.
    
    This agent can:
    - Identify programming languages and frameworks
    - Parse code structure (functions, classes, modules)
    - Assess code complexity and patterns
    - Identify dependencies and relationships
    """
    
    ROLE = "Senior Code Analyst"
    GOAL = (
        "Analyze repository structure, identify programming languages, frameworks, "
        "and key architectural patterns. Produce a comprehensive analysis of the codebase."
    )
    BACKSTORY = """You are an expert software architect with 15+ years of experience 
    across multiple programming languages and paradigms. You excel at quickly 
    understanding codebases, identifying patterns, and documenting software architecture.
    You have deep knowledge of design patterns, code quality metrics, and best practices.
    You always provide structured, detailed analysis that helps developers understand
    the codebase quickly."""
    
    @classmethod
    def create(
        cls,
        config: Optional[AgenticConfig] = None,
        model: Optional[str] = None,
        tools: Optional[list] = None,
        **kwargs,
    ) -> Any:
        """
        Create a Code Analyzer agent.
        
        Args:
            config: Configuration instance
            model: LLM model name
            tools: Additional tools
            **kwargs: Additional agent parameters
        
        Returns:
            Configured Agent instance
        """
        factory = AgentFactory(config)
        
        # Default tools for code analysis
        if tools is None:
            from agentic_assistants.crews.tools import (
                FileReaderTool,
                DirectoryListTool,
                CodeParserTool,
            )
            tools = [
                FileReaderTool(),
                DirectoryListTool(),
                CodeParserTool(),
            ]
        
        return factory.create_agent(
            role=cls.ROLE,
            goal=cls.GOAL,
            backstory=cls.BACKSTORY,
            tools=tools,
            model=model,
            **kwargs,
        )


class DocumentationGeneratorAgent:
    """
    Agent specialized in generating documentation.
    
    This agent can:
    - Generate docstrings and comments
    - Create README files
    - Document APIs and interfaces
    - Explain complex code logic
    """
    
    ROLE = "Technical Documentation Specialist"
    GOAL = (
        "Generate clear, comprehensive documentation for code including docstrings, "
        "README content, API documentation, and explanatory comments."
    )
    BACKSTORY = """You are a skilled technical writer with expertise in software 
    documentation. You have worked with development teams at major tech companies,
    creating documentation that is both accurate and accessible. You understand
    the importance of good documentation for code maintainability and team
    collaboration. You follow documentation best practices and style guides,
    always aiming for clarity and completeness."""
    
    @classmethod
    def create(
        cls,
        config: Optional[AgenticConfig] = None,
        model: Optional[str] = None,
        tools: Optional[list] = None,
        **kwargs,
    ) -> Any:
        """
        Create a Documentation Generator agent.
        
        Args:
            config: Configuration instance
            model: LLM model name
            tools: Additional tools
            **kwargs: Additional agent parameters
        
        Returns:
            Configured Agent instance
        """
        factory = AgentFactory(config)
        
        if tools is None:
            from agentic_assistants.crews.tools import (
                FileReaderTool,
                CodeParserTool,
            )
            tools = [
                FileReaderTool(),
                CodeParserTool(),
            ]
        
        return factory.create_agent(
            role=cls.ROLE,
            goal=cls.GOAL,
            backstory=cls.BACKSTORY,
            tools=tools,
            model=model,
            **kwargs,
        )


class CodeAnnotatorAgent:
    """
    Agent specialized in creating metadata annotations.
    
    This agent can:
    - Add semantic tags to code
    - Identify code purpose and intent
    - Create searchable metadata
    - Categorize code by functionality
    """
    
    ROLE = "Code Metadata Annotator"
    GOAL = (
        "Create rich metadata annotations for code including purpose descriptions, "
        "functionality tags, complexity assessments, and searchable keywords."
    )
    BACKSTORY = """You are a meticulous software cataloger who specializes in 
    organizing and annotating codebases for maximum searchability and discoverability.
    You have extensive experience with knowledge management systems and understand
    how to create metadata that makes code easy to find and understand. You think
    carefully about what information future developers will need when searching
    for code, and you create annotations that capture both the what and why of code."""
    
    @classmethod
    def create(
        cls,
        config: Optional[AgenticConfig] = None,
        model: Optional[str] = None,
        tools: Optional[list] = None,
        **kwargs,
    ) -> Any:
        """
        Create a Code Annotator agent.
        
        Args:
            config: Configuration instance
            model: LLM model name
            tools: Additional tools
            **kwargs: Additional agent parameters
        
        Returns:
            Configured Agent instance
        """
        factory = AgentFactory(config)
        
        if tools is None:
            from agentic_assistants.crews.tools import (
                FileReaderTool,
                CodeParserTool,
                VectorStoreTool,
            )
            tools = [
                FileReaderTool(),
                CodeParserTool(),
                VectorStoreTool(config=config),
            ]
        
        return factory.create_agent(
            role=cls.ROLE,
            goal=cls.GOAL,
            backstory=cls.BACKSTORY,
            tools=tools,
            model=model,
            **kwargs,
        )


class OrchestratorAgent:
    """
    Agent that coordinates the indexing workflow.
    
    This agent can:
    - Plan the analysis workflow
    - Coordinate other agents
    - Manage the indexing pipeline
    - Handle errors and retries
    """
    
    ROLE = "Repository Indexing Orchestrator"
    GOAL = (
        "Coordinate the repository indexing workflow, ensuring all files are properly "
        "analyzed, documented, annotated, and stored in the vector database."
    )
    BACKSTORY = """You are a seasoned project manager with deep technical expertise.
    You excel at breaking down complex tasks into manageable pieces and coordinating
    teams to achieve goals efficiently. You understand both the technical requirements
    of code analysis and the practical needs of making code discoverable. You always
    ensure work is completed thoroughly and verify results meet quality standards."""
    
    @classmethod
    def create(
        cls,
        config: Optional[AgenticConfig] = None,
        model: Optional[str] = None,
        tools: Optional[list] = None,
        **kwargs,
    ) -> Any:
        """
        Create an Orchestrator agent.
        
        Args:
            config: Configuration instance
            model: LLM model name
            tools: Additional tools
            **kwargs: Additional agent parameters
        
        Returns:
            Configured Agent instance
        """
        factory = AgentFactory(config)
        
        # Orchestrator gets all tools
        if tools is None:
            from agentic_assistants.crews.tools import create_all_tools
            tools = create_all_tools(config=config)
        
        return factory.create_agent(
            role=cls.ROLE,
            goal=cls.GOAL,
            backstory=cls.BACKSTORY,
            tools=tools,
            model=model,
            allow_delegation=True,  # Orchestrator can delegate
            **kwargs,
        )


def create_repository_indexing_agents(
    config: Optional[AgenticConfig] = None,
    model: Optional[str] = None,
    base_path: Optional[str] = None,
) -> dict:
    """
    Create all agents needed for repository indexing.
    
    Args:
        config: Configuration instance
        model: LLM model name
        base_path: Base path for file operations
    
    Returns:
        Dictionary of agent instances
    """
    config = config or AgenticConfig()
    
    # Create tools with base path
    from agentic_assistants.crews.tools import (
        FileReaderTool,
        DirectoryListTool,
        CodeParserTool,
        VectorStoreTool,
    )
    
    file_reader = FileReaderTool(base_path=base_path)
    dir_list = DirectoryListTool(base_path=base_path)
    code_parser = CodeParserTool()
    vector_store = VectorStoreTool(config=config)
    
    return {
        "analyzer": CodeAnalyzerAgent.create(
            config=config,
            model=model,
            tools=[file_reader, dir_list, code_parser],
        ),
        "documenter": DocumentationGeneratorAgent.create(
            config=config,
            model=model,
            tools=[file_reader, code_parser],
        ),
        "annotator": CodeAnnotatorAgent.create(
            config=config,
            model=model,
            tools=[file_reader, code_parser, vector_store],
        ),
        "orchestrator": OrchestratorAgent.create(
            config=config,
            model=model,
            tools=[file_reader, dir_list, code_parser, vector_store],
        ),
    }

