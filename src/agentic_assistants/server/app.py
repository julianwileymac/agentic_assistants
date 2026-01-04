"""
Combined server application for MCP and REST.

This module provides a unified server that can run both
MCP (Model Context Protocol) and REST APIs with full
OpenTelemetry instrumentation.

Example:
    >>> from agentic_assistants.server import start_server
    >>> 
    >>> start_server(host="127.0.0.1", port=8080)
"""

import asyncio
import time
from typing import Optional

from agentic_assistants.config import AgenticConfig
from agentic_assistants.server.mcp import MCPServer
from agentic_assistants.server.rest import create_rest_app
from agentic_assistants.core.telemetry import TelemetryManager, trace_async_function
from agentic_assistants.utils.logging import get_logger
from agentic_assistants.vectordb.base import VectorStore

logger = get_logger(__name__)


class OTELMiddleware:
    """
    OpenTelemetry middleware for FastAPI.
    
    Provides automatic tracing for all HTTP requests with:
    - Request/response timing
    - Status code tracking
    - Error capture
    - Request attributes (method, path, etc.)
    """
    
    def __init__(self, app, telemetry: TelemetryManager):
        self.app = app
        self.telemetry = telemetry
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Extract request info
        method = scope.get("method", "UNKNOWN")
        path = scope.get("path", "/")
        
        # Track response status
        status_code = 500
        start_time = time.time()
        
        async def send_wrapper(message):
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message.get("status", 500)
            await send(message)
        
        # Create span for the request
        span_name = f"HTTP {method} {path}"
        attributes = {
            "http.method": method,
            "http.route": path,
            "http.scheme": scope.get("scheme", "http"),
            "http.host": dict(scope.get("headers", [])).get(b"host", b"").decode(),
            "http.user_agent": dict(scope.get("headers", [])).get(b"user-agent", b"").decode()[:200],
        }
        
        error_msg = None
        with self.telemetry.span(span_name, attributes=attributes) as span_logger:
            try:
                await self.app(scope, receive, send_wrapper)
                span_logger.span.set_attribute("http.status_code", status_code)
                
                if status_code >= 400:
                    span_logger.span.set_attribute("error", True)
                    span_logger.log_event("http_error", {"status_code": status_code})
                
            except Exception as e:
                error_msg = str(e)
                span_logger.log_error(e)
                raise
            finally:
                duration = time.time() - start_time
                span_logger.span.set_attribute("http.duration_seconds", duration)
                
                # Record metrics
                self.telemetry.record_http_request(
                    method=method,
                    path=path,
                    status_code=status_code,
                    duration_seconds=duration,
                    error=error_msg,
                )


def create_app(
    config: Optional[AgenticConfig] = None,
    enable_mcp: bool = True,
    enable_rest: bool = True,
    enable_telemetry: bool = True,
):
    """
    Create a combined FastAPI application.
    
    Args:
        config: Configuration instance
        enable_mcp: Enable MCP endpoints
        enable_rest: Enable REST endpoints
        enable_telemetry: Enable OTEL middleware
    
    Returns:
        FastAPI application
    """
    from fastapi import FastAPI, WebSocket, WebSocketDisconnect
    from fastapi.middleware.cors import CORSMiddleware
    
    config = config or AgenticConfig()
    
    # Create base app
    app = create_rest_app(config=config)
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Initialize telemetry
    telemetry = None
    if enable_telemetry and config.telemetry_enabled:
        telemetry = TelemetryManager(config, verbose=config.log_level == "DEBUG")
        telemetry.initialize()
        
        # Add OTEL middleware
        app = OTELMiddleware(app, telemetry)
        logger.info("OpenTelemetry middleware enabled")
    
    # Store telemetry in app state for access in routes
    if hasattr(app, 'state'):
        app.state.telemetry = telemetry
    
    # Add MCP WebSocket endpoint if enabled
    if enable_mcp:
        mcp_server = MCPServer(config=config)
        
        # We need to wrap the ASGI app to add WebSocket routes
        # Since we've wrapped with middleware, we need to handle this differently
        original_app = app.app if isinstance(app, OTELMiddleware) else app
        
        @original_app.websocket("/mcp")
        async def mcp_websocket(websocket: WebSocket):
            """MCP WebSocket endpoint."""
            await websocket.accept()
            logger.info("MCP WebSocket connection established")
            
            if telemetry:
                with telemetry.span("mcp.websocket.session", attributes={"type": "websocket"}) as span_logger:
                    try:
                        await mcp_server.handle_websocket(websocket)
                    except WebSocketDisconnect:
                        span_logger.log_event("disconnected")
                        logger.info("MCP WebSocket disconnected")
                    except Exception as e:
                        span_logger.log_error(e)
                        logger.error(f"MCP WebSocket error: {e}")
            else:
                try:
                    await mcp_server.handle_websocket(websocket)
                except WebSocketDisconnect:
                    logger.info("MCP WebSocket disconnected")
                except Exception as e:
                    logger.error(f"MCP WebSocket error: {e}")
        
        @original_app.post("/mcp")
        @trace_async_function(span_name="mcp.http.request", record_args=True)
        async def mcp_http(request: dict):
            """MCP HTTP endpoint (for debugging/testing)."""
            return mcp_server.handle_request(request)
    
    return app


def start_server(
    host: Optional[str] = None,
    port: Optional[int] = None,
    config: Optional[AgenticConfig] = None,
    reload: bool = False,
) -> None:
    """
    Start the combined server.
    
    Args:
        host: Server host (default from config)
        port: Server port (default from config)
        config: Configuration instance
        reload: Enable auto-reload for development
    """
    import uvicorn
    
    config = config or AgenticConfig()
    host = host or config.server.host
    port = port or config.server.port
    
    logger.info(f"Starting Agentic Assistants server on {host}:{port}")
    
    app = create_app(
        config=config,
        enable_mcp=config.server.enable_mcp,
        enable_rest=config.server.enable_rest,
        enable_telemetry=config.telemetry_enabled,
    )
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=reload,
        log_level="info",
    )


async def start_server_async(
    host: Optional[str] = None,
    port: Optional[int] = None,
    config: Optional[AgenticConfig] = None,
) -> None:
    """
    Start the server asynchronously.
    
    Args:
        host: Server host
        port: Server port
        config: Configuration instance
    """
    import uvicorn
    
    config = config or AgenticConfig()
    host = host or config.server.host
    port = port or config.server.port
    
    app = create_app(
        config=config,
        enable_mcp=config.server.enable_mcp,
        enable_rest=config.server.enable_rest,
        enable_telemetry=config.telemetry_enabled,
    )
    
    server_config = uvicorn.Config(
        app,
        host=host,
        port=port,
        log_level="info",
    )
    server = uvicorn.Server(server_config)
    
    await server.serve()


class ServerManager:
    """
    Manager for running the server in the background.
    
    This is useful for running the server alongside
    other components (e.g., in a notebook).
    """

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        config: Optional[AgenticConfig] = None,
    ):
        """
        Initialize the server manager.
        
        Args:
            host: Server host
            port: Server port
            config: Configuration instance
        """
        self.config = config or AgenticConfig()
        self.host = host or self.config.server.host
        self.port = port or self.config.server.port
        self._server_task: Optional[asyncio.Task] = None
        self._server = None
        self._telemetry: Optional[TelemetryManager] = None

    async def start(self) -> None:
        """Start the server in the background."""
        import uvicorn
        
        if self._server_task is not None:
            logger.warning("Server is already running")
            return
        
        app = create_app(
            config=self.config,
            enable_mcp=self.config.server.enable_mcp,
            enable_rest=self.config.server.enable_rest,
            enable_telemetry=self.config.telemetry_enabled,
        )
        
        server_config = uvicorn.Config(
            app,
            host=self.host,
            port=self.port,
            log_level="warning",
        )
        self._server = uvicorn.Server(server_config)
        
        self._server_task = asyncio.create_task(self._server.serve())
        logger.info(f"Server started on {self.host}:{self.port}")

    async def stop(self) -> None:
        """Stop the server."""
        if self._server is not None:
            self._server.should_exit = True
            if self._server_task is not None:
                await self._server_task
                self._server_task = None
            self._server = None
            
            # Shutdown telemetry
            if self._telemetry:
                self._telemetry.shutdown()
            
            logger.info("Server stopped")

    @property
    def is_running(self) -> bool:
        """Check if server is running."""
        return self._server_task is not None and not self._server_task.done()

    @property
    def url(self) -> str:
        """Get the server URL."""
        return f"http://{self.host}:{self.port}"

    def __enter__(self):
        """Context manager entry."""
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.start())
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.stop())
        return False
