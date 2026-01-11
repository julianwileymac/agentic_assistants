"""
FastAPI REST server for vector search and indexing.

This module provides REST API endpoints for:
- Searching the vector database
- Indexing codebases
- Managing collections

Example:
    >>> from agentic_assistants.server.rest import create_rest_app
    >>> import uvicorn
    >>> 
    >>> app = create_rest_app()
    >>> uvicorn.run(app, host="127.0.0.1", port=8080)
"""

from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from agentic_assistants.config import AgenticConfig
from agentic_assistants.engine import AgenticEngine
from agentic_assistants.indexing.codebase import CodebaseIndexer
from agentic_assistants.utils.logging import get_logger
from agentic_assistants.vectordb.base import VectorStore

# Import API routers
from agentic_assistants.server.api import (
    experiments_router,
    artifacts_router,
    sessions_router,
    data_router,
    config_router,
    projects_router,
    agents_router,
    flows_router,
    components_router,
    notes_router,
    tags_router,
    datasources_router,
    generation_router,
    kubernetes_router,
)

# Import new pipeline and catalog routers
from agentic_assistants.server.api.pipelines import router as pipelines_router

# Import training and models routers
from agentic_assistants.server.api.training import router as training_router
from agentic_assistants.server.api.models import router as models_router

# Import WebSocket support
from agentic_assistants.server.websocket import add_websocket_routes

logger = get_logger(__name__)


# === Request/Response Models ===

class ChatRequest(BaseModel):
    """Request body for chat endpoint."""
    message: str
    model: Optional[str] = None
    system_prompt: Optional[str] = None
    context_collection: Optional[str] = None
    save_to_session: bool = True


class SessionCreateRequest(BaseModel):
    """Request body for creating a session."""
    name: str
    metadata: Optional[dict] = None


class ArtifactTagRequest(BaseModel):
    """Request body for tagging an artifact."""
    artifact_id: str
    tag: str
    group: Optional[str] = None


# === Server State ===

class ServerState:
    """Shared state for the REST server."""
    
    def __init__(self, config: Optional[AgenticConfig] = None):
        self.config = config or AgenticConfig()
        self._engine: Optional[AgenticEngine] = None

    @property
    def engine(self) -> AgenticEngine:
        """Get or create the agentic engine."""
        if self._engine is None:
            self._engine = AgenticEngine(config=self.config)
        return self._engine

    @property
    def vector_store(self) -> VectorStore:
        """Get vector store from engine."""
        return self.engine.vector_store

    @property
    def indexer(self) -> CodebaseIndexer:
        """Get indexer from engine."""
        return self.engine.indexer

class SearchRequest(BaseModel):
    """Request body for search endpoint."""
    
    query: str = Field(..., description="Search query text")
    collection: str = Field(default="default", description="Collection to search")
    top_k: int = Field(default=5, ge=1, le=100, description="Number of results")
    filter_metadata: Optional[dict] = Field(default=None, description="Metadata filters")


class SearchResult(BaseModel):
    """A single search result."""
    
    id: str
    content: str
    score: float
    metadata: dict


class SearchResponse(BaseModel):
    """Response from search endpoint."""
    
    query: str
    collection: str
    results: list[SearchResult]
    total: int


class IndexRequest(BaseModel):
    """Request body for index endpoint."""
    
    path: str = Field(..., description="Path to index")
    collection: str = Field(default="default", description="Collection name")
    patterns: Optional[list[str]] = Field(default=None, description="File patterns")
    recursive: bool = Field(default=True, description="Recurse into subdirectories")
    force: bool = Field(default=False, description="Force re-indexing")


class IndexResponse(BaseModel):
    """Response from index endpoint."""
    
    status: str
    collection: str
    files_processed: int
    files_skipped: int
    chunks_indexed: int
    duration_seconds: float
    errors: list[str]


class CollectionInfo(BaseModel):
    """Information about a collection."""
    
    name: str
    document_count: int


class CollectionsResponse(BaseModel):
    """Response from collections endpoint."""
    
    collections: list[CollectionInfo]


class HealthResponse(BaseModel):
    """Response from health endpoint."""
    
    status: str
    version: str
    vector_store: str


# Global state (initialized on app startup)
_state: Optional[ServerState] = None


def get_state() -> ServerState:
    """Get the server state."""
    global _state
    if _state is None:
        _state = ServerState()
    return _state


# === REST API ===

def create_rest_app(
    config: Optional[AgenticConfig] = None,
    title: str = "Agentic Assistants API",
    version: str = "0.1.0",
) -> FastAPI:
    """
    Create the FastAPI REST application.
    
    Args:
        config: Configuration instance
        title: API title
        version: API version
    
    Returns:
        FastAPI application
    """
    global _state
    _state = ServerState(config)
    
    app = FastAPI(
        title=title,
        version=version,
        description="REST API for Agentic Assistants vector search and indexing",
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include modular API routers
    app.include_router(experiments_router, prefix="/api/v1")
    app.include_router(artifacts_router, prefix="/api/v1")
    app.include_router(sessions_router, prefix="/api/v1")
    app.include_router(data_router, prefix="/api/v1")
    app.include_router(config_router, prefix="/api/v1")
    
    # Control Panel API routers
    app.include_router(projects_router, prefix="/api/v1")
    app.include_router(agents_router, prefix="/api/v1")
    app.include_router(flows_router, prefix="/api/v1")
    app.include_router(components_router, prefix="/api/v1")
    app.include_router(notes_router, prefix="/api/v1")
    app.include_router(tags_router, prefix="/api/v1")
    app.include_router(datasources_router, prefix="/api/v1")
    app.include_router(generation_router, prefix="/api/v1")
    
    # Pipeline and Data Catalog routers (Kedro-inspired)
    app.include_router(pipelines_router, prefix="/api/v1/pipelines", tags=["pipelines"])
    
    # Infrastructure routers
    app.include_router(kubernetes_router)
    
    # Training and Models routers (LLM/SLM development)
    app.include_router(training_router, prefix="/api/v1")
    app.include_router(models_router, prefix="/api/v1")
    
    # === Legacy Endpoints (kept for backwards compatibility) ===
    
    @app.get("/health", response_model=HealthResponse)
    async def health_check():
        """Health check endpoint."""
        state = get_state()
        return HealthResponse(
            status="healthy",
            version=version,
            vector_store=state.config.vectordb.backend,
        )
    
    @app.post("/chat")
    async def chat(request: ChatRequest):
        """Chat with the agentic engine."""
        state = get_state()
        try:
            response = state.engine.chat(
                message=request.message,
                model=request.model,
                system_prompt=request.system_prompt,
                context_collection=request.context_collection,
                save_to_session=request.save_to_session,
            )
            return {"response": response}
        except Exception as e:
            logger.error(f"Chat failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/sessions")
    async def list_sessions():
        """List all sessions."""
        state = get_state()
        return state.engine.list_sessions()

    @app.post("/sessions")
    async def create_session(request: SessionCreateRequest):
        """Create a new session."""
        state = get_state()
        try:
            session = state.engine.start_session(request.name)
            return session.to_dict()
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    @app.get("/sessions/{name}")
    async def get_session(name: str):
        """Get session details."""
        state = get_state()
        session = state.engine.get_session(name)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return session.to_dict()

    @app.post("/artifacts/tag")
    async def tag_artifact(request: ArtifactTagRequest):
        """Tag an artifact."""
        state = get_state()
        try:
            # Get current session
            session = state.engine.session
            artifact_id = session.add_artifact(
                name=f"tagged_{request.artifact_id}",
                path=request.artifact_id, # Assuming path is artifact_id for now
                tag=request.tag,
                group=request.group
            )
            return {"status": "tagged", "artifact_id": artifact_id}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/data/read")
    async def read_data(path: str):
        """Read data from the data layer."""
        state = get_state()
        try:
            data = state.engine.read_data(path)
            # Convert to serializable format if needed
            return {"data": str(data)}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/mlflow/experiment/start")
    async def start_experiment(name: str):
        """Start an MLFlow experiment."""
        state = get_state()
        try:
            from agentic_assistants.core.mlflow_tracker import MLFlowTracker
            tracker = MLFlowTracker(config=state.config)
            tracker.start_run(run_name=name)
            return {"status": "experiment started", "name": name}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/search", response_model=SearchResponse)
    async def search(request: SearchRequest):
        """
        Search the vector database.
        
        Returns documents similar to the query.
        """
        state = get_state()
        
        try:
            results = state.vector_store.search(
                query=request.query,
                collection=request.collection,
                top_k=request.top_k,
                filter_metadata=request.filter_metadata,
            )
            
            return SearchResponse(
                query=request.query,
                collection=request.collection,
                results=[
                    SearchResult(
                        id=r.document.id,
                        content=r.document.content,
                        score=r.score,
                        metadata=r.document.metadata,
                    )
                    for r in results
                ],
                total=len(results),
            )
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/index", response_model=IndexResponse)
    async def index_path(request: IndexRequest, background_tasks: BackgroundTasks):
        """
        Index a file or directory.
        
        For large directories, indexing runs in the background.
        """
        state = get_state()
        path = Path(request.path)
        
        if not path.exists():
            raise HTTPException(status_code=404, detail=f"Path not found: {request.path}")
        
        try:
            if path.is_file():
                stats = state.indexer.index_file(
                    path=path,
                    collection=request.collection,
                    force=request.force,
                )
            else:
                stats = state.indexer.index_directory(
                    directory=path,
                    collection=request.collection,
                    patterns=request.patterns,
                    recursive=request.recursive,
                    force=request.force,
                )
            
            return IndexResponse(
                status="completed",
                collection=request.collection,
                files_processed=stats.files_processed,
                files_skipped=stats.files_skipped,
                chunks_indexed=stats.chunks_indexed,
                duration_seconds=stats.duration_seconds,
                errors=stats.errors,
            )
            
        except Exception as e:
            logger.error(f"Indexing failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/collections", response_model=CollectionsResponse)
    async def list_collections():
        """List all collections."""
        state = get_state()
        
        try:
            collections = state.vector_store.list_collections()
            return CollectionsResponse(
                collections=[
                    CollectionInfo(
                        name=name,
                        document_count=state.vector_store.count(name),
                    )
                    for name in collections
                ]
            )
            
        except Exception as e:
            logger.error(f"Failed to list collections: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/collections/{name}")
    async def get_collection(name: str):
        """Get information about a collection."""
        state = get_state()
        
        if name not in state.vector_store.list_collections():
            raise HTTPException(status_code=404, detail=f"Collection not found: {name}")
        
        try:
            stats = state.indexer.get_stats(name)
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get collection info: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.delete("/collections/{name}")
    async def delete_collection(name: str):
        """Delete a collection."""
        state = get_state()
        
        try:
            success = state.vector_store.delete_collection(name)
            if success:
                return {"status": "deleted", "collection": name}
            else:
                raise HTTPException(status_code=404, detail=f"Collection not found: {name}")
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to delete collection: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/stats")
    async def get_stats():
        """Get overall statistics."""
        state = get_state()
        
        try:
            return state.vector_store.get_info()
            
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/v1/stats")
    async def get_control_panel_stats():
        """Get control panel statistics."""
        from agentic_assistants.core.models import ControlPanelStore
        
        try:
            store = ControlPanelStore.get_instance()
            return store.get_stats()
        except Exception as e:
            logger.error(f"Failed to get control panel stats: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # Add WebSocket routes
    add_websocket_routes(app)
    
    return app

