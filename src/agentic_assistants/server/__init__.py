"""
Server module for Agentic Assistants.

This module provides:
- MCPServer: Model Context Protocol server for Claude/Continue
- RESTServer: FastAPI REST API for search and indexing
- Combined server application

Example:
    >>> from agentic_assistants.server import create_app, start_server
    >>> 
    >>> # Start combined server
    >>> start_server(host="127.0.0.1", port=8080)
"""

from agentic_assistants.server.rest import create_rest_app
from agentic_assistants.server.app import create_app, start_server

__all__ = [
    "create_rest_app",
    "create_app",
    "start_server",
]

