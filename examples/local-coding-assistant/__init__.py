"""
Local Coding Assistant Starter Project.

A comprehensive coding assistant with RAG, memory persistence,
and episodic learning capabilities for local development.

Example:
    >>> from examples.local_coding_assistant import CodingAssistant
    >>> assistant = CodingAssistant()
    >>> response = assistant.ask("How does the auth module work?")
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from agentic_assistants.config import AgenticConfig
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)

# Package info
__version__ = "0.1.0"
__author__ = "Agentic Assistants Team"

# Default config path
DEFAULT_CONFIG_PATH = Path(__file__).parent / "config.yaml"


class CodingAssistant:
    """
    Main coding assistant interface.
    
    Provides a simple API for interacting with the coding assistant,
    including question answering, memory management, and caching.
    
    Example:
        >>> assistant = CodingAssistant()
        >>> response = assistant.ask("What does the UserService do?")
        >>> print(response)
        
        >>> # Access memory
        >>> history = assistant.memory.get_recent_episodes(limit=5)
        
        >>> # Access cache
        >>> solution = assistant.cache.get("jwt-validation")
    """
    
    def __init__(
        self,
        config_path: Optional[str] = None,
        project_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ):
        """
        Initialize the coding assistant.
        
        Args:
            config_path: Path to configuration file
            project_id: Project identifier for scoping
            user_id: User identifier for personalization
        """
        self.config_path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH
        self.project_id = project_id
        self.user_id = user_id
        
        # Load configuration
        self._config = self._load_config()
        
        # Initialize components (lazy loaded)
        self._agent = None
        self._memory = None
        self._episodic = None
        self._cache = None
        self._vectordb = None
        self._lineage = None
        
        logger.info(f"CodingAssistant initialized with config: {self.config_path}")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if self.config_path.exists():
            with open(self.config_path) as f:
                return yaml.safe_load(f)
        return {}
    
    @property
    def memory(self):
        """Get the memory store."""
        if self._memory is None:
            from agentic_assistants.memory import get_memory_store
            self._memory = get_memory_store(
                backend=self._config.get("memory", {}).get("backend", "mem0"),
                user_id=self.user_id,
            )
        return self._memory
    
    @property
    def episodic(self):
        """Get the episodic memory manager."""
        if self._episodic is None:
            from agentic_assistants.memory import EpisodicMemory
            self._episodic = EpisodicMemory(memory_store=self.memory)
        return self._episodic
    
    @property
    def cache(self):
        """Get the solution cache."""
        if self._cache is None:
            from agentic_assistants.cache import get_solution_cache
            self._cache = get_solution_cache()
        return self._cache
    
    @property
    def vectordb(self):
        """Get the scoped vector store."""
        if self._vectordb is None:
            from agentic_assistants.vectordb.scoped_store import ScopedVectorStore
            self._vectordb = ScopedVectorStore(
                project_id=self.project_id or self._config.get("project", {}).get("id"),
                user_id=self.user_id,
            )
        return self._vectordb
    
    @property
    def lineage(self):
        """Get the lineage tracker."""
        if self._lineage is None:
            from agentic_assistants.lineage import get_lineage_tracker
            self._lineage = get_lineage_tracker()
        return self._lineage
    
    def ask(
        self,
        question: str,
        use_memory: bool = True,
        use_codebase: bool = True,
        collection: str = "codebase",
    ) -> str:
        """
        Ask a question to the coding assistant.
        
        Args:
            question: The question to ask
            use_memory: Include relevant memories in context
            use_codebase: Search codebase for relevant code
            collection: Vector store collection to search
            
        Returns:
            Assistant's response
        """
        context_parts = []
        
        # Get relevant memories
        if use_memory:
            memory_context = self.memory.get_relevant_context(
                query=question,
                max_memories=self._config.get("agents", {}).get("coding_assistant", {}).get("memory", {}).get("context_limit", 5),
            )
            if memory_context:
                context_parts.append(f"Relevant memories:\n{memory_context}")
        
        # Search codebase
        if use_codebase:
            results = self.vectordb.search(
                query=question,
                collection=collection,
                top_k=5,
            )
            if results:
                code_context = "\n\n".join([
                    f"File: {r.document.metadata.get('source', 'unknown')}\n```\n{r.document.content[:1000]}...\n```"
                    for r in results
                ])
                context_parts.append(f"Relevant code:\n{code_context}")
        
        # Build prompt
        system_prompt = self._config.get("agents", {}).get("coding_assistant", {}).get(
            "system_prompt",
            "You are a helpful coding assistant."
        )
        
        context = "\n\n".join(context_parts) if context_parts else ""
        
        # Get LLM response
        response = self._get_llm_response(
            system_prompt=system_prompt,
            question=question,
            context=context,
        )
        
        # Record interaction
        self.episodic.record_conversation(
            user_message=question,
            assistant_response=response,
            context={"collection": collection, "use_memory": use_memory},
        )
        
        return response
    
    def _get_llm_response(
        self,
        system_prompt: str,
        question: str,
        context: str,
    ) -> str:
        """Get response from LLM."""
        llm_config = self._config.get("llm", {})
        provider = llm_config.get("provider", "ollama")
        
        full_prompt = f"{system_prompt}\n\n{context}\n\nUser: {question}\n\nAssistant:"
        
        try:
            if provider == "ollama":
                import ollama
                response = ollama.chat(
                    model=llm_config.get("model", "llama3.2"),
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"{context}\n\n{question}"},
                    ],
                )
                return response["message"]["content"]
            
            elif provider == "openai":
                import openai
                client = openai.OpenAI(api_key=llm_config.get("api_key"))
                response = client.chat.completions.create(
                    model=llm_config.get("model", "gpt-4-turbo-preview"),
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"{context}\n\n{question}"},
                    ],
                    temperature=llm_config.get("temperature", 0.7),
                    max_tokens=llm_config.get("max_tokens", 4096),
                )
                return response.choices[0].message.content
            
            else:
                return f"Unknown LLM provider: {provider}"
                
        except Exception as e:
            logger.error(f"LLM error: {e}")
            return f"Error getting response: {e}"
    
    def index_codebase(
        self,
        path: str,
        collection: str = "codebase",
        incremental: bool = True,
    ) -> Dict[str, Any]:
        """
        Index a codebase for searching.
        
        Args:
            path: Path to the codebase
            collection: Collection name
            incremental: Only index changed files
            
        Returns:
            Indexing results
        """
        from pathlib import Path as PathLib
        
        indexing_config = self._config.get("indexing", {})
        include_patterns = indexing_config.get("include_patterns", ["**/*.py"])
        exclude_patterns = indexing_config.get("exclude_patterns", ["**/__pycache__/**"])
        
        codebase_path = PathLib(path)
        files_indexed = 0
        total_chunks = 0
        errors = []
        
        from agentic_assistants.vectordb import Document
        
        for pattern in include_patterns:
            for file_path in codebase_path.glob(pattern):
                # Check exclusions
                skip = False
                for exclude in exclude_patterns:
                    if file_path.match(exclude):
                        skip = True
                        break
                
                if skip or not file_path.is_file():
                    continue
                
                try:
                    content = file_path.read_text(encoding="utf-8", errors="ignore")
                    
                    # Chunk the content
                    chunk_size = indexing_config.get("chunk_size", 1000)
                    chunk_overlap = indexing_config.get("chunk_overlap", 200)
                    
                    chunks = self._chunk_content(content, chunk_size, chunk_overlap)
                    
                    # Create documents
                    documents = []
                    for i, chunk in enumerate(chunks):
                        doc = Document(
                            id=f"{file_path.name}_{i}",
                            content=chunk,
                            metadata={
                                "source": str(file_path),
                                "chunk_index": i,
                                "total_chunks": len(chunks),
                                "language": file_path.suffix,
                            },
                        )
                        documents.append(doc)
                    
                    # Add to vector store
                    if documents:
                        self.vectordb.add(documents, collection=collection)
                        total_chunks += len(documents)
                    
                    files_indexed += 1
                    
                    # Record lineage
                    self.lineage.record_ingestion(
                        document_id=f"file_{file_path.name}",
                        source_uri=str(file_path),
                        source_type="file",
                        collection=collection,
                        pipeline="index_codebase",
                        metadata={"chunks": len(chunks)},
                    )
                    
                except Exception as e:
                    errors.append(f"{file_path}: {e}")
                    logger.error(f"Error indexing {file_path}: {e}")
        
        logger.info(f"Indexed {files_indexed} files ({total_chunks} chunks)")
        
        return {
            "files_indexed": files_indexed,
            "total_chunks": total_chunks,
            "errors": errors,
            "collection": collection,
        }
    
    def _chunk_content(
        self,
        content: str,
        chunk_size: int,
        overlap: int,
    ) -> List[str]:
        """Split content into overlapping chunks."""
        if len(content) <= chunk_size:
            return [content]
        
        chunks = []
        start = 0
        
        while start < len(content):
            end = start + chunk_size
            chunk = content[start:end]
            chunks.append(chunk)
            start += chunk_size - overlap
        
        return chunks
    
    def get_stats(self) -> Dict[str, Any]:
        """Get assistant statistics."""
        return {
            "memory": self.memory.get_stats(),
            "cache": self.cache.get_stats(),
            "vectordb": self.vectordb.get_info(),
        }


# Export main class
__all__ = [
    "CodingAssistant",
    "DEFAULT_CONFIG_PATH",
]
