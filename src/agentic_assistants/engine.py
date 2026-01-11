"""
Agentic Engine - Unified programmatic interface.

This module provides the AgenticEngine class, a facade that
orchestrates all framework components.

Example:
    >>> from agentic_assistants import AgenticEngine
    >>> 
    >>> engine = AgenticEngine()
    >>> engine.start_session("research")
    >>> engine.index_codebase("./src")
    >>> results = engine.search("how does auth work")
    >>> response = engine.chat("Explain this code")
"""

import asyncio
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from threading import RLock
from typing import Any, Optional, Union

from agentic_assistants.config import AgenticConfig
from agentic_assistants.core.ollama import OllamaManager
from agentic_assistants.core.session import Session, SessionManager
from agentic_assistants.data.layer import DataLayer
from agentic_assistants.indexing.codebase import CodebaseIndexer, IndexingStats
from agentic_assistants.utils.logging import get_logger
from agentic_assistants.vectordb.base import Document, SearchResult, VectorStore

# Type hints for lazy-loaded components
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from agentic_assistants.data.catalog import DataCatalog
    from agentic_assistants.data.layers import DataLayerManager
    from agentic_assistants.pipelines.registry import PipelineRegistry
    from agentic_assistants.pipelines.runners.base import PipelineRunResult
    from agentic_assistants.hooks.manager import HookManager

logger = get_logger(__name__)


class AgenticEngine:
    """
    Unified interface for the Agentic Assistants framework.
    
    This class provides a single entry point for:
    - Session management
    - Vector database operations
    - Codebase indexing
    - Chat with LLM
    - Server management
    
    The engine is thread-safe and manages component lifecycles.
    
    Attributes:
        config: Framework configuration
        session: Current active session
    """

    def __init__(
        self,
        config: Optional[AgenticConfig] = None,
        session_name: Optional[str] = None,
        auto_start_ollama: bool = False,
    ):
        """
        Initialize the Agentic Engine.
        
        Args:
            config: Configuration instance
            session_name: Initial session name (uses default if None)
            auto_start_ollama: Automatically start Ollama if not running
        """
        self.config = config or AgenticConfig()
        self._lock = RLock()
        
        # Lazy-initialized components
        self._session_manager: Optional[SessionManager] = None
        self._session: Optional[Session] = None
        self._vector_store: Optional[VectorStore] = None
        self._data_layer: Optional[DataLayer] = None
        self._ollama: Optional[OllamaManager] = None
        self._indexer: Optional[CodebaseIndexer] = None
        self._server_manager = None
        
        # New Kedro-inspired components
        self._catalog: Optional["DataCatalog"] = None
        self._pipeline_registry: Optional["PipelineRegistry"] = None
        self._layer_manager: Optional["DataLayerManager"] = None
        self._hook_manager: Optional["HookManager"] = None
        
        # Initialize session if specified
        if session_name:
            self.start_session(session_name)
        
        # Start Ollama if requested
        if auto_start_ollama:
            self.ensure_ollama()

    # === Component Properties (Lazy Initialization) ===

    @property
    def session_manager(self) -> SessionManager:
        """Get the session manager."""
        if self._session_manager is None:
            self._session_manager = SessionManager(self.config)
        return self._session_manager

    @property
    def session(self) -> Session:
        """Get the current session."""
        if self._session is None:
            self._session = SessionManager.get_or_create(config=self.config)
        return self._session

    @property
    def vector_store(self) -> VectorStore:
        """Get the vector store."""
        if self._vector_store is None:
            self._vector_store = VectorStore.create(config=self.config)
        return self._vector_store

    @property
    def data_layer(self) -> DataLayer:
        """Get the data layer."""
        if self._data_layer is None:
            self._data_layer = DataLayer(self.config)
        return self._data_layer

    @property
    def ollama(self) -> OllamaManager:
        """Get the Ollama manager."""
        if self._ollama is None:
            self._ollama = OllamaManager(self.config)
        return self._ollama

    @property
    def indexer(self) -> CodebaseIndexer:
        """Get the codebase indexer."""
        if self._indexer is None:
            self._indexer = CodebaseIndexer(
                vector_store=self.vector_store,
                config=self.config,
            )
        return self._indexer

    @property
    def catalog(self) -> "DataCatalog":
        """
        Get the data catalog (Kedro-style).
        
        The catalog provides:
        - YAML-based dataset configuration
        - Dataset versioning
        - Pattern-based dataset factories
        - Multiple dataset types (CSV, Parquet, API, etc.)
        
        Example:
            >>> df = engine.catalog.load("users")
            >>> engine.catalog.save("processed_users", df)
        """
        if self._catalog is None:
            from agentic_assistants.data.catalog import DataCatalog
            
            # Try to load from config directory
            conf_path = self.config.data_dir.parent / "conf"
            if conf_path.exists():
                self._catalog = DataCatalog.from_config_dir(conf_path)
            else:
                self._catalog = DataCatalog(config=self.config)
        
        return self._catalog

    @property
    def pipeline_registry(self) -> "PipelineRegistry":
        """
        Get the pipeline registry.
        
        The registry manages all registered pipelines for the project.
        
        Example:
            >>> engine.pipeline_registry.register("my_pipeline", pipeline)
            >>> names = engine.pipeline_registry.list_pipelines()
        """
        if self._pipeline_registry is None:
            from agentic_assistants.pipelines.registry import PipelineRegistry
            self._pipeline_registry = PipelineRegistry()
        return self._pipeline_registry

    @property
    def layer_manager(self) -> "DataLayerManager":
        """
        Get the data layer manager.
        
        Manages data organization across the 8-layer convention:
        - 01_raw, 02_intermediate, 03_primary, 04_feature
        - 05_model_input, 06_model_output, 07_reporting, 08_external
        
        Example:
            >>> engine.layer_manager.create_layer_structure()
            >>> path = engine.layer_manager.get_layer_path(DataLayer.RAW)
        """
        if self._layer_manager is None:
            from agentic_assistants.data.layers import DataLayerManager
            self._layer_manager = DataLayerManager(
                data_root=self.config.data_dir / "layers",
            )
        return self._layer_manager

    @property
    def hook_manager(self) -> "HookManager":
        """
        Get the hook manager for pipeline lifecycle events.
        
        Example:
            >>> from agentic_assistants.hooks.implementations import MLFlowHook
            >>> engine.hook_manager.register(MLFlowHook())
        """
        if self._hook_manager is None:
            from agentic_assistants.hooks.manager import HookManager
            self._hook_manager = HookManager()
        return self._hook_manager

    # === Session Management ===

    def start_session(self, name: str) -> Session:
        """
        Start or switch to a session.
        
        Args:
            name: Session name
        
        Returns:
            Session instance
        """
        with self._lock:
            self._session = SessionManager.get_or_create(name, self.config)
            logger.info(f"Started session: {name}")
            return self._session

    def get_session(self, name: Optional[str] = None) -> Session:
        """
        Get a session by name.
        
        Args:
            name: Session name (current session if None)
        
        Returns:
            Session instance
        """
        if name is None:
            return self.session
        return self.session_manager.get_session(name) or self.start_session(name)

    def list_sessions(self) -> list[dict]:
        """List all sessions."""
        return self.session_manager.list_sessions()

    def delete_session(self, name: str) -> bool:
        """Delete a session."""
        return self.session_manager.delete_session(name)

    # === Vector Database Operations ===

    def search(
        self,
        query: str,
        collection: str = "default",
        top_k: int = 5,
        filter_metadata: Optional[dict] = None,
    ) -> list[SearchResult]:
        """
        Search the vector database.
        
        Args:
            query: Search query text
            collection: Collection to search
            top_k: Number of results
            filter_metadata: Optional metadata filters
        
        Returns:
            List of SearchResult objects
        """
        return self.vector_store.search(
            query=query,
            collection=collection,
            top_k=top_k,
            filter_metadata=filter_metadata,
        )

    def add_documents(
        self,
        documents: Union[Document, list[Document]],
        collection: str = "default",
    ) -> list[str]:
        """
        Add documents to the vector database.
        
        Args:
            documents: Document(s) to add
            collection: Collection name
        
        Returns:
            List of added document IDs
        """
        return self.vector_store.add(documents, collection=collection)

    def list_collections(self) -> list[str]:
        """List all vector database collections."""
        return self.vector_store.list_collections()

    def delete_collection(self, name: str) -> bool:
        """Delete a collection."""
        return self.vector_store.delete_collection(name)

    # === Codebase Indexing ===

    def index_codebase(
        self,
        path: Union[str, Path],
        collection: str = "default",
        patterns: Optional[list[str]] = None,
        force: bool = False,
        progress_callback: Optional[callable] = None,
    ) -> IndexingStats:
        """
        Index a codebase directory.
        
        Args:
            path: Directory path to index
            collection: Collection name
            patterns: File patterns to include
            force: Force re-indexing
            progress_callback: Progress callback function
        
        Returns:
            Indexing statistics
        """
        path = Path(path)
        
        if path.is_file():
            return self.indexer.index_file(
                path=path,
                collection=collection,
                force=force,
            )
        else:
            return self.indexer.index_directory(
                directory=path,
                collection=collection,
                patterns=patterns,
                force=force,
                progress_callback=progress_callback,
            )

    def get_indexing_stats(self, collection: str = "default") -> dict:
        """Get indexing statistics for a collection."""
        return self.indexer.get_stats(collection)

    # === Pipeline Execution ===

    def run_pipeline(
        self,
        name: str = "__default__",
        runner: str = "sequential",
        from_nodes: Optional[list[str]] = None,
        to_nodes: Optional[list[str]] = None,
        tags: Optional[list[str]] = None,
        run_id: Optional[str] = None,
    ) -> "PipelineRunResult":
        """
        Run a pipeline from the registry.
        
        Args:
            name: Pipeline name (default: "__default__" runs all pipelines)
            runner: Runner type ('sequential', 'parallel', 'thread')
            from_nodes: Start from these nodes (inclusive)
            to_nodes: Run up to these nodes (inclusive)
            tags: Filter nodes by tags
            run_id: Optional unique run identifier
        
        Returns:
            PipelineRunResult with execution details
        
        Example:
            >>> result = engine.run_pipeline("data_processing")
            >>> result = engine.run_pipeline("training", runner="parallel")
            >>> result = engine.run_pipeline(tags=["preprocessing"])
        """
        from agentic_assistants.pipelines.runners import (
            SequentialRunner,
            ParallelRunner,
            ThreadRunner,
        )
        
        # Get pipeline
        if name == "__default__":
            pipeline = self.pipeline_registry.get_default_pipeline()
        else:
            pipeline = self.pipeline_registry.get(name)
            if pipeline is None:
                raise ValueError(f"Pipeline '{name}' not found in registry")
        
        # Apply filters
        if from_nodes:
            pipeline = pipeline.from_nodes(*from_nodes)
        if to_nodes:
            pipeline = pipeline.to_nodes(*to_nodes)
        if tags:
            pipeline = pipeline.only_nodes_with_tags(*tags)
        
        # Get runner
        if runner == "parallel":
            runner_instance = ParallelRunner()
        elif runner == "thread":
            runner_instance = ThreadRunner()
        else:
            runner_instance = SequentialRunner()
        
        # Run with hooks
        logger.info(f"Running pipeline '{name}' with {len(pipeline)} nodes")
        result = runner_instance.run(
            pipeline=pipeline,
            catalog=self.catalog,
            run_id=run_id,
            hook_manager=self._hook_manager,
        )
        
        if result.success:
            logger.info(f"Pipeline completed in {result.duration_seconds:.2f}s")
        else:
            logger.error(f"Pipeline failed: {result.errors}")
        
        return result

    def load_dataset(self, name: str, version: Optional[str] = None) -> Any:
        """
        Load a dataset from the catalog.
        
        Args:
            name: Dataset name
            version: Optional specific version to load
        
        Returns:
            Loaded data
        
        Example:
            >>> df = engine.load_dataset("users")
            >>> df = engine.load_dataset("model", version="2024-01-15T10.30.00.000000Z")
        """
        return self.catalog.load(name, version=version)

    def save_dataset(self, name: str, data: Any) -> None:
        """
        Save data to a dataset in the catalog.
        
        Args:
            name: Dataset name
            data: Data to save
        
        Example:
            >>> engine.save_dataset("processed_users", df)
        """
        self.catalog.save(name, data)

    def list_datasets(self) -> list[str]:
        """List all datasets in the catalog."""
        return self.catalog.list_datasets()

    def list_pipelines(self) -> list[str]:
        """List all registered pipelines."""
        return self.pipeline_registry.list_pipelines()

    # === Chat with LLM ===

    def chat(
        self,
        message: Union[str, list[dict]],
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        context_collection: Optional[str] = None,
        context_top_k: int = 3,
        save_to_session: bool = True,
        **kwargs,
    ) -> str:
        """
        Chat with the LLM, optionally with RAG context.
        
        Args:
            message: User message or full messages list
            model: Model to use (default from config)
            system_prompt: Optional system prompt
            context_collection: Collection for RAG context
            context_top_k: Number of context documents
            save_to_session: Whether to save chat to session
            **kwargs: Additional parameters for Ollama
        
        Returns:
            Assistant response text
        """
        # Ensure Ollama is running
        self.ensure_ollama()
        
        # Build messages
        if isinstance(message, str):
            messages = []
            
            # Add system prompt
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            # Add RAG context if specified
            if context_collection:
                context = self._get_rag_context(message, context_collection, context_top_k)
                if context:
                    messages.append({
                        "role": "system",
                        "content": f"Relevant context:\n\n{context}",
                    })
            
            messages.append({"role": "user", "content": message})
        else:
            messages = message
        
        # Call Ollama
        with self._trace_chat(messages, model) as run:
            response = self.ollama.chat(messages, model=model, **kwargs)
            response_text = response["message"]["content"]
            
            if run:
                from agentic_assistants.core.mlflow_tracker import MLFlowTracker
                MLFlowTracker(self.config).log_chat_interaction(
                    messages=messages,
                    response=response_text,
                    model=model or self.config.ollama.default_model,
                )
        
        # Save to session
        if save_to_session:
            self.session.log_chat(
                messages=messages + [{"role": "assistant", "content": response_text}],
                summary=message[:100] if isinstance(message, str) else None,
                model=model or self.config.ollama.default_model,
            )
        
        return response_text

    def _get_rag_context(
        self,
        query: str,
        collection: str,
        top_k: int,
    ) -> str:
        """Get RAG context from vector database."""
        results = self.search(query, collection=collection, top_k=top_k)
        
        if not results:
            return ""
        
        context_parts = []
        for i, result in enumerate(results, 1):
            file_path = result.document.metadata.get("file_path", "unknown")
            content = result.document.content
            context_parts.append(f"[{i}] {file_path}:\n```\n{content}\n```")
        
        return "\n\n".join(context_parts)

    @contextmanager
    def _trace_chat(self, messages: list[dict], model: Optional[str]):
        """Trace chat interaction with MLFlow if enabled."""
        if not self.config.mlflow_enabled:
            yield None
            return

        try:
            from agentic_assistants.core.mlflow_tracker import MLFlowTracker
            tracker = MLFlowTracker(self.config)
            with tracker.start_run(run_name=f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}") as run:
                yield run
        except Exception as e:
            logger.warning(f"MLFlow tracing failed: {e}")
            yield None

    # === Ollama Management ===

    def ensure_ollama(self) -> bool:
        """
        Ensure Ollama is running.
        
        Returns:
            True if Ollama is running
        """
        if not self.ollama.is_running():
            logger.info("Starting Ollama...")
            self.ollama.start()
        return self.ollama.is_running()

    def list_models(self) -> list:
        """List available Ollama models."""
        self.ensure_ollama()
        return self.ollama.list_models()

    def pull_model(self, model: str) -> bool:
        """Pull an Ollama model."""
        self.ensure_ollama()
        return self.ollama.pull_model(model)

    # === Data Layer ===

    def read_data(self, path: Union[str, Path], **kwargs) -> Any:
        """
        Read data from a file.
        
        Args:
            path: File path
            **kwargs: Additional arguments
        
        Returns:
            Data from the file
        """
        return self.data_layer.read(path, **kwargs)

    def write_data(self, data: Any, path: Union[str, Path], **kwargs) -> Path:
        """
        Write data to a file.
        
        Args:
            data: Data to write
            path: File path
            **kwargs: Additional arguments
        
        Returns:
            Path to written file
        """
        return self.data_layer.write(data, path, **kwargs)

    # === Context Management ===

    def save_context(
        self,
        name: str,
        data: Any,
        metadata: Optional[dict] = None,
    ) -> str:
        """
        Save context to the current session.
        
        Args:
            name: Context name
            data: Data to save
            metadata: Optional metadata
        
        Returns:
            Context entry ID
        """
        return self.session.save_context(name, data, metadata)

    def get_context(self, name: str) -> Optional[Any]:
        """
        Get context from the current session.
        
        Args:
            name: Context name
        
        Returns:
            Context data or None
        """
        return self.session.get_context(name)

    def list_contexts(self) -> list[dict]:
        """List all contexts in the current session."""
        return self.session.list_contexts()

    # === Server Management ===

    def start_server(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        background: bool = True,
    ) -> Optional[str]:
        """
        Start the MCP/REST server.
        
        Args:
            host: Server host
            port: Server port
            background: Run in background
        
        Returns:
            Server URL if started in background
        """
        from agentic_assistants.server.app import ServerManager, start_server
        
        host = host or self.config.server.host
        port = port or self.config.server.port
        
        if background:
            if self._server_manager is None:
                self._server_manager = ServerManager(
                    host=host,
                    port=port,
                    config=self.config,
                )
            
            if not self._server_manager.is_running:
                # Run in a thread with its own event loop
                import threading
                
                def run_server():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(self._server_manager.start())
                
                thread = threading.Thread(target=run_server, daemon=True)
                thread.start()
                
                # Wait a bit for server to start
                import time
                time.sleep(1)
            
            return self._server_manager.url
        else:
            start_server(host=host, port=port, config=self.config)
            return None

    def stop_server(self) -> None:
        """Stop the server."""
        if self._server_manager is not None:
            loop = asyncio.new_event_loop()
            loop.run_until_complete(self._server_manager.stop())

    # === Context Manager Support ===

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup resources."""
        self.close()
        return False

    def close(self) -> None:
        """Close the engine and cleanup resources."""
        with self._lock:
            # Stop server if running
            if self._server_manager is not None:
                self.stop_server()
            
            # Clear references
            self._session = None
            self._vector_store = None
            self._data_layer = None
            self._indexer = None
            
            logger.info("Engine closed")

    # === Utility Methods ===

    def get_status(self) -> dict:
        """Get overall engine status."""
        return {
            "session": {
                "name": self.session.name if self._session else None,
                "id": self.session.id if self._session else None,
            },
            "ollama": {
                "running": self.ollama.is_running(),
                "host": self.config.ollama.host,
            },
            "vector_store": {
                "backend": self.config.vectordb.backend,
                "collections": self.list_collections() if self._vector_store else [],
            },
            "server": {
                "running": self._server_manager.is_running if self._server_manager else False,
                "url": self._server_manager.url if self._server_manager else None,
            },
            "config": {
                "data_dir": str(self.config.data_dir),
                "mlflow_enabled": self.config.mlflow_enabled,
                "telemetry_enabled": self.config.telemetry_enabled,
            },
        }

    def __repr__(self) -> str:
        session_name = self._session.name if self._session else "none"
        return f"AgenticEngine(session={session_name!r})"

