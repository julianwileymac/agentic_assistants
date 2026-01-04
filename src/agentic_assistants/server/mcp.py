"""
Model Context Protocol (MCP) server implementation.

This module implements Anthropic's Model Context Protocol for
integration with Claude and the Continue framework.

Example:
    >>> from agentic_assistants.server.mcp import MCPServer
    >>> 
    >>> server = MCPServer()
    >>> server.run()
"""

import json
from typing import Any, Optional

from agentic_assistants.config import AgenticConfig
from agentic_assistants.indexing.codebase import CodebaseIndexer
from agentic_assistants.utils.logging import get_logger
from agentic_assistants.vectordb.base import VectorStore

logger = get_logger(__name__)


class MCPServer:
    """
    Model Context Protocol server.
    
    This server implements the MCP protocol for providing
    codebase context to AI assistants like Claude.
    
    The protocol uses JSON-RPC over stdio or HTTP.
    
    Attributes:
        vector_store: Vector store for searching
        config: Configuration instance
    """

    # MCP Protocol version
    PROTOCOL_VERSION = "2024-11-05"
    
    # Server capabilities
    CAPABILITIES = {
        "tools": {},  # Tool definitions
        "resources": {},  # Resource providers
        "prompts": {},  # Prompt templates
    }

    def __init__(
        self,
        config: Optional[AgenticConfig] = None,
        vector_store: Optional[VectorStore] = None,
    ):
        """
        Initialize the MCP server.
        
        Args:
            config: Configuration instance
            vector_store: Vector store instance
        """
        self.config = config or AgenticConfig()
        self._vector_store = vector_store
        self._indexer: Optional[CodebaseIndexer] = None
        
        # Register tools
        self._tools = {
            "search_codebase": self._tool_search_codebase,
            "get_file_context": self._tool_get_file_context,
            "list_collections": self._tool_list_collections,
            "index_directory": self._tool_index_directory,
        }

    @property
    def vector_store(self) -> VectorStore:
        """Get or create vector store."""
        if self._vector_store is None:
            self._vector_store = VectorStore.create(config=self.config)
        return self._vector_store

    @property
    def indexer(self) -> CodebaseIndexer:
        """Get or create indexer."""
        if self._indexer is None:
            self._indexer = CodebaseIndexer(
                vector_store=self.vector_store,
                config=self.config,
            )
        return self._indexer

    # === MCP Protocol Methods ===

    def handle_request(self, request: dict) -> dict:
        """
        Handle an MCP request.
        
        Args:
            request: JSON-RPC request dictionary
        
        Returns:
            JSON-RPC response dictionary
        """
        method = request.get("method", "")
        params = request.get("params", {})
        request_id = request.get("id")
        
        try:
            if method == "initialize":
                result = self._handle_initialize(params)
            elif method == "tools/list":
                result = self._handle_tools_list()
            elif method == "tools/call":
                result = self._handle_tools_call(params)
            elif method == "resources/list":
                result = self._handle_resources_list()
            elif method == "resources/read":
                result = self._handle_resources_read(params)
            elif method == "prompts/list":
                result = self._handle_prompts_list()
            elif method == "prompts/get":
                result = self._handle_prompts_get(params)
            else:
                return self._error_response(
                    request_id,
                    -32601,
                    f"Method not found: {method}",
                )
            
            return self._success_response(request_id, result)
            
        except Exception as e:
            logger.error(f"Error handling MCP request: {e}")
            return self._error_response(request_id, -32603, str(e))

    def _success_response(self, request_id: Any, result: Any) -> dict:
        """Create a success response."""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result,
        }

    def _error_response(self, request_id: Any, code: int, message: str) -> dict:
        """Create an error response."""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": code,
                "message": message,
            },
        }

    # === Protocol Handlers ===

    def _handle_initialize(self, params: dict) -> dict:
        """Handle initialize request."""
        return {
            "protocolVersion": self.PROTOCOL_VERSION,
            "capabilities": self.CAPABILITIES,
            "serverInfo": {
                "name": "agentic-assistants",
                "version": "0.1.0",
            },
        }

    def _handle_tools_list(self) -> dict:
        """Handle tools/list request."""
        tools = [
            {
                "name": "search_codebase",
                "description": "Search the indexed codebase for relevant code snippets",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query",
                        },
                        "collection": {
                            "type": "string",
                            "description": "Collection to search (default: 'default')",
                            "default": "default",
                        },
                        "top_k": {
                            "type": "integer",
                            "description": "Number of results (default: 5)",
                            "default": 5,
                        },
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "get_file_context",
                "description": "Get the full content of a file from the codebase",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the file",
                        },
                    },
                    "required": ["file_path"],
                },
            },
            {
                "name": "list_collections",
                "description": "List all indexed collections",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                },
            },
            {
                "name": "index_directory",
                "description": "Index a directory into the vector database",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Directory path to index",
                        },
                        "collection": {
                            "type": "string",
                            "description": "Collection name",
                            "default": "default",
                        },
                    },
                    "required": ["path"],
                },
            },
        ]
        
        return {"tools": tools}

    def _handle_tools_call(self, params: dict) -> dict:
        """Handle tools/call request."""
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})
        
        if tool_name not in self._tools:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        result = self._tools[tool_name](arguments)
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(result, indent=2),
                }
            ],
        }

    def _handle_resources_list(self) -> dict:
        """Handle resources/list request."""
        # List indexed files as resources
        collections = self.vector_store.list_collections()
        resources = []
        
        for collection in collections:
            files = self.indexer.get_indexed_files(collection)
            for file_info in files:
                resources.append({
                    "uri": f"file://{file_info['path']}",
                    "name": file_info["path"].split("/")[-1],
                    "mimeType": self._get_mime_type(file_info.get("language", "")),
                    "description": f"Indexed file in collection '{collection}'",
                })
        
        return {"resources": resources}

    def _handle_resources_read(self, params: dict) -> dict:
        """Handle resources/read request."""
        uri = params.get("uri", "")
        
        # Parse file:// URI
        if uri.startswith("file://"):
            file_path = uri[7:]
        else:
            file_path = uri
        
        try:
            from pathlib import Path
            path = Path(file_path)
            if path.exists():
                content = path.read_text(encoding="utf-8")
                return {
                    "contents": [
                        {
                            "uri": uri,
                            "mimeType": self._get_mime_type_from_path(file_path),
                            "text": content,
                        }
                    ],
                }
            else:
                raise ValueError(f"File not found: {file_path}")
        except Exception as e:
            raise ValueError(f"Failed to read resource: {e}")

    def _handle_prompts_list(self) -> dict:
        """Handle prompts/list request."""
        prompts = [
            {
                "name": "code_review",
                "description": "Review code changes",
                "arguments": [
                    {
                        "name": "file_path",
                        "description": "Path to the file to review",
                        "required": True,
                    },
                ],
            },
            {
                "name": "explain_code",
                "description": "Explain how code works",
                "arguments": [
                    {
                        "name": "query",
                        "description": "What to explain",
                        "required": True,
                    },
                ],
            },
        ]
        
        return {"prompts": prompts}

    def _handle_prompts_get(self, params: dict) -> dict:
        """Handle prompts/get request."""
        name = params.get("name", "")
        arguments = params.get("arguments", {})
        
        if name == "code_review":
            file_path = arguments.get("file_path", "")
            return {
                "messages": [
                    {
                        "role": "user",
                        "content": {
                            "type": "text",
                            "text": f"Please review the code in {file_path} and provide feedback on:\n"
                                   f"1. Code quality and best practices\n"
                                   f"2. Potential bugs or issues\n"
                                   f"3. Suggestions for improvement",
                        },
                    },
                ],
            }
        elif name == "explain_code":
            query = arguments.get("query", "")
            return {
                "messages": [
                    {
                        "role": "user",
                        "content": {
                            "type": "text",
                            "text": f"Please explain: {query}\n\n"
                                   f"Include:\n"
                                   f"1. How it works\n"
                                   f"2. Key concepts involved\n"
                                   f"3. Example usage",
                        },
                    },
                ],
            }
        else:
            raise ValueError(f"Unknown prompt: {name}")

    # === Tool Implementations ===

    def _tool_search_codebase(self, arguments: dict) -> dict:
        """Search the codebase."""
        query = arguments.get("query", "")
        collection = arguments.get("collection", "default")
        top_k = arguments.get("top_k", 5)
        
        results = self.vector_store.search(
            query=query,
            collection=collection,
            top_k=top_k,
        )
        
        return {
            "query": query,
            "results": [
                {
                    "file_path": r.document.metadata.get("file_path", ""),
                    "content": r.document.content,
                    "score": r.score,
                    "language": r.document.metadata.get("language", ""),
                }
                for r in results
            ],
        }

    def _tool_get_file_context(self, arguments: dict) -> dict:
        """Get file content."""
        from pathlib import Path
        
        file_path = arguments.get("file_path", "")
        path = Path(file_path)
        
        if not path.exists():
            return {"error": f"File not found: {file_path}"}
        
        try:
            content = path.read_text(encoding="utf-8")
            return {
                "file_path": file_path,
                "content": content,
                "size_bytes": path.stat().st_size,
            }
        except Exception as e:
            return {"error": str(e)}

    def _tool_list_collections(self, arguments: dict) -> dict:
        """List collections."""
        collections = self.vector_store.list_collections()
        return {
            "collections": [
                {
                    "name": name,
                    "document_count": self.vector_store.count(name),
                }
                for name in collections
            ],
        }

    def _tool_index_directory(self, arguments: dict) -> dict:
        """Index a directory."""
        path = arguments.get("path", "")
        collection = arguments.get("collection", "default")
        
        stats = self.indexer.index_directory(
            directory=path,
            collection=collection,
        )
        
        return {
            "status": "completed",
            "files_processed": stats.files_processed,
            "chunks_indexed": stats.chunks_indexed,
            "errors": stats.errors,
        }

    # === Utility Methods ===

    def _get_mime_type(self, language: str) -> str:
        """Get MIME type for a language."""
        mime_types = {
            "python": "text/x-python",
            "javascript": "text/javascript",
            "typescript": "text/typescript",
            "java": "text/x-java",
            "go": "text/x-go",
            "rust": "text/x-rust",
            "c": "text/x-c",
            "cpp": "text/x-c++",
            "markdown": "text/markdown",
            "json": "application/json",
            "yaml": "text/yaml",
        }
        return mime_types.get(language, "text/plain")

    def _get_mime_type_from_path(self, path: str) -> str:
        """Get MIME type from file path."""
        ext_map = {
            ".py": "text/x-python",
            ".js": "text/javascript",
            ".ts": "text/typescript",
            ".java": "text/x-java",
            ".go": "text/x-go",
            ".rs": "text/x-rust",
            ".c": "text/x-c",
            ".cpp": "text/x-c++",
            ".md": "text/markdown",
            ".json": "application/json",
            ".yaml": "text/yaml",
            ".yml": "text/yaml",
        }
        
        from pathlib import Path
        ext = Path(path).suffix.lower()
        return ext_map.get(ext, "text/plain")

    # === Server Methods ===

    def run_stdio(self) -> None:
        """
        Run the MCP server over stdio.
        
        This is the standard way to run MCP servers.
        """
        import sys
        
        logger.info("Starting MCP server on stdio")
        
        while True:
            try:
                # Read request from stdin
                line = sys.stdin.readline()
                if not line:
                    break
                
                request = json.loads(line)
                response = self.handle_request(request)
                
                # Write response to stdout
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()
                
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON: {e}")
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"Error: {e}")

    async def handle_websocket(self, websocket) -> None:
        """
        Handle MCP over WebSocket.
        
        Args:
            websocket: WebSocket connection
        """
        async for message in websocket:
            try:
                request = json.loads(message)
                response = self.handle_request(request)
                await websocket.send(json.dumps(response))
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                error = self._error_response(None, -32603, str(e))
                await websocket.send(json.dumps(error))

