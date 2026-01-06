"""
Task definitions for repository indexing workflow.

This module provides pre-defined tasks for:
- Repository analysis
- Documentation generation
- Code annotation
- Vector store indexing

Example:
    >>> from agentic_assistants.crews.tasks import AnalyzeRepositoryTask
    >>> 
    >>> task = AnalyzeRepositoryTask.create(
    ...     agent=analyzer_agent,
    ...     repo_path="./my-project"
    ... )
"""

from typing import Any, Optional

from agentic_assistants.config import AgenticConfig
from agentic_assistants.core.telemetry import trace_function
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


class TaskFactory:
    """
    Factory for creating CrewAI tasks.
    
    This factory standardizes task creation with:
    - Consistent parameter handling
    - Telemetry integration
    - Output validation
    """
    
    def __init__(self, config: Optional[AgenticConfig] = None):
        """
        Initialize the task factory.
        
        Args:
            config: Configuration instance
        """
        self.config = config or AgenticConfig()
    
    @trace_function(attributes={"component": "task_factory"})
    def create_task(
        self,
        description: str,
        agent: Any,
        expected_output: str,
        context: Optional[list] = None,
        async_execution: bool = False,
        output_file: Optional[str] = None,
        output_json: Optional[Any] = None,
        **kwargs,
    ) -> Any:
        """
        Create a CrewAI task.
        
        Args:
            description: Task description
            agent: Agent to perform the task
            expected_output: Description of expected output
            context: Context tasks (dependencies)
            async_execution: Run asynchronously
            output_file: File to write output to
            output_json: Pydantic model for JSON output
            **kwargs: Additional task parameters
        
        Returns:
            Configured Task instance
        """
        try:
            from crewai import Task
        except ImportError as e:
            raise ImportError(
                "CrewAI is required. Install with: pip install crewai"
            ) from e
        
        task_kwargs = {
            "description": description,
            "agent": agent,
            "expected_output": expected_output,
            "async_execution": async_execution,
            **kwargs,
        }
        
        if context:
            task_kwargs["context"] = context
        
        if output_file:
            task_kwargs["output_file"] = output_file
        
        if output_json:
            task_kwargs["output_json"] = output_json
        
        task = Task(**task_kwargs)
        logger.debug(f"Created task for agent: {agent.role}")
        return task


class AnalyzeRepositoryTask:
    """
    Task for analyzing repository structure.
    
    This task instructs an agent to:
    1. Scan the repository directory structure
    2. Identify programming languages and file types
    3. Detect frameworks and libraries
    4. Map code dependencies and relationships
    5. Assess overall architecture
    """
    
    DESCRIPTION_TEMPLATE = """Analyze the repository at: {repo_path}

Your comprehensive analysis should include:

1. **Directory Structure Overview**
   - List all major directories and their purposes
   - Identify entry points (main files, index files)
   - Note any configuration files

2. **Language & Technology Detection**
   - List all programming languages found
   - Identify frameworks and libraries used
   - Note build tools and package managers

3. **Architecture Analysis**
   - Identify architectural patterns (MVC, microservices, etc.)
   - Map module dependencies
   - Note any design patterns used

4. **Code Organization**
   - How is the code structured?
   - Are there clear separation of concerns?
   - What naming conventions are used?

5. **Quality Indicators**
   - Presence of tests
   - Documentation coverage
   - Code style consistency

Use the directory_list and file_reader tools to explore the repository.
Use the code_parser tool to analyze code structure.

Provide a detailed, structured analysis report."""

    EXPECTED_OUTPUT = """A comprehensive JSON report containing:
- repository_name: Name of the repository
- languages: List of programming languages with file counts
- frameworks: Detected frameworks and libraries
- architecture: Description of architectural patterns
- directories: Map of major directories and their purposes
- entry_points: Main files and entry points
- dependencies: External dependencies
- quality_metrics: Test coverage, documentation presence
- recommendations: Suggestions for improvement"""
    
    @classmethod
    def create(
        cls,
        agent: Any,
        repo_path: str,
        config: Optional[AgenticConfig] = None,
        context: Optional[list] = None,
        **kwargs,
    ) -> Any:
        """
        Create a repository analysis task.
        
        Args:
            agent: Agent to perform the task
            repo_path: Path to the repository
            config: Configuration instance
            context: Context tasks
            **kwargs: Additional task parameters
        
        Returns:
            Configured Task instance
        """
        factory = TaskFactory(config)
        
        description = cls.DESCRIPTION_TEMPLATE.format(repo_path=repo_path)
        
        return factory.create_task(
            description=description,
            agent=agent,
            expected_output=cls.EXPECTED_OUTPUT,
            context=context,
            **kwargs,
        )


class GenerateDocumentationTask:
    """
    Task for generating documentation.
    
    This task instructs an agent to:
    1. Review code analysis results
    2. Generate missing documentation
    3. Create code explanations
    4. Produce summary descriptions
    """
    
    DESCRIPTION_TEMPLATE = """Based on the repository analysis, generate documentation for the codebase at: {repo_path}

Using the analysis results, create comprehensive documentation:

1. **Repository Overview**
   - What does this project do?
   - Who is it for?
   - Key features and capabilities

2. **Getting Started**
   - Prerequisites
   - Installation steps
   - Basic usage examples

3. **Architecture Documentation**
   - System overview diagram description
   - Component descriptions
   - Data flow explanations

4. **Module Documentation**
   For each major module/package:
   - Purpose and responsibility
   - Key classes and functions
   - Usage examples

5. **API Documentation**
   For public interfaces:
   - Function signatures
   - Parameter descriptions
   - Return value documentation
   - Usage examples

Focus on clarity and usefulness. The documentation should help new developers
understand and work with the codebase quickly.

Use file_reader to examine code files for accurate documentation.
Use code_parser to extract function and class information."""

    EXPECTED_OUTPUT = """Comprehensive documentation containing:
- overview: Project overview and purpose
- getting_started: Setup and installation guide
- architecture: Architecture documentation
- modules: Per-module documentation
- api_reference: API documentation for public interfaces
- examples: Usage examples
- glossary: Key terms and definitions"""
    
    @classmethod
    def create(
        cls,
        agent: Any,
        repo_path: str,
        config: Optional[AgenticConfig] = None,
        context: Optional[list] = None,
        **kwargs,
    ) -> Any:
        """
        Create a documentation generation task.
        
        Args:
            agent: Agent to perform the task
            repo_path: Path to the repository
            config: Configuration instance
            context: Context tasks (e.g., analysis task)
            **kwargs: Additional task parameters
        
        Returns:
            Configured Task instance
        """
        factory = TaskFactory(config)
        
        description = cls.DESCRIPTION_TEMPLATE.format(repo_path=repo_path)
        
        return factory.create_task(
            description=description,
            agent=agent,
            expected_output=cls.EXPECTED_OUTPUT,
            context=context,
            **kwargs,
        )


class AnnotateCodeTask:
    """
    Task for creating code annotations.
    
    This task instructs an agent to:
    1. Review code files
    2. Create semantic annotations
    3. Add searchable metadata
    4. Categorize code by functionality
    """
    
    DESCRIPTION_TEMPLATE = """Create rich metadata annotations for the codebase at: {repo_path}

Based on the analysis and documentation, create searchable annotations:

1. **File-Level Annotations**
   For each significant file:
   - purpose: What does this file do?
   - category: What category does it belong to? (api, model, util, config, etc.)
   - keywords: Searchable keywords
   - dependencies: What does it depend on?
   - complexity: Simple, moderate, or complex

2. **Function/Class Annotations**
   For key functions and classes:
   - purpose: One-line description
   - functionality: What it does in detail
   - parameters: Input descriptions
   - returns: Output description
   - side_effects: Any side effects
   - related: Related code entities

3. **Semantic Tags**
   Add semantic tags like:
   - authentication, authorization, security
   - data-access, database, storage
   - api, endpoint, route
   - model, schema, validation
   - utility, helper, common
   - configuration, settings
   - testing, mock, fixture

4. **Search Optimization**
   Create metadata optimized for semantic search:
   - Descriptive summaries
   - Alternative terminology
   - Use case descriptions
   - Problem-solution mappings

Output the annotations in a format ready for vector store indexing.

Use file_reader and code_parser to examine the code.
The annotations will be used to make the codebase searchable via semantic search."""

    EXPECTED_OUTPUT = """Structured annotations containing:
- files: List of file annotations with metadata
- functions: List of function annotations
- classes: List of class annotations
- relationships: Dependency graph annotations
- search_index: Optimized search metadata
Each annotation should include: id, content, metadata with purpose, category, keywords, and tags."""
    
    @classmethod
    def create(
        cls,
        agent: Any,
        repo_path: str,
        config: Optional[AgenticConfig] = None,
        context: Optional[list] = None,
        **kwargs,
    ) -> Any:
        """
        Create a code annotation task.
        
        Args:
            agent: Agent to perform the task
            repo_path: Path to the repository
            config: Configuration instance
            context: Context tasks
            **kwargs: Additional task parameters
        
        Returns:
            Configured Task instance
        """
        factory = TaskFactory(config)
        
        description = cls.DESCRIPTION_TEMPLATE.format(repo_path=repo_path)
        
        return factory.create_task(
            description=description,
            agent=agent,
            expected_output=cls.EXPECTED_OUTPUT,
            context=context,
            **kwargs,
        )


class IndexToVectorStoreTask:
    """
    Task for indexing content to vector store.
    
    This task instructs an agent to:
    1. Collect all annotated content
    2. Format for vector storage
    3. Add to vector database
    4. Verify indexing success
    """
    
    DESCRIPTION_TEMPLATE = """Index the analyzed and annotated content to the vector store.

Collection: {collection}
Repository: {repo_path}

Using the analysis, documentation, and annotations from previous tasks:

1. **Prepare Documents**
   Create vector store documents with:
   - Unique IDs based on file path and content hash
   - Rich text content combining code and documentation
   - Comprehensive metadata for filtering

2. **Document Structure**
   Each document should contain:
   - id: Unique identifier
   - content: Searchable text (code + documentation + annotations)
   - metadata:
     - file_path: Source file path
     - language: Programming language
     - category: Code category
     - keywords: Search keywords
     - purpose: Purpose description
     - indexed_at: Timestamp

3. **Chunking Strategy**
   - Split large files into logical chunks
   - Keep related code together
   - Include context in each chunk

4. **Index and Verify**
   - Add documents to collection '{collection}'
   - Verify successful indexing
   - Report any errors

Use the vector_store tool with action='add' to index documents.
Use action='count' to verify the final document count.

Provide a summary of what was indexed."""

    EXPECTED_OUTPUT = """Indexing report containing:
- collection: Name of the collection used
- documents_indexed: Number of documents added
- total_chunks: Total chunks created
- by_language: Breakdown by programming language
- by_category: Breakdown by code category
- errors: Any indexing errors
- verification: Confirmation of successful indexing"""
    
    @classmethod
    def create(
        cls,
        agent: Any,
        repo_path: str,
        collection: str = "default",
        config: Optional[AgenticConfig] = None,
        context: Optional[list] = None,
        **kwargs,
    ) -> Any:
        """
        Create a vector store indexing task.
        
        Args:
            agent: Agent to perform the task
            repo_path: Path to the repository
            collection: Vector store collection name
            config: Configuration instance
            context: Context tasks
            **kwargs: Additional task parameters
        
        Returns:
            Configured Task instance
        """
        factory = TaskFactory(config)
        
        description = cls.DESCRIPTION_TEMPLATE.format(
            repo_path=repo_path,
            collection=collection,
        )
        
        return factory.create_task(
            description=description,
            agent=agent,
            expected_output=cls.EXPECTED_OUTPUT,
            context=context,
            **kwargs,
        )


def create_repository_indexing_tasks(
    agents: dict,
    repo_path: str,
    collection: str = "default",
    config: Optional[AgenticConfig] = None,
) -> list:
    """
    Create all tasks for repository indexing workflow.
    
    Args:
        agents: Dictionary of agents from create_repository_indexing_agents
        repo_path: Path to the repository
        collection: Vector store collection name
        config: Configuration instance
    
    Returns:
        List of tasks in execution order
    """
    config = config or AgenticConfig()
    
    # Task 1: Analyze repository
    analyze_task = AnalyzeRepositoryTask.create(
        agent=agents["analyzer"],
        repo_path=repo_path,
        config=config,
    )
    
    # Task 2: Generate documentation (depends on analysis)
    document_task = GenerateDocumentationTask.create(
        agent=agents["documenter"],
        repo_path=repo_path,
        config=config,
        context=[analyze_task],
    )
    
    # Task 3: Annotate code (depends on analysis and documentation)
    annotate_task = AnnotateCodeTask.create(
        agent=agents["annotator"],
        repo_path=repo_path,
        config=config,
        context=[analyze_task, document_task],
    )
    
    # Task 4: Index to vector store (depends on all previous)
    index_task = IndexToVectorStoreTask.create(
        agent=agents["orchestrator"],
        repo_path=repo_path,
        collection=collection,
        config=config,
        context=[analyze_task, document_task, annotate_task],
    )
    
    return [analyze_task, document_task, annotate_task, index_task]

