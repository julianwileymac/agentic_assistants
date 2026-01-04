"""
Jupyter Workspace context manager.

This module provides a workspace manager for Jupyter notebooks
that handles session state, resources, and provides a convenient
interface for interactive development.

Example:
    >>> from agentic_assistants import JupyterWorkspace
    >>> 
    >>> with JupyterWorkspace("my-session") as ws:
    ...     ws.index("./data")
    ...     results = ws.search("relevant docs")
    ...     ws.chat("Summarize these findings")
"""

import atexit
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Optional, Union

from agentic_assistants.config import AgenticConfig
from agentic_assistants.engine import AgenticEngine
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


class JupyterWorkspace:
    """
    Workspace manager for Jupyter notebooks.
    
    This class provides:
    - Automatic session management
    - Resource lifecycle management
    - State persistence between cells
    - Rich display integration
    - Convenient API for common operations
    
    The workspace is designed to be used as a context manager
    or as a long-lived object in a notebook.
    
    Attributes:
        engine: The underlying AgenticEngine
        session_name: Name of the current session
    """

    # Registry of active workspaces
    _instances: dict[str, "JupyterWorkspace"] = {}

    def __init__(
        self,
        session_name: str = "notebook",
        config: Optional[AgenticConfig] = None,
        auto_start_ollama: bool = True,
        display_status: bool = True,
    ):
        """
        Initialize a Jupyter workspace.
        
        Args:
            session_name: Session name for persistence
            config: Configuration instance
            auto_start_ollama: Start Ollama if not running
            display_status: Display status on initialization
        """
        self.session_name = session_name
        self.config = config or AgenticConfig()
        self._display_status = display_status
        
        # Initialize engine
        self.engine = AgenticEngine(
            config=self.config,
            session_name=session_name,
            auto_start_ollama=auto_start_ollama,
        )
        
        # Register instance
        JupyterWorkspace._instances[session_name] = self
        
        # Register cleanup on exit
        atexit.register(self._cleanup)
        
        if display_status:
            self._show_status()

    @classmethod
    def get_or_create(
        cls,
        session_name: str = "notebook",
        **kwargs,
    ) -> "JupyterWorkspace":
        """
        Get an existing workspace or create a new one.
        
        Args:
            session_name: Session name
            **kwargs: Arguments for JupyterWorkspace
        
        Returns:
            JupyterWorkspace instance
        """
        if session_name in cls._instances:
            return cls._instances[session_name]
        return cls(session_name, **kwargs)

    def _cleanup(self) -> None:
        """Cleanup resources on exit."""
        try:
            self.engine.close()
        except Exception:
            pass

    def _show_status(self) -> None:
        """Display workspace status."""
        try:
            from IPython.display import display, HTML
            
            status = self.engine.get_status()
            
            html = f"""
            <div style="padding: 10px; border: 1px solid #ddd; border-radius: 5px; 
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white; font-family: system-ui;">
                <h3 style="margin: 0 0 10px 0;">🚀 Agentic Workspace Ready</h3>
                <table style="color: white;">
                    <tr>
                        <td><strong>Session:</strong></td>
                        <td>{status['session']['name']}</td>
                    </tr>
                    <tr>
                        <td><strong>Ollama:</strong></td>
                        <td>{'✅ Running' if status['ollama']['running'] else '❌ Not Running'}</td>
                    </tr>
                    <tr>
                        <td><strong>Vector DB:</strong></td>
                        <td>{status['vector_store']['backend']}</td>
                    </tr>
                </table>
            </div>
            """
            display(HTML(html))
        except ImportError:
            # Not in Jupyter
            logger.info(f"Workspace ready: {self.session_name}")

    # === Convenience Methods ===

    def search(
        self,
        query: str,
        collection: str = "default",
        top_k: int = 5,
        display_results: bool = True,
    ) -> list:
        """
        Search the vector database.
        
        Args:
            query: Search query
            collection: Collection to search
            top_k: Number of results
            display_results: Display results in notebook
        
        Returns:
            List of search results
        """
        results = self.engine.search(query, collection, top_k)
        
        if display_results and results:
            self._display_search_results(query, results)
        
        return results

    def _display_search_results(self, query: str, results: list) -> None:
        """Display search results in a formatted way."""
        try:
            from IPython.display import display, HTML
            
            html_parts = [
                f"<div style='margin-bottom: 10px;'><strong>Search:</strong> {query}</div>"
            ]
            
            for i, r in enumerate(results, 1):
                file_path = r.document.metadata.get("file_path", "")
                content = r.document.content[:300] + "..." if len(r.document.content) > 300 else r.document.content
                content = content.replace("<", "&lt;").replace(">", "&gt;")
                
                html_parts.append(f"""
                <div style="border: 1px solid #e0e0e0; padding: 10px; margin: 5px 0; 
                            border-radius: 5px; background: #f9f9f9;">
                    <div style="display: flex; justify-content: space-between;">
                        <strong>{i}. {file_path}</strong>
                        <span style="color: #666;">Score: {r.score:.3f}</span>
                    </div>
                    <pre style="margin: 10px 0 0 0; font-size: 12px; 
                                overflow-x: auto; background: #fff; 
                                padding: 8px; border-radius: 3px;">{content}</pre>
                </div>
                """)
            
            display(HTML("".join(html_parts)))
        except ImportError:
            for r in results:
                print(f"- {r.document.metadata.get('file_path', 'unknown')}: {r.score:.3f}")

    def index(
        self,
        path: Union[str, Path],
        collection: str = "default",
        patterns: Optional[list[str]] = None,
        force: bool = False,
        show_progress: bool = True,
    ) -> dict:
        """
        Index a file or directory.
        
        Args:
            path: Path to index
            collection: Collection name
            patterns: File patterns
            force: Force re-indexing
            show_progress: Show progress bar
        
        Returns:
            Indexing statistics
        """
        callback = None
        progress_bar = None
        
        if show_progress:
            try:
                from tqdm.notebook import tqdm
                progress_bar = tqdm(total=100, desc="Indexing")
                last_percent = [0]
                
                def callback(current, total, path):
                    percent = int((current / total) * 100)
                    if percent > last_percent[0]:
                        progress_bar.update(percent - last_percent[0])
                        last_percent[0] = percent
                        progress_bar.set_postfix({"file": str(path).split("/")[-1][:30]})
                
            except ImportError:
                pass
        
        stats = self.engine.index_codebase(
            path=path,
            collection=collection,
            patterns=patterns,
            force=force,
            progress_callback=callback,
        )
        
        if progress_bar:
            progress_bar.close()
        
        self._display_indexing_stats(stats)
        return stats.to_dict()

    def _display_indexing_stats(self, stats) -> None:
        """Display indexing statistics."""
        try:
            from IPython.display import display, HTML
            
            html = f"""
            <div style="padding: 10px; border: 1px solid #4caf50; border-radius: 5px; 
                        background: #e8f5e9;">
                <h4 style="margin: 0 0 10px 0; color: #2e7d32;">📁 Indexing Complete</h4>
                <table>
                    <tr><td>Files Processed:</td><td><strong>{stats.files_processed}</strong></td></tr>
                    <tr><td>Files Skipped:</td><td>{stats.files_skipped}</td></tr>
                    <tr><td>Chunks Created:</td><td><strong>{stats.chunks_indexed}</strong></td></tr>
                    <tr><td>Duration:</td><td>{stats.duration_seconds:.2f}s</td></tr>
                </table>
                {f'<p style="color: #d32f2f;">Errors: {len(stats.errors)}</p>' if stats.errors else ''}
            </div>
            """
            display(HTML(html))
        except ImportError:
            print(f"Indexed {stats.files_processed} files, {stats.chunks_indexed} chunks")

    def chat(
        self,
        message: str,
        context_collection: Optional[str] = None,
        model: Optional[str] = None,
        display_response: bool = True,
        **kwargs,
    ) -> str:
        """
        Chat with the LLM.
        
        Args:
            message: User message
            context_collection: Collection for RAG context
            model: Model to use
            display_response: Display response in notebook
            **kwargs: Additional chat parameters
        
        Returns:
            Response text
        """
        response = self.engine.chat(
            message=message,
            model=model,
            context_collection=context_collection,
            **kwargs,
        )
        
        if display_response:
            self._display_chat_response(message, response)
        
        return response

    def _display_chat_response(self, message: str, response: str) -> None:
        """Display chat response."""
        try:
            from IPython.display import display, Markdown
            display(Markdown(response))
        except ImportError:
            print(response)

    def save(self, name: str, data: Any, **metadata) -> str:
        """
        Save data to the session.
        
        Args:
            name: Context name
            data: Data to save
            **metadata: Additional metadata
        
        Returns:
            Context entry ID
        """
        return self.engine.save_context(name, data, metadata or None)

    def load(self, name: str) -> Optional[Any]:
        """
        Load data from the session.
        
        Args:
            name: Context name
        
        Returns:
            Saved data or None
        """
        return self.engine.get_context(name)

    def list_saved(self) -> list[dict]:
        """List all saved contexts."""
        return self.engine.list_contexts()

    def status(self) -> dict:
        """Get workspace status."""
        status = self.engine.get_status()
        if self._display_status:
            self._show_status()
        return status

    def history(self, limit: int = 10) -> list[dict]:
        """
        Get chat history.
        
        Args:
            limit: Maximum entries to return
        
        Returns:
            List of chat history entries
        """
        return self.engine.session.get_chat_history(limit=limit)

    # === Resource Management ===

    def start_server(self, background: bool = True) -> Optional[str]:
        """Start the MCP/REST server."""
        return self.engine.start_server(background=background)

    def stop_server(self) -> None:
        """Stop the server."""
        self.engine.stop_server()

    def list_models(self) -> list:
        """List available Ollama models."""
        return self.engine.list_models()

    def pull_model(self, model: str) -> bool:
        """Pull an Ollama model."""
        return self.engine.pull_model(model)

    # === Context Manager ===

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        return False

    def close(self) -> None:
        """Close the workspace."""
        self.engine.close()
        JupyterWorkspace._instances.pop(self.session_name, None)
        logger.info(f"Workspace closed: {self.session_name}")

    # === IPython Integration ===

    def _repr_html_(self) -> str:
        """HTML representation for Jupyter."""
        status = self.engine.get_status()
        return f"""
        <div style="padding: 10px; border: 1px solid #ddd; border-radius: 5px;">
            <strong>JupyterWorkspace</strong>: {self.session_name}<br>
            <small>
                Ollama: {'✅' if status['ollama']['running'] else '❌'} |
                Collections: {len(status['vector_store']['collections'])} |
                Server: {'✅' if status['server']['running'] else '❌'}
            </small>
        </div>
        """

    def __repr__(self) -> str:
        return f"JupyterWorkspace(session={self.session_name!r})"


# Convenience function for quick setup
def workspace(
    session_name: str = "notebook",
    **kwargs,
) -> JupyterWorkspace:
    """
    Quick setup for a Jupyter workspace.
    
    Args:
        session_name: Session name
        **kwargs: Additional arguments
    
    Returns:
        JupyterWorkspace instance
    
    Example:
        >>> from agentic_assistants import workspace
        >>> ws = workspace("my-project")
        >>> ws.index("./src")
        >>> results = ws.search("authentication")
    """
    return JupyterWorkspace.get_or_create(session_name, **kwargs)

