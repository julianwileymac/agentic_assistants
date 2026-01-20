"""
Components API Router.

This module provides REST endpoints for code component management.
"""

from typing import Optional, List

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from agentic_assistants.core.models import ControlPanelStore
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/components", tags=["components"])


# === Request/Response Models ===

class ComponentCreate(BaseModel):
    """Request to create a new component."""
    name: str = Field(..., description="Component name")
    category: str = Field(..., description="Component category (tool, agent, task, pattern, utility, template)")
    code: str = Field(default="", description="Component source code")
    language: str = Field(default="python", description="Programming language")
    description: str = Field(default="", description="Component description")
    usage_example: str = Field(default="", description="Usage example")
    version: str = Field(default="1.0.0", description="Component version")
    tags: List[str] = Field(default_factory=list, description="Component tags")
    metadata: dict = Field(default_factory=dict, description="Additional metadata")


class ComponentUpdate(BaseModel):
    """Request to update a component."""
    name: Optional[str] = None
    category: Optional[str] = None
    code: Optional[str] = None
    language: Optional[str] = None
    description: Optional[str] = None
    usage_example: Optional[str] = None
    version: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[dict] = None


class ComponentResponse(BaseModel):
    """Component response model."""
    id: str
    name: str
    category: str
    code: str
    language: str
    description: str
    usage_example: str
    version: str
    created_at: str
    updated_at: str
    tags: List[str]
    metadata: dict


class ComponentsListResponse(BaseModel):
    """Response containing list of components."""
    items: List[ComponentResponse]
    total: int
    page: int
    page_size: int
    has_more: bool


# === Helper Functions ===

def _get_store() -> ControlPanelStore:
    """Get the control panel store instance."""
    return ControlPanelStore.get_instance()


# Extended categories for Dify/RAGFlow-inspired workflow
VALID_CATEGORIES = {
    # Original categories
    "tool",          # Reusable agent tools
    "agent",         # Agent templates
    "task",          # Task definitions
    "pattern",       # Agentic patterns (RAG, ReAct, etc.)
    "utility",       # Utility functions
    "template",      # Project templates
    # New categories for extended functionality
    "datasource_handler",  # Data source connection handlers
    "embedding_model",     # Custom embedding configurations
    "prompt_template",     # Reusable prompt templates
    "workflow_node",       # Dify-style workflow nodes
    "retrieval_strategy",  # RAG retrieval strategies
    "llm_wrapper",         # LLM integration wrappers
    "crew_config",         # CrewAI crew configurations
    # Additional Dify/RAGFlow categories
    "knowledge_retrieval", # RAGFlow-style knowledge base retrieval
    "conditional_branch",  # Decision/routing nodes
    "iteration_node",      # Loop/batch processing nodes
    "http_request",        # External API integration nodes
    "code_executor",       # Sandboxed code execution nodes
    "variable_aggregator", # Data transformation nodes
}


# === Endpoints ===

@router.get("", response_model=ComponentsListResponse)
async def list_components(
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search in name and description"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
) -> ComponentsListResponse:
    """List all components with optional filtering."""
    store = _get_store()
    
    if category and category not in VALID_CATEGORIES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid category. Must be one of: {', '.join(VALID_CATEGORIES)}"
        )
    
    components, total = store.list_components(
        category=category, search=search, page=page, limit=limit
    )
    
    return ComponentsListResponse(
        items=[ComponentResponse(**c.to_dict()) for c in components],
        total=total,
        page=page,
        page_size=limit,
        has_more=(page * limit) < total,
    )


@router.post("", response_model=ComponentResponse)
async def create_component(request: ComponentCreate) -> ComponentResponse:
    """Create a new component."""
    store = _get_store()
    
    if request.category not in VALID_CATEGORIES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid category. Must be one of: {', '.join(VALID_CATEGORIES)}"
        )
    
    try:
        component = store.create_component(
            name=request.name,
            category=request.category,
            code=request.code,
            language=request.language,
            description=request.description,
            usage_example=request.usage_example,
            version=request.version,
            tags=request.tags,
            metadata=request.metadata,
        )
        return ComponentResponse(**component.to_dict())
    except Exception as e:
        logger.error(f"Failed to create component: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{component_id}", response_model=ComponentResponse)
async def get_component(component_id: str) -> ComponentResponse:
    """Get a component by ID."""
    store = _get_store()
    component = store.get_component(component_id)
    
    if component is None:
        raise HTTPException(status_code=404, detail="Component not found")
    
    return ComponentResponse(**component.to_dict())


@router.put("/{component_id}", response_model=ComponentResponse)
async def update_component(component_id: str, request: ComponentUpdate) -> ComponentResponse:
    """Update a component."""
    store = _get_store()
    
    if request.category and request.category not in VALID_CATEGORIES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid category. Must be one of: {', '.join(VALID_CATEGORIES)}"
        )
    
    update_data = {k: v for k, v in request.model_dump().items() if v is not None}
    component = store.update_component(component_id, **update_data)
    
    if component is None:
        raise HTTPException(status_code=404, detail="Component not found")
    
    return ComponentResponse(**component.to_dict())


@router.delete("/{component_id}")
async def delete_component(component_id: str) -> dict:
    """Delete a component."""
    store = _get_store()
    
    if not store.delete_component(component_id):
        raise HTTPException(status_code=404, detail="Component not found")
    
    return {"status": "deleted", "id": component_id}


@router.get("/categories/list")
async def list_categories() -> dict:
    """List all valid component categories."""
    return {
        "categories": [
            # Core categories
            {"id": "tool", "name": "Tool", "description": "Reusable agent tools", "group": "core"},
            {"id": "agent", "name": "Agent", "description": "Agent templates", "group": "core"},
            {"id": "task", "name": "Task", "description": "Task definitions", "group": "core"},
            {"id": "pattern", "name": "Pattern", "description": "Agentic patterns (RAG, ReAct, etc.)", "group": "core"},
            {"id": "utility", "name": "Utility", "description": "Utility functions", "group": "core"},
            {"id": "template", "name": "Template", "description": "Project templates", "group": "core"},
            # Extended categories
            {"id": "datasource_handler", "name": "Data Source Handler", "description": "Custom data source connection handlers", "group": "data"},
            {"id": "embedding_model", "name": "Embedding Model", "description": "Custom embedding configurations", "group": "ai"},
            {"id": "prompt_template", "name": "Prompt Template", "description": "Reusable prompt templates", "group": "ai"},
            {"id": "workflow_node", "name": "Workflow Node", "description": "Dify-style workflow nodes", "group": "workflow"},
            {"id": "retrieval_strategy", "name": "Retrieval Strategy", "description": "RAG retrieval strategies", "group": "data"},
            {"id": "llm_wrapper", "name": "LLM Wrapper", "description": "LLM integration wrappers", "group": "ai"},
            {"id": "crew_config", "name": "Crew Configuration", "description": "CrewAI crew configurations", "group": "workflow"},
        ],
        "groups": [
            {"id": "core", "name": "Core Components"},
            {"id": "ai", "name": "AI & Language Models"},
            {"id": "data", "name": "Data & Retrieval"},
            {"id": "workflow", "name": "Workflow & Orchestration"},
        ]
    }


# === Base Components from Installed Packages ===

BASE_COMPONENTS = [
    # CrewAI components
    {
        "name": "CrewAIAgent",
        "category": "agent",
        "description": "Base CrewAI agent template with role, goal, and backstory configuration",
        "language": "python",
        "code": '''"""CrewAI Agent Template.

A base template for creating CrewAI agents with standard configuration.
"""

from crewai import Agent

def create_agent(
    role: str,
    goal: str,
    backstory: str,
    tools: list = None,
    verbose: bool = True,
    allow_delegation: bool = False,
) -> Agent:
    """Create a CrewAI agent with the specified configuration.
    
    Args:
        role: The agent's role in the crew
        goal: The agent's goal
        backstory: The agent's backstory for context
        tools: List of tools the agent can use
        verbose: Enable verbose logging
        allow_delegation: Allow delegating tasks to other agents
    
    Returns:
        Configured CrewAI Agent instance
    """
    return Agent(
        role=role,
        goal=goal,
        backstory=backstory,
        tools=tools or [],
        verbose=verbose,
        allow_delegation=allow_delegation,
    )
''',
        "usage_example": '''from crewai import Crew, Task

# Create an agent
researcher = create_agent(
    role="Senior Researcher",
    goal="Find and analyze relevant information",
    backstory="You are an expert researcher with years of experience",
    tools=[search_tool, scrape_tool],
)

# Create a task
task = Task(
    description="Research the latest AI developments",
    expected_output="A summary of recent AI advancements",
    agent=researcher,
)

# Create and run crew
crew = Crew(agents=[researcher], tasks=[task])
result = crew.kickoff()
''',
        "tags": ["crewai", "agent", "template"],
        "metadata": {"package": "crewai", "version": ">=0.28.0"},
    },
    # LangGraph workflow
    {
        "name": "LangGraphWorkflow",
        "category": "pattern",
        "description": "LangGraph state machine workflow template for multi-step agent orchestration",
        "language": "python",
        "code": '''"""LangGraph Workflow Template.

A base template for creating state machine workflows with LangGraph.
"""

from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END

class WorkflowState(TypedDict):
    """State for the workflow."""
    messages: list
    current_step: str
    data: dict


def create_workflow():
    """Create a LangGraph workflow with standard structure.
    
    Returns:
        Compiled StateGraph ready for execution
    """
    workflow = StateGraph(WorkflowState)
    
    # Define nodes
    def process_input(state: WorkflowState) -> WorkflowState:
        """Process initial input."""
        return {"current_step": "processed", **state}
    
    def analyze(state: WorkflowState) -> WorkflowState:
        """Analyze the data."""
        return {"current_step": "analyzed", **state}
    
    def decide_next(state: WorkflowState) -> str:
        """Decide the next step."""
        if state.get("data", {}).get("complete"):
            return "end"
        return "analyze"
    
    # Add nodes to graph
    workflow.add_node("process", process_input)
    workflow.add_node("analyze", analyze)
    
    # Add edges
    workflow.set_entry_point("process")
    workflow.add_edge("process", "analyze")
    workflow.add_conditional_edges("analyze", decide_next, {"analyze": "analyze", "end": END})
    
    return workflow.compile()
''',
        "usage_example": '''# Create and run the workflow
workflow = create_workflow()

# Initial state
initial_state = {
    "messages": [],
    "current_step": "start",
    "data": {"input": "Some data to process"},
}

# Run the workflow
result = workflow.invoke(initial_state)
print(result)
''',
        "tags": ["langgraph", "workflow", "state-machine"],
        "metadata": {"package": "langgraph", "version": ">=0.0.1"},
    },
    # RAG Retriever
    {
        "name": "RAGRetriever",
        "category": "tool",
        "description": "RAG retrieval tool using LlamaIndex for semantic document search",
        "language": "python",
        "code": '''"""RAG Retriever Tool.

A retrieval tool using LlamaIndex for semantic document search.
"""

from typing import Optional, List
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.retrievers import VectorIndexRetriever


class RAGRetriever:
    """RAG-based document retriever using LlamaIndex."""
    
    def __init__(
        self,
        index: Optional[VectorStoreIndex] = None,
        top_k: int = 5,
    ):
        """Initialize the retriever.
        
        Args:
            index: Pre-built VectorStoreIndex
            top_k: Number of results to retrieve
        """
        self.index = index
        self.top_k = top_k
        self._retriever = None
    
    def from_directory(self, path: str) -> "RAGRetriever":
        """Build index from a directory of documents.
        
        Args:
            path: Path to documents directory
        
        Returns:
            Self for chaining
        """
        documents = SimpleDirectoryReader(path).load_data()
        self.index = VectorStoreIndex.from_documents(documents)
        return self
    
    def retrieve(self, query: str) -> List[dict]:
        """Retrieve relevant documents.
        
        Args:
            query: Search query
        
        Returns:
            List of retrieved documents with scores
        """
        if self.index is None:
            raise ValueError("Index not initialized. Call from_directory first.")
        
        if self._retriever is None:
            self._retriever = VectorIndexRetriever(
                index=self.index,
                similarity_top_k=self.top_k,
            )
        
        nodes = self._retriever.retrieve(query)
        return [
            {
                "content": node.node.text,
                "score": node.score,
                "metadata": node.node.metadata,
            }
            for node in nodes
        ]
''',
        "usage_example": '''# Create retriever from documents
retriever = RAGRetriever(top_k=3).from_directory("./docs")

# Retrieve relevant documents
results = retriever.retrieve("How do I configure the system?")
for doc in results:
    print(f"Score: {doc['score']:.2f}")
    print(f"Content: {doc['content'][:200]}...")
''',
        "tags": ["rag", "retrieval", "llama-index"],
        "metadata": {"package": "llama-index", "version": ">=0.10.0"},
    },
    # Ollama Embedder
    {
        "name": "OllamaEmbedder",
        "category": "embedding_model",
        "description": "Embedding model configuration using Ollama for local embeddings",
        "language": "python",
        "code": '''"""Ollama Embedding Model.

Configuration for using Ollama as an embedding provider.
"""

from typing import List, Optional
from langchain_ollama import OllamaEmbeddings


class OllamaEmbedder:
    """Embedding model using Ollama."""
    
    def __init__(
        self,
        model: str = "nomic-embed-text",
        base_url: str = "http://localhost:11434",
    ):
        """Initialize the Ollama embedder.
        
        Args:
            model: Ollama model name for embeddings
            base_url: Ollama server URL
        """
        self.model = model
        self.base_url = base_url
        self._embeddings = None
    
    @property
    def embeddings(self) -> OllamaEmbeddings:
        """Get the LangChain embeddings instance."""
        if self._embeddings is None:
            self._embeddings = OllamaEmbeddings(
                model=self.model,
                base_url=self.base_url,
            )
        return self._embeddings
    
    def embed_query(self, text: str) -> List[float]:
        """Embed a single query text.
        
        Args:
            text: Text to embed
        
        Returns:
            Embedding vector
        """
        return self.embeddings.embed_query(text)
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple documents.
        
        Args:
            texts: List of texts to embed
        
        Returns:
            List of embedding vectors
        """
        return self.embeddings.embed_documents(texts)
''',
        "usage_example": '''# Create embedder
embedder = OllamaEmbedder(model="nomic-embed-text")

# Embed a query
query_embedding = embedder.embed_query("What is machine learning?")
print(f"Embedding dimension: {len(query_embedding)}")

# Embed documents
docs = ["Document 1 content", "Document 2 content"]
doc_embeddings = embedder.embed_documents(docs)
''',
        "tags": ["ollama", "embeddings", "langchain"],
        "metadata": {"package": "langchain-ollama", "version": ">=0.1.0"},
    },
    # MLFlow Logger
    {
        "name": "MLFlowLogger",
        "category": "utility",
        "description": "MLFlow experiment tracking utility for logging metrics, parameters, and artifacts",
        "language": "python",
        "code": '''"""MLFlow Experiment Logger.

Utility for tracking ML experiments with MLFlow.
"""

import mlflow
from typing import Any, Dict, Optional
from pathlib import Path


class MLFlowLogger:
    """MLFlow experiment logger."""
    
    def __init__(
        self,
        experiment_name: str,
        tracking_uri: str = "http://localhost:5000",
    ):
        """Initialize the MLFlow logger.
        
        Args:
            experiment_name: Name of the experiment
            tracking_uri: MLFlow tracking server URI
        """
        self.experiment_name = experiment_name
        mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
        self._run = None
    
    def start_run(self, run_name: Optional[str] = None) -> "MLFlowLogger":
        """Start a new run.
        
        Args:
            run_name: Optional name for the run
        
        Returns:
            Self for chaining
        """
        self._run = mlflow.start_run(run_name=run_name)
        return self
    
    def log_params(self, params: Dict[str, Any]) -> "MLFlowLogger":
        """Log parameters.
        
        Args:
            params: Dictionary of parameters
        
        Returns:
            Self for chaining
        """
        mlflow.log_params(params)
        return self
    
    def log_metrics(self, metrics: Dict[str, float], step: Optional[int] = None) -> "MLFlowLogger":
        """Log metrics.
        
        Args:
            metrics: Dictionary of metrics
            step: Optional step number
        
        Returns:
            Self for chaining
        """
        mlflow.log_metrics(metrics, step=step)
        return self
    
    def log_artifact(self, path: str) -> "MLFlowLogger":
        """Log an artifact.
        
        Args:
            path: Path to artifact file
        
        Returns:
            Self for chaining
        """
        mlflow.log_artifact(path)
        return self
    
    def end_run(self) -> None:
        """End the current run."""
        if self._run:
            mlflow.end_run()
            self._run = None
    
    def __enter__(self):
        self.start_run()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_run()
        return False
''',
        "usage_example": '''# Use as context manager
with MLFlowLogger("my-experiment") as logger:
    logger.log_params({"learning_rate": 0.01, "epochs": 100})
    
    for epoch in range(100):
        loss = train_epoch()
        logger.log_metrics({"loss": loss}, step=epoch)
    
    logger.log_artifact("model.pkl")
''',
        "tags": ["mlflow", "experiment-tracking", "logging"],
        "metadata": {"package": "mlflow", "version": ">=2.0.0"},
    },
    # Vector Search Tool
    {
        "name": "VectorSearchTool",
        "category": "tool",
        "description": "Vector similarity search tool supporting LanceDB and ChromaDB backends",
        "language": "python",
        "code": '''"""Vector Search Tool.

A unified vector search tool supporting multiple backends.
"""

from typing import List, Dict, Any, Optional, Literal
from abc import ABC, abstractmethod


class VectorSearchTool:
    """Unified vector search tool."""
    
    def __init__(
        self,
        backend: Literal["lancedb", "chromadb"] = "lancedb",
        collection: str = "default",
        db_path: str = "./data/vectors",
    ):
        """Initialize the vector search tool.
        
        Args:
            backend: Vector database backend
            collection: Collection name
            db_path: Path to database storage
        """
        self.backend = backend
        self.collection = collection
        self.db_path = db_path
        self._db = None
        self._table = None
    
    def _init_lancedb(self):
        """Initialize LanceDB backend."""
        import lancedb
        self._db = lancedb.connect(self.db_path)
    
    def _init_chromadb(self):
        """Initialize ChromaDB backend."""
        import chromadb
        self._db = chromadb.PersistentClient(path=self.db_path)
    
    def add(
        self,
        texts: List[str],
        embeddings: List[List[float]],
        metadata: Optional[List[Dict]] = None,
        ids: Optional[List[str]] = None,
    ) -> None:
        """Add documents to the collection.
        
        Args:
            texts: Document texts
            embeddings: Document embeddings
            metadata: Optional metadata for each document
            ids: Optional IDs for each document
        """
        if self._db is None:
            if self.backend == "lancedb":
                self._init_lancedb()
            else:
                self._init_chromadb()
        
        # Implementation depends on backend
        raise NotImplementedError("Implement for specific backend")
    
    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter_metadata: Optional[Dict] = None,
    ) -> List[Dict[str, Any]]:
        """Search for similar documents.
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results
            filter_metadata: Optional metadata filter
        
        Returns:
            List of results with text, score, and metadata
        """
        raise NotImplementedError("Implement for specific backend")
''',
        "usage_example": '''# Create search tool
search = VectorSearchTool(backend="lancedb", collection="docs")

# Add documents
embeddings = embed_documents(["Doc 1", "Doc 2", "Doc 3"])
search.add(
    texts=["Doc 1", "Doc 2", "Doc 3"],
    embeddings=embeddings,
)

# Search
query_emb = embed_query("find relevant documents")
results = search.search(query_emb, top_k=5)
''',
        "tags": ["vector-search", "lancedb", "chromadb"],
        "metadata": {"packages": ["lancedb", "chromadb"]},
    },
    # Prompt Template
    {
        "name": "StructuredPromptTemplate",
        "category": "prompt_template",
        "description": "Structured prompt template with variable substitution and validation",
        "language": "python",
        "code": '''"""Structured Prompt Template.

A flexible prompt template system with validation.
"""

import re
from typing import Dict, List, Optional, Any
from string import Template


class StructuredPromptTemplate:
    """Structured prompt template with validation."""
    
    def __init__(
        self,
        template: str,
        required_vars: Optional[List[str]] = None,
        default_values: Optional[Dict[str, Any]] = None,
    ):
        """Initialize the prompt template.
        
        Args:
            template: Template string with {var} placeholders
            required_vars: List of required variables
            default_values: Default values for optional variables
        """
        self.template = template
        self.required_vars = required_vars or []
        self.default_values = default_values or {}
        
        # Extract variables from template
        self.variables = set(re.findall(r'\\{(\\w+)\\}', template))
    
    def validate(self, **kwargs) -> tuple[bool, List[str]]:
        """Validate that all required variables are provided.
        
        Returns:
            Tuple of (is_valid, list of missing variables)
        """
        provided = set(kwargs.keys()) | set(self.default_values.keys())
        missing = [v for v in self.required_vars if v not in provided]
        return len(missing) == 0, missing
    
    def format(self, **kwargs) -> str:
        """Format the template with provided values.
        
        Args:
            **kwargs: Variable values
        
        Returns:
            Formatted prompt string
        
        Raises:
            ValueError: If required variables are missing
        """
        is_valid, missing = self.validate(**kwargs)
        if not is_valid:
            raise ValueError(f"Missing required variables: {missing}")
        
        # Merge defaults with provided values
        values = {**self.default_values, **kwargs}
        
        # Use safe substitution
        result = self.template
        for var, value in values.items():
            result = result.replace(f"{{{var}}}", str(value))
        
        return result
    
    def get_variables(self) -> Dict[str, str]:
        """Get all variables with their status.
        
        Returns:
            Dict mapping variable name to status (required/optional/default)
        """
        result = {}
        for var in self.variables:
            if var in self.required_vars:
                result[var] = "required"
            elif var in self.default_values:
                result[var] = f"default: {self.default_values[var]}"
            else:
                result[var] = "optional"
        return result
''',
        "usage_example": '''# Create a template
template = StructuredPromptTemplate(
    template=\"\"\"You are a {role} assistant.

Your task is to {task}.

Context:
{context}

Please respond in {format} format.
\"\"\",
    required_vars=["role", "task"],
    default_values={"format": "markdown"},
)

# Format the template
prompt = template.format(
    role="research",
    task="analyze the provided data",
    context="Sales data from Q1 2024...",
)
print(prompt)
''',
        "tags": ["prompt", "template", "llm"],
        "metadata": {},
    },
    # === Dify-Style Workflow Node Components ===
    # LLM Node - Configurable LLM invocation
    {
        "name": "LLMNode",
        "category": "workflow_node",
        "description": "Dify-style LLM node for configurable model invocation with prompt templates and parameters",
        "language": "python",
        "code": '''"""LLM Workflow Node.

A configurable LLM node for workflow orchestration inspired by Dify.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class LLMNodeConfig:
    """Configuration for LLM node."""
    model: str = "llama3.2"
    temperature: float = 0.7
    max_tokens: int = 2048
    system_prompt: str = ""
    output_schema: Optional[Dict] = None
    stop_sequences: List[str] = field(default_factory=list)


class LLMNode:
    """Dify-style LLM workflow node."""
    
    def __init__(
        self,
        config: Optional[LLMNodeConfig] = None,
        ollama_host: str = "http://localhost:11434",
    ):
        """Initialize the LLM node.
        
        Args:
            config: Node configuration
            ollama_host: Ollama server URL
        """
        self.config = config or LLMNodeConfig()
        self.ollama_host = ollama_host
    
    async def execute(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        variables: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Execute the LLM node.
        
        Args:
            prompt: User prompt template
            context: Additional context data
            variables: Variables for prompt substitution
        
        Returns:
            Dictionary with response and metadata
        """
        import httpx
        
        # Substitute variables in prompt
        formatted_prompt = prompt
        if variables:
            for key, value in variables.items():
                formatted_prompt = formatted_prompt.replace(f"{{{key}}}", str(value))
        
        # Build messages
        messages = []
        if self.config.system_prompt:
            messages.append({"role": "system", "content": self.config.system_prompt})
        messages.append({"role": "user", "content": formatted_prompt})
        
        # Call Ollama
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                f"{self.ollama_host}/api/chat",
                json={
                    "model": self.config.model,
                    "messages": messages,
                    "options": {
                        "temperature": self.config.temperature,
                        "num_predict": self.config.max_tokens,
                    },
                    "stream": False,
                },
            )
            response.raise_for_status()
            data = response.json()
        
        return {
            "output": data.get("message", {}).get("content", ""),
            "model": self.config.model,
            "tokens_used": data.get("eval_count", 0),
            "context": context,
        }
''',
        "usage_example": '''# Create LLM node
config = LLMNodeConfig(
    model="llama3.2",
    temperature=0.3,
    system_prompt="You are a helpful coding assistant.",
)
node = LLMNode(config)

# Execute node
result = await node.execute(
    prompt="Explain {concept} in simple terms.",
    variables={"concept": "recursion"},
)
print(result["output"])
''',
        "tags": ["workflow", "llm", "dify", "node"],
        "metadata": {"inspired_by": "dify", "requires": "ollama"},
    },
    # Knowledge Retrieval Node - RAG retrieval with chunking
    {
        "name": "KnowledgeRetrievalNode",
        "category": "workflow_node",
        "description": "RAGFlow-style knowledge retrieval node with chunking, embedding, and semantic search",
        "language": "python",
        "code": '''"""Knowledge Retrieval Workflow Node.

A RAG retrieval node for knowledge base queries inspired by RAGFlow.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class RetrievalConfig:
    """Configuration for retrieval node."""
    top_k: int = 5
    score_threshold: float = 0.5
    reranking: bool = True
    chunk_size: int = 512
    chunk_overlap: int = 64


class KnowledgeRetrievalNode:
    """RAGFlow-style knowledge retrieval node."""
    
    def __init__(
        self,
        config: Optional[RetrievalConfig] = None,
        vector_store = None,
        embedder = None,
    ):
        """Initialize the retrieval node.
        
        Args:
            config: Node configuration
            vector_store: Vector store instance
            embedder: Embedding model instance
        """
        self.config = config or RetrievalConfig()
        self.vector_store = vector_store
        self.embedder = embedder
    
    def execute(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        knowledge_base_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Execute the retrieval node.
        
        Args:
            query: Search query
            filters: Optional metadata filters
            knowledge_base_ids: Optional knowledge base IDs to search
        
        Returns:
            Dictionary with retrieved chunks and metadata
        """
        if not self.vector_store or not self.embedder:
            return {"error": "Vector store or embedder not configured"}
        
        # Generate query embedding
        query_embedding = self.embedder.embed_query(query)
        
        # Search vector store
        results = self.vector_store.search(
            query_embedding=query_embedding,
            top_k=self.config.top_k * 2 if self.config.reranking else self.config.top_k,
            filter=filters,
        )
        
        # Filter by score threshold
        filtered_results = [
            r for r in results
            if r.get("score", 0) >= self.config.score_threshold
        ]
        
        # Rerank if enabled (simple relevance reranking)
        if self.config.reranking and len(filtered_results) > self.config.top_k:
            filtered_results = sorted(
                filtered_results,
                key=lambda x: x.get("score", 0),
                reverse=True,
            )[:self.config.top_k]
        
        return {
            "chunks": filtered_results,
            "query": query,
            "total_retrieved": len(filtered_results),
            "config": {
                "top_k": self.config.top_k,
                "threshold": self.config.score_threshold,
            },
        }
    
    def format_context(self, retrieval_result: Dict[str, Any]) -> str:
        """Format retrieved chunks into context string.
        
        Args:
            retrieval_result: Result from execute()
        
        Returns:
            Formatted context string
        """
        chunks = retrieval_result.get("chunks", [])
        if not chunks:
            return "No relevant information found."
        
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            content = chunk.get("content", chunk.get("text", ""))
            source = chunk.get("metadata", {}).get("source", "Unknown")
            context_parts.append(f"[{i}] ({source}):\\n{content}")
        
        return "\\n\\n".join(context_parts)
''',
        "usage_example": '''# Create retrieval node
config = RetrievalConfig(top_k=3, score_threshold=0.6)
node = KnowledgeRetrievalNode(
    config=config,
    vector_store=my_vector_store,
    embedder=my_embedder,
)

# Retrieve knowledge
result = node.execute("How do I configure the API?")
context = node.format_context(result)
print(f"Found {result['total_retrieved']} relevant chunks")
''',
        "tags": ["workflow", "rag", "retrieval", "ragflow", "node"],
        "metadata": {"inspired_by": "ragflow"},
    },
    # Conditional Branch Node
    {
        "name": "ConditionalBranchNode",
        "category": "workflow_node",
        "description": "Conditional branching node for workflow decision making with multiple conditions",
        "language": "python",
        "code": '''"""Conditional Branch Workflow Node.

A decision node for workflow branching based on conditions.
"""

from typing import Any, Callable, Dict, List, Optional, Union
from dataclasses import dataclass


@dataclass
class Condition:
    """A condition for branching."""
    name: str
    expression: str  # Python expression or key path
    operator: str  # eq, ne, gt, lt, gte, lte, contains, in
    value: Any
    target_branch: str


class ConditionalBranchNode:
    """Conditional branching node for workflows."""
    
    def __init__(
        self,
        conditions: Optional[List[Condition]] = None,
        default_branch: str = "default",
    ):
        """Initialize the conditional node.
        
        Args:
            conditions: List of conditions to evaluate
            default_branch: Default branch if no conditions match
        """
        self.conditions = conditions or []
        self.default_branch = default_branch
    
    def add_condition(
        self,
        name: str,
        expression: str,
        operator: str,
        value: Any,
        target_branch: str,
    ) -> "ConditionalBranchNode":
        """Add a condition.
        
        Args:
            name: Condition name
            expression: Expression to evaluate (key path in data)
            operator: Comparison operator
            value: Value to compare against
            target_branch: Branch to take if condition is true
        
        Returns:
            Self for chaining
        """
        self.conditions.append(Condition(
            name=name,
            expression=expression,
            operator=operator,
            value=value,
            target_branch=target_branch,
        ))
        return self
    
    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the conditional node.
        
        Args:
            data: Input data to evaluate conditions against
        
        Returns:
            Dictionary with selected branch and matched condition
        """
        for condition in self.conditions:
            if self._evaluate_condition(condition, data):
                return {
                    "branch": condition.target_branch,
                    "matched_condition": condition.name,
                    "data": data,
                }
        
        return {
            "branch": self.default_branch,
            "matched_condition": None,
            "data": data,
        }
    
    def _get_value(self, data: Dict, path: str) -> Any:
        """Get value from data using dot notation path."""
        parts = path.split(".")
        current = data
        for part in parts:
            if isinstance(current, dict):
                current = current.get(part)
            else:
                return None
        return current
    
    def _evaluate_condition(self, condition: Condition, data: Dict) -> bool:
        """Evaluate a single condition."""
        actual_value = self._get_value(data, condition.expression)
        expected_value = condition.value
        
        operators = {
            "eq": lambda a, b: a == b,
            "ne": lambda a, b: a != b,
            "gt": lambda a, b: a > b,
            "lt": lambda a, b: a < b,
            "gte": lambda a, b: a >= b,
            "lte": lambda a, b: a <= b,
            "contains": lambda a, b: b in a if a else False,
            "in": lambda a, b: a in b if b else False,
            "exists": lambda a, b: a is not None,
            "empty": lambda a, b: not a,
        }
        
        op_func = operators.get(condition.operator)
        if op_func:
            try:
                return op_func(actual_value, expected_value)
            except (TypeError, ValueError):
                return False
        return False
''',
        "usage_example": '''# Create conditional node
node = ConditionalBranchNode(default_branch="error_handler")

# Add conditions
node.add_condition(
    name="high_confidence",
    expression="result.confidence",
    operator="gte",
    value=0.9,
    target_branch="direct_response",
).add_condition(
    name="needs_review",
    expression="result.confidence",
    operator="gte",
    value=0.5,
    target_branch="human_review",
)

# Execute
data = {"result": {"confidence": 0.85, "answer": "..."}}
result = node.execute(data)
print(f"Selected branch: {result['branch']}")
''',
        "tags": ["workflow", "conditional", "branching", "node"],
        "metadata": {"inspired_by": "dify"},
    },
    # Iteration Node
    {
        "name": "IterationNode",
        "category": "workflow_node",
        "description": "Iteration node for batch processing and looping over collections",
        "language": "python",
        "code": '''"""Iteration Workflow Node.

A node for processing collections and batch operations.
"""

from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass
import asyncio


@dataclass
class IterationConfig:
    """Configuration for iteration node."""
    max_iterations: int = 100
    parallel: bool = False
    max_parallel: int = 5
    continue_on_error: bool = True


class IterationNode:
    """Iteration node for batch processing."""
    
    def __init__(
        self,
        config: Optional[IterationConfig] = None,
        processor: Optional[Callable] = None,
    ):
        """Initialize the iteration node.
        
        Args:
            config: Node configuration
            processor: Function to process each item
        """
        self.config = config or IterationConfig()
        self.processor = processor
    
    def set_processor(self, processor: Callable) -> "IterationNode":
        """Set the processor function.
        
        Args:
            processor: Function(item, index, context) -> result
        
        Returns:
            Self for chaining
        """
        self.processor = processor
        return self
    
    def execute(
        self,
        items: List[Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Execute iteration over items.
        
        Args:
            items: Items to iterate over
            context: Shared context for all iterations
        
        Returns:
            Dictionary with results and statistics
        """
        if not self.processor:
            return {"error": "No processor function set"}
        
        context = context or {}
        results = []
        errors = []
        
        # Limit iterations
        items_to_process = items[:self.config.max_iterations]
        
        for i, item in enumerate(items_to_process):
            try:
                result = self.processor(item, i, context)
                results.append({
                    "index": i,
                    "input": item,
                    "output": result,
                    "success": True,
                })
            except Exception as e:
                error_entry = {
                    "index": i,
                    "input": item,
                    "error": str(e),
                    "success": False,
                }
                errors.append(error_entry)
                results.append(error_entry)
                
                if not self.config.continue_on_error:
                    break
        
        return {
            "results": results,
            "total_processed": len(results),
            "successful": len([r for r in results if r.get("success")]),
            "failed": len(errors),
            "errors": errors,
        }
    
    async def execute_async(
        self,
        items: List[Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Execute iteration with async parallel processing.
        
        Args:
            items: Items to iterate over
            context: Shared context for all iterations
        
        Returns:
            Dictionary with results and statistics
        """
        if not self.processor:
            return {"error": "No processor function set"}
        
        context = context or {}
        items_to_process = items[:self.config.max_iterations]
        
        if not self.config.parallel:
            return self.execute(items_to_process, context)
        
        # Parallel execution with semaphore
        semaphore = asyncio.Semaphore(self.config.max_parallel)
        
        async def process_with_semaphore(item, index):
            async with semaphore:
                try:
                    if asyncio.iscoroutinefunction(self.processor):
                        result = await self.processor(item, index, context)
                    else:
                        result = self.processor(item, index, context)
                    return {"index": index, "input": item, "output": result, "success": True}
                except Exception as e:
                    return {"index": index, "input": item, "error": str(e), "success": False}
        
        tasks = [process_with_semaphore(item, i) for i, item in enumerate(items_to_process)]
        results = await asyncio.gather(*tasks)
        
        # Sort by index
        results = sorted(results, key=lambda x: x["index"])
        errors = [r for r in results if not r.get("success")]
        
        return {
            "results": results,
            "total_processed": len(results),
            "successful": len([r for r in results if r.get("success")]),
            "failed": len(errors),
            "errors": errors,
        }
''',
        "usage_example": '''# Create iteration node
config = IterationConfig(max_iterations=50, parallel=True, max_parallel=3)
node = IterationNode(config)

# Set processor
def process_item(item, index, context):
    # Process each item
    return f"Processed: {item}"

node.set_processor(process_item)

# Execute
items = ["item1", "item2", "item3"]
result = node.execute(items)
print(f"Processed {result['successful']} items")
''',
        "tags": ["workflow", "iteration", "batch", "loop", "node"],
        "metadata": {"inspired_by": "dify"},
    },
    # HTTP Request Node
    {
        "name": "HTTPRequestNode",
        "category": "workflow_node",
        "description": "HTTP request node for external API integration in workflows",
        "language": "python",
        "code": '''"""HTTP Request Workflow Node.

A node for making HTTP requests to external APIs.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
import json


@dataclass
class HTTPRequestConfig:
    """Configuration for HTTP request node."""
    timeout: int = 30
    retries: int = 3
    retry_delay: float = 1.0
    follow_redirects: bool = True


class HTTPRequestNode:
    """HTTP request node for API calls."""
    
    def __init__(
        self,
        config: Optional[HTTPRequestConfig] = None,
    ):
        """Initialize the HTTP request node.
        
        Args:
            config: Node configuration
        """
        self.config = config or HTTPRequestConfig()
    
    async def execute(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, str]] = None,
        body: Optional[Any] = None,
        auth: Optional[tuple] = None,
    ) -> Dict[str, Any]:
        """Execute HTTP request.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            url: Request URL
            headers: Request headers
            params: Query parameters
            body: Request body (will be JSON encoded if dict)
            auth: Basic auth tuple (username, password)
        
        Returns:
            Dictionary with response data
        """
        import httpx
        
        headers = headers or {}
        
        # Prepare body
        content = None
        json_body = None
        if body:
            if isinstance(body, dict):
                json_body = body
            else:
                content = body
        
        # Execute with retries
        last_error = None
        for attempt in range(self.config.retries):
            try:
                async with httpx.AsyncClient(
                    timeout=self.config.timeout,
                    follow_redirects=self.config.follow_redirects,
                ) as client:
                    response = await client.request(
                        method=method.upper(),
                        url=url,
                        headers=headers,
                        params=params,
                        json=json_body,
                        content=content,
                        auth=auth,
                    )
                    
                    # Parse response
                    try:
                        response_body = response.json()
                    except json.JSONDecodeError:
                        response_body = response.text
                    
                    return {
                        "status_code": response.status_code,
                        "headers": dict(response.headers),
                        "body": response_body,
                        "success": response.is_success,
                        "url": str(response.url),
                    }
                    
            except Exception as e:
                last_error = str(e)
                if attempt < self.config.retries - 1:
                    import asyncio
                    await asyncio.sleep(self.config.retry_delay * (attempt + 1))
        
        return {
            "success": False,
            "error": last_error,
            "url": url,
            "attempts": self.config.retries,
        }
''',
        "usage_example": '''# Create HTTP node
node = HTTPRequestNode(HTTPRequestConfig(timeout=10, retries=2))

# Make request
result = await node.execute(
    method="POST",
    url="https://api.example.com/data",
    headers={"Authorization": "Bearer token"},
    body={"query": "test"},
)

if result["success"]:
    print(f"Response: {result['body']}")
else:
    print(f"Error: {result['error']}")
''',
        "tags": ["workflow", "http", "api", "request", "node"],
        "metadata": {"inspired_by": "dify"},
    },
    # Code Executor Node
    {
        "name": "CodeExecutorNode",
        "category": "workflow_node",
        "description": "Sandboxed code execution node for running Python/JavaScript in workflows",
        "language": "python",
        "code": '''"""Code Executor Workflow Node.

A sandboxed code execution node for workflows.
"""

from typing import Any, Dict, Optional
from dataclasses import dataclass
import ast
import sys
from io import StringIO


@dataclass
class CodeExecutorConfig:
    """Configuration for code executor node."""
    language: str = "python"
    timeout: int = 30
    max_output_size: int = 10000
    allowed_imports: list = None


class CodeExecutorNode:
    """Sandboxed code execution node."""
    
    # Safe built-ins for sandbox
    SAFE_BUILTINS = {
        "abs", "all", "any", "ascii", "bin", "bool", "chr", "dict",
        "divmod", "enumerate", "filter", "float", "format", "frozenset",
        "getattr", "hasattr", "hash", "hex", "int", "isinstance",
        "issubclass", "iter", "len", "list", "map", "max", "min",
        "next", "oct", "ord", "pow", "print", "range", "repr",
        "reversed", "round", "set", "slice", "sorted", "str", "sum",
        "tuple", "type", "zip",
    }
    
    def __init__(
        self,
        config: Optional[CodeExecutorConfig] = None,
    ):
        """Initialize the code executor node.
        
        Args:
            config: Node configuration
        """
        self.config = config or CodeExecutorConfig()
        self.config.allowed_imports = self.config.allowed_imports or [
            "json", "math", "datetime", "re", "collections", "itertools",
        ]
    
    def execute(
        self,
        code: str,
        inputs: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Execute code in sandbox.
        
        Args:
            code: Code to execute
            inputs: Input variables to make available
        
        Returns:
            Dictionary with outputs and execution info
        """
        if self.config.language == "python":
            return self._execute_python(code, inputs or {})
        else:
            return {"error": f"Unsupported language: {self.config.language}"}
    
    def _execute_python(
        self,
        code: str,
        inputs: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute Python code in sandbox."""
        # Validate code (basic AST check)
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return {"error": f"Syntax error: {e}", "success": False}
        
        # Check for forbidden operations
        forbidden = self._check_forbidden(tree)
        if forbidden:
            return {"error": f"Forbidden operation: {forbidden}", "success": False}
        
        # Setup sandbox environment
        sandbox_globals = {
            "__builtins__": {k: getattr(__builtins__, k) if hasattr(__builtins__, k) else __builtins__[k]
                           for k in self.SAFE_BUILTINS
                           if (hasattr(__builtins__, k) if isinstance(__builtins__, type(__builtins__)) 
                               else k in __builtins__)},
        }
        
        # Add allowed imports
        for module_name in self.config.allowed_imports:
            try:
                sandbox_globals[module_name] = __import__(module_name)
            except ImportError:
                pass
        
        # Add inputs
        sandbox_globals.update(inputs)
        sandbox_globals["__inputs__"] = inputs
        
        # Capture output
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()
        
        outputs = {}
        error = None
        
        try:
            exec(compile(tree, "<sandbox>", "exec"), sandbox_globals)
            
            # Extract outputs (variables that start with output_)
            outputs = {
                k: v for k, v in sandbox_globals.items()
                if k.startswith("output_") or k == "result"
            }
            
        except Exception as e:
            error = f"{type(e).__name__}: {e}"
        finally:
            sys.stdout = old_stdout
        
        stdout = captured_output.getvalue()[:self.config.max_output_size]
        
        return {
            "success": error is None,
            "outputs": outputs,
            "stdout": stdout,
            "error": error,
        }
    
    def _check_forbidden(self, tree: ast.AST) -> Optional[str]:
        """Check for forbidden operations in AST."""
        forbidden_names = {"eval", "exec", "compile", "open", "__import__", "globals", "locals"}
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id in forbidden_names:
                return node.id
            if isinstance(node, ast.Attribute) and node.attr.startswith("_"):
                return f"private attribute: {node.attr}"
        
        return None
''',
        "usage_example": '''# Create code executor
node = CodeExecutorNode(CodeExecutorConfig(timeout=5))

# Execute code
code = \"\"\"
import json

data = json.loads(__inputs__["json_str"])
result = sum(data["values"])
output_sum = result
print(f"Calculated sum: {result}")
\"\"\"

result = node.execute(
    code=code,
    inputs={"json_str": '{"values": [1, 2, 3, 4, 5]}'},
)

if result["success"]:
    print(f"Sum: {result['outputs']['output_sum']}")
    print(f"Output: {result['stdout']}")
''',
        "tags": ["workflow", "code", "executor", "sandbox", "node"],
        "metadata": {"inspired_by": "dify", "security": "sandboxed"},
    },
    # Variable Aggregator Node
    {
        "name": "VariableAggregatorNode",
        "category": "workflow_node",
        "description": "Variable aggregator node for collecting and transforming data across workflow branches",
        "language": "python",
        "code": '''"""Variable Aggregator Workflow Node.

A node for aggregating and transforming variables from multiple sources.
"""

from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass


@dataclass 
class AggregatorConfig:
    """Configuration for aggregator node."""
    merge_strategy: str = "merge"  # merge, concat, sum, first, last
    flatten_lists: bool = False
    remove_nulls: bool = True


class VariableAggregatorNode:
    """Variable aggregator for data transformation."""
    
    def __init__(
        self,
        config: Optional[AggregatorConfig] = None,
        mappings: Optional[Dict[str, str]] = None,
    ):
        """Initialize the aggregator node.
        
        Args:
            config: Node configuration
            mappings: Variable mappings (output_name -> input_path)
        """
        self.config = config or AggregatorConfig()
        self.mappings = mappings or {}
    
    def add_mapping(
        self,
        output_name: str,
        input_path: str,
        transform: Optional[Callable] = None,
    ) -> "VariableAggregatorNode":
        """Add a variable mapping.
        
        Args:
            output_name: Name in output
            input_path: Path in input data (dot notation)
            transform: Optional transform function
        
        Returns:
            Self for chaining
        """
        self.mappings[output_name] = {
            "path": input_path,
            "transform": transform,
        }
        return self
    
    def execute(
        self,
        *inputs: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Aggregate variables from multiple inputs.
        
        Args:
            *inputs: Input dictionaries to aggregate
        
        Returns:
            Aggregated output dictionary
        """
        # Merge inputs based on strategy
        merged = self._merge_inputs(list(inputs))
        
        # Apply mappings
        output = {}
        for output_name, mapping in self.mappings.items():
            if isinstance(mapping, str):
                # Simple path mapping
                value = self._get_path(merged, mapping)
            else:
                # Mapping with transform
                value = self._get_path(merged, mapping["path"])
                if mapping.get("transform") and value is not None:
                    value = mapping["transform"](value)
            
            if value is not None or not self.config.remove_nulls:
                output[output_name] = value
        
        # If no mappings, return merged data
        if not self.mappings:
            output = merged
        
        return {
            "output": output,
            "input_count": len(inputs),
            "strategy": self.config.merge_strategy,
        }
    
    def _merge_inputs(self, inputs: List[Dict]) -> Dict:
        """Merge multiple input dictionaries."""
        if not inputs:
            return {}
        
        if self.config.merge_strategy == "first":
            return inputs[0]
        
        if self.config.merge_strategy == "last":
            return inputs[-1]
        
        if self.config.merge_strategy == "concat":
            # Concatenate list values
            result = {}
            for inp in inputs:
                for k, v in inp.items():
                    if k in result and isinstance(result[k], list):
                        if isinstance(v, list):
                            result[k].extend(v)
                        else:
                            result[k].append(v)
                    elif k in result:
                        result[k] = [result[k], v]
                    else:
                        result[k] = [v] if not isinstance(v, list) else v
            return result
        
        # Default: merge (later values overwrite)
        result = {}
        for inp in inputs:
            result.update(inp)
        return result
    
    def _get_path(self, data: Dict, path: str) -> Any:
        """Get value from nested dict using dot notation."""
        parts = path.split(".")
        current = data
        for part in parts:
            if isinstance(current, dict):
                current = current.get(part)
            elif isinstance(current, list) and part.isdigit():
                idx = int(part)
                current = current[idx] if idx < len(current) else None
            else:
                return None
        return current
''',
        "usage_example": '''# Create aggregator
node = VariableAggregatorNode()

# Add mappings
node.add_mapping("user_name", "user.name")
node.add_mapping("total", "results.count", transform=lambda x: x * 2)

# Aggregate from multiple sources
result = node.execute(
    {"user": {"name": "Alice", "id": 1}},
    {"results": {"count": 5, "items": []}},
)

print(result["output"])  # {"user_name": "Alice", "total": 10}
''',
        "tags": ["workflow", "aggregator", "transform", "variables", "node"],
        "metadata": {"inspired_by": "dify"},
    },
    {
        "name": "GlobalRepoIngestionPipeline",
        "category": "template",
        "description": "Pipeline template for cloning and ingesting Git repos into the global knowledgebase",
        "language": "python",
        "code": '''"""Global Repo Ingestion Pipeline.

Clone/pull tracked Git repositories, index code into the vector store,
and write plaintext summaries per run.
"""

from agentic_assistants.data.catalog import DataCatalog
from agentic_assistants.pipelines.runners import SequentialRunner
from agentic_assistants.pipelines.templates import create_repo_ingestion_pipeline

pipeline = create_repo_ingestion_pipeline(
    config_path="examples/global-knowledgebase-starter/config.yaml",
)
runner = SequentialRunner()
result = runner.run(pipeline, DataCatalog())
print(result.outputs.get("summary_result"))
''',
        "usage_example": '''# Run the global repo ingestion pipeline
from agentic_assistants.data.catalog import DataCatalog
from agentic_assistants.pipelines.runners import SequentialRunner
from agentic_assistants.pipelines.templates import create_repo_ingestion_pipeline

pipeline = create_repo_ingestion_pipeline(
    config_path="examples/global-knowledgebase-starter/config.yaml",
)
runner = SequentialRunner()
runner.run(pipeline, DataCatalog())
''',
        "tags": ["pipeline", "ingestion", "git", "knowledgebase", "starter"],
        "metadata": {"starter_id": "global-knowledgebase-starter"},
    },
    {
        "name": "McpOllamaCodingAgent",
        "category": "agent",
        "description": "Ollama-based coding agent that retrieves context via MCP tools",
        "language": "python",
        "code": '''"""MCP + Ollama coding agent.

Uses the MCP server's search tool to retrieve code context,
then answers with Ollama.
"""

from agentic_assistants import AgenticConfig
from agentic_assistants.agents import McpOllamaCodingAgent

config = AgenticConfig()
agent = McpOllamaCodingAgent(
    config=config,
    collection="global-knowledgebase",
    top_k=6,
)

answer = agent.answer("Where is the repo ingestion pipeline defined?")
print(answer)
''',
        "usage_example": '''# Ask a question with MCP context
from agentic_assistants import AgenticConfig
from agentic_assistants.agents import McpOllamaCodingAgent

agent = McpOllamaCodingAgent(
    config=AgenticConfig(),
    collection="global-knowledgebase",
    top_k=5,
)

print(agent.answer("How do we schedule repository ingestion?"))
''',
        "tags": ["agent", "mcp", "ollama", "coding"],
        "metadata": {"starter_id": "global-knowledgebase-starter"},
    },
]


@router.post("/base/install")
async def install_base_components() -> dict:
    """Install base components from installed packages."""
    store = _get_store()
    installed = []
    skipped = []
    errors = []
    
    for component_data in BASE_COMPONENTS:
        try:
            # Check if component already exists
            existing, _ = store.list_components(search=component_data["name"])
            if any(c.name == component_data["name"] for c in existing):
                skipped.append(component_data["name"])
                continue
            
            # Create component
            component = store.create_component(**component_data)
            installed.append(component.name)
        except Exception as e:
            errors.append(f"{component_data['name']}: {str(e)}")
    
    return {
        "installed": installed,
        "skipped": skipped,
        "errors": errors,
        "total_base_components": len(BASE_COMPONENTS),
    }

