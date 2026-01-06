"""
Repository Indexing Crew - Multi-agent system for code analysis and indexing.

This module provides a complete CrewAI crew for:
- Analyzing repository structure and code
- Generating documentation
- Creating semantic annotations
- Indexing content to vector stores

Example:
    >>> from agentic_assistants.crews import RepositoryIndexingCrew
    >>> 
    >>> crew = RepositoryIndexingCrew()
    >>> result = crew.run(
    ...     repo_path="./my-project",
    ...     collection="my-project",
    ...     experiment_name="indexing-v1"
    ... )
    >>> print(result.stats)
"""

import json
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, Union

from agentic_assistants.config import AgenticConfig
from agentic_assistants.core.mlflow_tracker import MLFlowTracker
from agentic_assistants.core.telemetry import TelemetryManager, trace_function
from agentic_assistants.crews.agents import create_repository_indexing_agents
from agentic_assistants.crews.tasks import create_repository_indexing_tasks
from agentic_assistants.utils.logging import get_logger
from agentic_assistants.vectordb.base import VectorStore

logger = get_logger(__name__)


@dataclass
class IndexingResult:
    """
    Result from a repository indexing run.
    
    Attributes:
        success: Whether the indexing completed successfully
        repo_path: Path to the indexed repository
        collection: Vector store collection used
        crew_output: Raw output from the CrewAI crew
        stats: Indexing statistics
        duration_seconds: Total execution time
        errors: Any errors encountered
        experiment_run_id: MLFlow run ID if tracking was enabled
    """
    
    success: bool
    repo_path: str
    collection: str
    crew_output: Any = None
    stats: dict = field(default_factory=dict)
    duration_seconds: float = 0.0
    errors: list = field(default_factory=list)
    experiment_run_id: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "repo_path": self.repo_path,
            "collection": self.collection,
            "stats": self.stats,
            "duration_seconds": self.duration_seconds,
            "errors": self.errors,
            "experiment_run_id": self.experiment_run_id,
        }
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


class RepositoryIndexingCrew:
    """
    Multi-agent crew for repository analysis and indexing.
    
    This crew orchestrates multiple specialized agents to:
    1. Analyze repository structure and code quality
    2. Generate comprehensive documentation
    3. Create semantic annotations for searchability
    4. Index everything into vector stores
    
    The crew integrates with:
    - MLFlow for experiment tracking
    - OpenTelemetry for distributed tracing
    - LanceDB/ChromaDB for vector storage
    
    Attributes:
        config: Framework configuration
        tracker: MLFlow experiment tracker
        telemetry: OpenTelemetry manager
        vector_store: Vector store instance
    
    Example:
        >>> crew = RepositoryIndexingCrew(
        ...     model="llama3.2",
        ...     vector_backend="lancedb"
        ... )
        >>> 
        >>> # Run with MLFlow tracking
        >>> result = crew.run(
        ...     repo_path="./my-project",
        ...     collection="my-project-index",
        ...     experiment_name="repo-indexing"
        ... )
        >>> 
        >>> # Check results
        >>> print(f"Indexed: {result.stats.get('documents_indexed', 0)} documents")
        >>> print(f"Duration: {result.duration_seconds:.2f}s")
    """
    
    def __init__(
        self,
        config: Optional[AgenticConfig] = None,
        model: Optional[str] = None,
        vector_backend: Optional[str] = None,
        embedding_model: Optional[str] = None,
        verbose: bool = True,
    ):
        """
        Initialize the Repository Indexing Crew.
        
        Args:
            config: Framework configuration
            model: LLM model for agents (default from config)
            vector_backend: Vector store backend ("lancedb" or "chroma")
            embedding_model: Embedding model name
            verbose: Enable verbose output
        """
        self.config = config or AgenticConfig()
        self.model = model or self.config.ollama.default_model
        self.vector_backend = vector_backend or self.config.vectordb.backend
        self.embedding_model = embedding_model or self.config.vectordb.embedding_model
        self.verbose = verbose
        
        # Initialize observability
        self.tracker = MLFlowTracker(self.config)
        self.telemetry = TelemetryManager(self.config)
        
        if self.config.telemetry_enabled:
            self.telemetry.initialize()
        
        # Lazy-initialized components
        self._vector_store: Optional[VectorStore] = None
        self._crew = None
        
        logger.info(
            f"Initialized RepositoryIndexingCrew "
            f"(model={self.model}, backend={self.vector_backend})"
        )
    
    @property
    def vector_store(self) -> VectorStore:
        """Get or create the vector store."""
        if self._vector_store is None:
            self._vector_store = VectorStore.create(
                backend=self.vector_backend,
                config=self.config,
                embedding_model=self.embedding_model,
            )
        return self._vector_store
    
    def _create_crew(self, repo_path: str, collection: str) -> Any:
        """
        Create the CrewAI crew instance.
        
        Args:
            repo_path: Path to repository
            collection: Vector store collection
        
        Returns:
            Configured Crew instance
        """
        try:
            from crewai import Crew, Process
        except ImportError as e:
            raise ImportError(
                "CrewAI is required. Install with: pip install crewai"
            ) from e
        
        # Create agents with repo_path as base
        agents = create_repository_indexing_agents(
            config=self.config,
            model=self.model,
            base_path=repo_path,
        )
        
        # Create tasks
        tasks = create_repository_indexing_tasks(
            agents=agents,
            repo_path=repo_path,
            collection=collection,
            config=self.config,
        )
        
        # Create crew
        crew = Crew(
            agents=list(agents.values()),
            tasks=tasks,
            process=Process.sequential,
            verbose=self.verbose,
        )
        
        return crew
    
    @trace_function(
        span_name="repository_indexing_crew.run",
        attributes={"component": "repository_indexing_crew"},
    )
    def run(
        self,
        repo_path: Union[str, Path],
        collection: str = "default",
        experiment_name: Optional[str] = None,
        run_name: Optional[str] = None,
        tags: Optional[dict[str, str]] = None,
        force_reindex: bool = False,
    ) -> IndexingResult:
        """
        Run the repository indexing crew.
        
        This method:
        1. Creates the multi-agent crew
        2. Runs analysis, documentation, annotation tasks
        3. Indexes results to vector store
        4. Tracks everything in MLFlow
        5. Returns comprehensive results
        
        Args:
            repo_path: Path to the repository to index
            collection: Vector store collection name
            experiment_name: MLFlow experiment name
            run_name: Name for this run
            tags: Additional tags for tracking
            force_reindex: Force re-indexing even if already indexed
        
        Returns:
            IndexingResult with statistics and outputs
        
        Raises:
            ValueError: If repo_path doesn't exist
            RuntimeError: If crew execution fails
        """
        start_time = time.time()
        
        # Validate repo path
        repo_path = Path(repo_path).resolve()
        if not repo_path.exists():
            raise ValueError(f"Repository path does not exist: {repo_path}")
        
        if not repo_path.is_dir():
            raise ValueError(f"Repository path is not a directory: {repo_path}")
        
        # Set up result
        result = IndexingResult(
            success=False,
            repo_path=str(repo_path),
            collection=collection,
        )
        
        # Set up MLFlow tracking
        if experiment_name:
            self.tracker.experiment_name = experiment_name
        
        actual_run_name = run_name or f"index-{repo_path.name}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # Build parameters
        params = {
            "repo_path": str(repo_path),
            "collection": collection,
            "model": self.model,
            "vector_backend": self.vector_backend,
            "embedding_model": self.embedding_model,
            "force_reindex": force_reindex,
        }
        
        # Build tags
        all_tags = {
            "crew": "repository_indexing",
            "repo_name": repo_path.name,
        }
        if tags:
            all_tags.update(tags)
        
        logger.info(f"Starting repository indexing: {repo_path}")
        logger.info(f"Collection: {collection}, Model: {self.model}")
        
        with self.tracker.start_run(run_name=actual_run_name, tags=all_tags) as mlflow_run:
            with self.telemetry.span(
                "repository_indexing",
                attributes={
                    "repo_path": str(repo_path),
                    "collection": collection,
                    "model": self.model,
                },
            ) as span:
                try:
                    # Log parameters
                    self.tracker.log_params(params)
                    
                    # Count files to index
                    file_count = self._count_files(repo_path)
                    span.set_attribute("file_count", file_count)
                    self.tracker.log_metric("files_to_index", file_count)
                    
                    # Create and run crew
                    logger.info("Creating indexing crew...")
                    crew = self._create_crew(str(repo_path), collection)
                    
                    logger.info("Running crew...")
                    with self.telemetry.span("crew_execution"):
                        crew_output = crew.kickoff()
                    
                    result.crew_output = crew_output
                    
                    # Process results
                    result.stats = self._process_crew_output(crew_output, collection)
                    
                    # Log success metrics
                    duration = time.time() - start_time
                    result.duration_seconds = duration
                    result.success = True
                    
                    self.tracker.log_metrics({
                        "duration_seconds": duration,
                        "success": 1,
                        "documents_indexed": result.stats.get("documents_indexed", 0),
                    })
                    
                    # Log output as artifact
                    if isinstance(crew_output, str):
                        self.tracker.log_text(crew_output, "output/crew_result.txt")
                    
                    self.tracker.log_dict(result.stats, "output/indexing_stats.json")
                    
                    span.set_attribute("success", True)
                    span.set_attribute("documents_indexed", result.stats.get("documents_indexed", 0))
                    
                    logger.info(
                        f"Indexing complete: {result.stats.get('documents_indexed', 0)} documents "
                        f"in {duration:.2f}s"
                    )
                    
                except Exception as e:
                    duration = time.time() - start_time
                    result.duration_seconds = duration
                    result.errors.append(str(e))
                    
                    self.tracker.log_metrics({
                        "duration_seconds": duration,
                        "success": 0,
                    })
                    self.tracker.set_tag("error", str(e)[:200])
                    
                    span.set_attribute("success", False)
                    span.set_attribute("error", str(e))
                    span.record_exception(e)
                    
                    logger.error(f"Indexing failed: {e}")
                    raise RuntimeError(f"Repository indexing failed: {e}") from e
                
                finally:
                    if mlflow_run:
                        result.experiment_run_id = mlflow_run.info.run_id
        
        return result
    
    def _count_files(self, repo_path: Path) -> int:
        """Count files in the repository."""
        from agentic_assistants.indexing.codebase import CodebaseIndexer
        
        patterns = CodebaseIndexer.DEFAULT_CODE_PATTERNS
        count = 0
        
        for pattern in patterns:
            count += len(list(repo_path.glob(f"**/{pattern}")))
        
        return count
    
    def _process_crew_output(self, output: Any, collection: str) -> dict:
        """
        Process crew output and extract statistics.
        
        Args:
            output: Raw crew output
            collection: Vector store collection
        
        Returns:
            Statistics dictionary
        """
        stats = {
            "collection": collection,
            "processed_at": datetime.utcnow().isoformat(),
        }
        
        # Try to parse JSON from output
        if isinstance(output, str):
            try:
                # Look for JSON in the output
                import re
                json_match = re.search(r'\{[\s\S]*\}', output)
                if json_match:
                    parsed = json.loads(json_match.group())
                    stats.update(parsed)
            except json.JSONDecodeError:
                pass
        
        # Get actual count from vector store
        try:
            stats["documents_indexed"] = self.vector_store.count(collection)
        except Exception:
            stats["documents_indexed"] = 0
        
        return stats
    
    def search(
        self,
        query: str,
        collection: str = "default",
        top_k: int = 5,
    ) -> list:
        """
        Search the indexed repository.
        
        Args:
            query: Search query
            collection: Collection to search
            top_k: Number of results
        
        Returns:
            List of search results
        """
        return self.vector_store.search(
            query=query,
            collection=collection,
            top_k=top_k,
        )
    
    def get_stats(self, collection: str = "default") -> dict:
        """
        Get statistics for an indexed collection.
        
        Args:
            collection: Collection name
        
        Returns:
            Statistics dictionary
        """
        return {
            "collection": collection,
            "document_count": self.vector_store.count(collection),
            "vector_backend": self.vector_backend,
            "embedding_model": self.embedding_model,
        }
    
    def clear(self, collection: str = "default") -> bool:
        """
        Clear an indexed collection.
        
        Args:
            collection: Collection to clear
        
        Returns:
            True if cleared successfully
        """
        return self.vector_store.delete_collection(collection)


def run_repository_indexing(
    repo_path: Union[str, Path],
    collection: str = "default",
    model: Optional[str] = None,
    experiment_name: Optional[str] = None,
    config: Optional[AgenticConfig] = None,
    verbose: bool = True,
) -> IndexingResult:
    """
    Convenience function to run repository indexing.
    
    Args:
        repo_path: Path to the repository
        collection: Vector store collection
        model: LLM model name
        experiment_name: MLFlow experiment name
        config: Configuration instance
        verbose: Enable verbose output
    
    Returns:
        IndexingResult with statistics
    
    Example:
        >>> from agentic_assistants.crews import run_repository_indexing
        >>> 
        >>> result = run_repository_indexing(
        ...     repo_path="./my-project",
        ...     collection="my-project",
        ...     experiment_name="indexing-run"
        ... )
    """
    crew = RepositoryIndexingCrew(
        config=config,
        model=model,
        verbose=verbose,
    )
    
    return crew.run(
        repo_path=repo_path,
        collection=collection,
        experiment_name=experiment_name,
    )

