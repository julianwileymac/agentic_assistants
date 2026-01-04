"""
WebSocket handler for real-time events and log streaming.

This module provides WebSocket support for:
- Real-time event broadcasting (experiments, artifacts, sessions)
- Log streaming from script execution
- Status updates and notifications
"""

import asyncio
import json
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Optional
from uuid import uuid4

from fastapi import WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field

from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


# === Event Types ===


class EventType(str, Enum):
    """Types of WebSocket events."""
    
    # Connection events
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    PING = "ping"
    PONG = "pong"
    
    # Experiment events
    EXPERIMENT_CREATED = "experiment.created"
    EXPERIMENT_UPDATED = "experiment.updated"
    EXPERIMENT_DELETED = "experiment.deleted"
    RUN_STARTED = "run.started"
    RUN_ENDED = "run.ended"
    RUN_LOG = "run.log"
    METRICS_LOGGED = "metrics.logged"
    
    # Artifact events
    ARTIFACT_CREATED = "artifact.created"
    ARTIFACT_UPDATED = "artifact.updated"
    ARTIFACT_DELETED = "artifact.deleted"
    ARTIFACT_SHARED = "artifact.shared"
    
    # Session events
    SESSION_CREATED = "session.created"
    SESSION_ACTIVATED = "session.activated"
    SESSION_DELETED = "session.deleted"
    INTERACTION_LOGGED = "interaction.logged"
    
    # Data events
    FILE_CREATED = "file.created"
    FILE_UPDATED = "file.updated"
    FILE_DELETED = "file.deleted"
    
    # System events
    CONFIG_CHANGED = "config.changed"
    ERROR = "error"
    NOTIFICATION = "notification"


class WSMessage(BaseModel):
    """WebSocket message format."""
    
    id: str = Field(default_factory=lambda: str(uuid4()))
    type: EventType = Field(..., description="Event type")
    timestamp: datetime = Field(default_factory=datetime.now)
    data: dict[str, Any] = Field(default_factory=dict)
    source: str = Field(default="server")
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps({
            "id": self.id,
            "type": self.type.value,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data,
            "source": self.source,
        })


class WSCommand(BaseModel):
    """WebSocket command from client."""
    
    id: Optional[str] = None
    command: str = Field(..., description="Command name")
    params: dict[str, Any] = Field(default_factory=dict)


# === Connection Manager ===


class ConnectionManager:
    """
    Manages WebSocket connections and message broadcasting.
    
    Supports:
    - Multiple simultaneous connections
    - Topic-based subscriptions
    - Broadcast and targeted messaging
    - Server-side ping/pong keepalive
    """
    
    def __init__(
        self,
        ping_interval: int = 30,
        ping_timeout: int = 10,
        max_connections: int = 100,
    ):
        self.active_connections: dict[str, WebSocket] = {}
        self.subscriptions: dict[str, set[str]] = {}  # topic -> connection_ids
        self._lock = asyncio.Lock()
        self._event_handlers: dict[str, list[Callable]] = {}
        
        # Keepalive configuration
        self.ping_interval = ping_interval
        self.ping_timeout = ping_timeout
        self.max_connections = max_connections
        
        # Connection health tracking
        self._last_activity: dict[str, datetime] = {}
        self._pending_pings: dict[str, datetime] = {}
        self._ping_task: Optional[asyncio.Task] = None
        self._running = False
    
    async def start(self):
        """Start the connection manager and ping task."""
        if self._running:
            return
        self._running = True
        self._ping_task = asyncio.create_task(self._ping_loop())
        logger.info("ConnectionManager started with ping interval=%ds, timeout=%ds", 
                   self.ping_interval, self.ping_timeout)
    
    async def stop(self):
        """Stop the connection manager and ping task."""
        self._running = False
        if self._ping_task:
            self._ping_task.cancel()
            try:
                await self._ping_task
            except asyncio.CancelledError:
                pass
            self._ping_task = None
        logger.info("ConnectionManager stopped")
    
    async def _ping_loop(self):
        """Background task to send pings and check for stale connections."""
        while self._running:
            try:
                await asyncio.sleep(self.ping_interval)
                await self._send_pings()
                await self._check_stale_connections()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in ping loop: {e}")
    
    async def _send_pings(self):
        """Send ping to all active connections."""
        now = datetime.now()
        for connection_id in list(self.active_connections.keys()):
            try:
                # Only send ping if no pending ping
                if connection_id not in self._pending_pings:
                    await self.send_to(connection_id, WSMessage(
                        type=EventType.PING,
                        data={"timestamp": now.isoformat()},
                    ))
                    self._pending_pings[connection_id] = now
                    logger.debug(f"Sent ping to {connection_id}")
            except Exception as e:
                logger.error(f"Failed to send ping to {connection_id}: {e}")
    
    async def _check_stale_connections(self):
        """Check for connections that haven't responded to pings."""
        now = datetime.now()
        stale_connections = []
        
        for connection_id, ping_time in list(self._pending_pings.items()):
            if (now - ping_time).total_seconds() > self.ping_timeout:
                logger.warning(f"Connection {connection_id} timed out (no pong received)")
                stale_connections.append(connection_id)
        
        for connection_id in stale_connections:
            await self.disconnect(connection_id)
    
    def handle_pong(self, connection_id: str):
        """Handle pong response from client."""
        if connection_id in self._pending_pings:
            del self._pending_pings[connection_id]
        self._last_activity[connection_id] = datetime.now()
        logger.debug(f"Received pong from {connection_id}")
    
    def update_activity(self, connection_id: str):
        """Update last activity time for a connection."""
        self._last_activity[connection_id] = datetime.now()
    
    async def connect(self, websocket: WebSocket, client_id: Optional[str] = None) -> str:
        """Accept a new WebSocket connection."""
        # Check max connections
        if len(self.active_connections) >= self.max_connections:
            logger.warning("Max connections reached, rejecting new connection")
            await websocket.close(code=1013, reason="Max connections reached")
            raise ConnectionError("Max connections reached")
        
        await websocket.accept()
        
        connection_id = client_id or str(uuid4())
        
        async with self._lock:
            self.active_connections[connection_id] = websocket
            self._last_activity[connection_id] = datetime.now()
        
        logger.info(f"WebSocket connected: {connection_id}")
        
        # Send connection confirmation
        await self.send_to(connection_id, WSMessage(
            type=EventType.CONNECTED,
            data={"connection_id": connection_id},
        ))
        
        return connection_id
    
    async def disconnect(self, connection_id: str):
        """Handle WebSocket disconnection."""
        async with self._lock:
            if connection_id in self.active_connections:
                del self.active_connections[connection_id]
            
            # Clean up tracking data
            self._last_activity.pop(connection_id, None)
            self._pending_pings.pop(connection_id, None)
            
            # Remove from all subscriptions
            for topic in list(self.subscriptions.keys()):
                self.subscriptions[topic].discard(connection_id)
                if not self.subscriptions[topic]:
                    del self.subscriptions[topic]
        
        logger.info(f"WebSocket disconnected: {connection_id}")
    
    async def subscribe(self, connection_id: str, topic: str):
        """Subscribe a connection to a topic."""
        async with self._lock:
            if topic not in self.subscriptions:
                self.subscriptions[topic] = set()
            self.subscriptions[topic].add(connection_id)
        
        logger.debug(f"Connection {connection_id} subscribed to {topic}")
    
    async def unsubscribe(self, connection_id: str, topic: str):
        """Unsubscribe a connection from a topic."""
        async with self._lock:
            if topic in self.subscriptions:
                self.subscriptions[topic].discard(connection_id)
                if not self.subscriptions[topic]:
                    del self.subscriptions[topic]
        
        logger.debug(f"Connection {connection_id} unsubscribed from {topic}")
    
    async def send_to(self, connection_id: str, message: WSMessage):
        """Send a message to a specific connection."""
        if connection_id in self.active_connections:
            try:
                await self.active_connections[connection_id].send_text(message.to_json())
            except Exception as e:
                logger.error(f"Failed to send message to {connection_id}: {e}")
                await self.disconnect(connection_id)
    
    async def broadcast(self, message: WSMessage, exclude: Optional[set[str]] = None):
        """Broadcast a message to all connections."""
        exclude = exclude or set()
        
        disconnected = []
        for connection_id, websocket in list(self.active_connections.items()):
            if connection_id in exclude:
                continue
            try:
                await websocket.send_text(message.to_json())
            except Exception as e:
                logger.error(f"Failed to broadcast to {connection_id}: {e}")
                disconnected.append(connection_id)
        
        # Clean up disconnected
        for connection_id in disconnected:
            await self.disconnect(connection_id)
    
    async def broadcast_to_topic(self, topic: str, message: WSMessage):
        """Broadcast a message to all connections subscribed to a topic."""
        if topic not in self.subscriptions:
            return
        
        for connection_id in list(self.subscriptions[topic]):
            await self.send_to(connection_id, message)
    
    def register_handler(self, command: str, handler: Callable):
        """Register a command handler."""
        if command not in self._event_handlers:
            self._event_handlers[command] = []
        self._event_handlers[command].append(handler)
    
    async def handle_command(self, connection_id: str, command: WSCommand) -> Optional[WSMessage]:
        """Handle a command from a client."""
        handlers = self._event_handlers.get(command.command, [])
        
        for handler in handlers:
            try:
                result = handler(connection_id, command.params)
                if asyncio.iscoroutine(result):
                    result = await result
                
                if result is not None:
                    return WSMessage(
                        id=command.id,
                        type=EventType.NOTIFICATION,
                        data={"result": result},
                    )
            except Exception as e:
                logger.error(f"Command handler error: {e}")
                return WSMessage(
                    id=command.id,
                    type=EventType.ERROR,
                    data={"error": str(e)},
                )
        
        return None
    
    @property
    def connection_count(self) -> int:
        """Get number of active connections."""
        return len(self.active_connections)
    
    def get_connection_info(self) -> dict[str, Any]:
        """Get information about active connections."""
        return {
            "active_connections": len(self.active_connections),
            "connection_ids": list(self.active_connections.keys()),
            "subscriptions": {
                topic: list(connections)
                for topic, connections in self.subscriptions.items()
            },
        }


# Global connection manager (initialized with defaults, can be reconfigured)
manager = ConnectionManager()


def configure_manager(
    ping_interval: int = 30,
    ping_timeout: int = 10,
    max_connections: int = 100,
) -> None:
    """
    Configure the global connection manager with custom settings.
    
    Should be called before starting the server.
    
    Args:
        ping_interval: Seconds between ping messages
        ping_timeout: Seconds to wait for pong response
        max_connections: Maximum concurrent connections
    """
    global manager, emitter
    manager = ConnectionManager(
        ping_interval=ping_interval,
        ping_timeout=ping_timeout,
        max_connections=max_connections,
    )
    emitter = EventEmitter(manager)
    logger.info(
        f"ConnectionManager configured: ping_interval={ping_interval}s, "
        f"ping_timeout={ping_timeout}s, max_connections={max_connections}"
    )


# === Event Emitter ===


class EventEmitter:
    """
    Emits events to WebSocket connections.
    
    Use this to broadcast events from other parts of the application.
    """
    
    def __init__(self, connection_manager: ConnectionManager):
        self.manager = connection_manager
    
    async def emit(self, event_type: EventType, data: dict[str, Any], topic: Optional[str] = None):
        """Emit an event."""
        message = WSMessage(type=event_type, data=data)
        
        if topic:
            await self.manager.broadcast_to_topic(topic, message)
        else:
            await self.manager.broadcast(message)
    
    async def emit_experiment_created(self, experiment_id: str, name: str):
        """Emit experiment created event."""
        await self.emit(
            EventType.EXPERIMENT_CREATED,
            {"experiment_id": experiment_id, "name": name},
            topic="experiments",
        )
    
    async def emit_run_started(self, run_id: str, experiment_id: str, run_name: Optional[str] = None):
        """Emit run started event."""
        await self.emit(
            EventType.RUN_STARTED,
            {"run_id": run_id, "experiment_id": experiment_id, "run_name": run_name},
            topic="experiments",
        )
    
    async def emit_run_log(self, run_id: str, message: str, level: str = "INFO"):
        """Emit run log event (for streaming output)."""
        await self.emit(
            EventType.RUN_LOG,
            {"run_id": run_id, "message": message, "level": level},
            topic=f"run.{run_id}",
        )
    
    async def emit_run_ended(self, run_id: str, status: str):
        """Emit run ended event."""
        await self.emit(
            EventType.RUN_ENDED,
            {"run_id": run_id, "status": status},
            topic="experiments",
        )
    
    async def emit_artifact_created(self, artifact_id: str, name: str, tags: list[str] = None):
        """Emit artifact created event."""
        await self.emit(
            EventType.ARTIFACT_CREATED,
            {"artifact_id": artifact_id, "name": name, "tags": tags or []},
            topic="artifacts",
        )
    
    async def emit_session_activated(self, session_id: str, name: str):
        """Emit session activated event."""
        await self.emit(
            EventType.SESSION_ACTIVATED,
            {"session_id": session_id, "name": name},
            topic="sessions",
        )
    
    async def emit_config_changed(self, section: str, changes: dict[str, Any]):
        """Emit configuration changed event."""
        await self.emit(
            EventType.CONFIG_CHANGED,
            {"section": section, "changes": changes},
        )
    
    async def emit_notification(self, title: str, message: str, level: str = "info"):
        """Emit a notification to all clients."""
        await self.emit(
            EventType.NOTIFICATION,
            {"title": title, "message": message, "level": level},
        )
    
    async def emit_error(self, error: str, details: Optional[dict] = None):
        """Emit an error event."""
        await self.emit(
            EventType.ERROR,
            {"error": error, "details": details or {}},
        )


# Global event emitter
emitter = EventEmitter(manager)


# === Log Streamer ===


class LogStreamer:
    """
    Streams logs to WebSocket connections.
    
    Use this to stream script execution output in real-time.
    """
    
    def __init__(self, run_id: str, emitter: EventEmitter):
        self.run_id = run_id
        self.emitter = emitter
        self._buffer: list[str] = []
        self._flush_task: Optional[asyncio.Task] = None
    
    async def write(self, message: str, level: str = "INFO"):
        """Write a log message."""
        self._buffer.append(message)
        
        # Emit immediately for important messages
        if level in ("ERROR", "WARNING"):
            await self._flush()
        elif len(self._buffer) >= 10:
            await self._flush()
        elif self._flush_task is None or self._flush_task.done():
            self._flush_task = asyncio.create_task(self._delayed_flush())
    
    async def _delayed_flush(self):
        """Flush buffer after a short delay."""
        await asyncio.sleep(0.1)  # 100ms delay
        await self._flush()
    
    async def _flush(self):
        """Flush the buffer."""
        if not self._buffer:
            return
        
        message = "\n".join(self._buffer)
        self._buffer.clear()
        
        await self.emitter.emit_run_log(self.run_id, message)
    
    async def close(self):
        """Close the streamer and flush remaining logs."""
        if self._flush_task and not self._flush_task.done():
            self._flush_task.cancel()
        await self._flush()


# === WebSocket Endpoint Handler ===


async def websocket_endpoint(websocket: WebSocket, client_id: Optional[str] = None):
    """
    WebSocket endpoint handler.
    
    Protocol:
    - Client connects and receives connection confirmation
    - Client can send commands: subscribe, unsubscribe, ping, pong
    - Server broadcasts events based on subscriptions
    - Server sends periodic pings to keep connection alive
    """
    try:
        connection_id = await manager.connect(websocket, client_id)
    except ConnectionError as e:
        logger.warning(f"Connection rejected: {e}")
        return
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            
            # Update activity on any message
            manager.update_activity(connection_id)
            
            try:
                message = json.loads(data)
                command = WSCommand(**message)
                
                # Handle built-in commands
                if command.command == "ping":
                    # Client-initiated ping, respond with pong
                    await manager.send_to(connection_id, WSMessage(
                        type=EventType.PONG,
                        data={"timestamp": datetime.now().isoformat()},
                    ))
                
                elif command.command == "pong":
                    # Client response to server ping - update keepalive tracking
                    manager.handle_pong(connection_id)
                
                elif command.command == "subscribe":
                    topic = command.params.get("topic")
                    if topic:
                        await manager.subscribe(connection_id, topic)
                        await manager.send_to(connection_id, WSMessage(
                            type=EventType.NOTIFICATION,
                            data={"subscribed": topic},
                        ))
                
                elif command.command == "unsubscribe":
                    topic = command.params.get("topic")
                    if topic:
                        await manager.unsubscribe(connection_id, topic)
                        await manager.send_to(connection_id, WSMessage(
                            type=EventType.NOTIFICATION,
                            data={"unsubscribed": topic},
                        ))
                
                elif command.command == "get_status":
                    await manager.send_to(connection_id, WSMessage(
                        type=EventType.NOTIFICATION,
                        data=manager.get_connection_info(),
                    ))
                
                else:
                    # Handle custom commands
                    response = await manager.handle_command(connection_id, command)
                    if response:
                        await manager.send_to(connection_id, response)
            
            except json.JSONDecodeError:
                await manager.send_to(connection_id, WSMessage(
                    type=EventType.ERROR,
                    data={"error": "Invalid JSON"},
                ))
            except Exception as e:
                logger.error(f"Error handling WebSocket message: {e}")
                await manager.send_to(connection_id, WSMessage(
                    type=EventType.ERROR,
                    data={"error": str(e)},
                ))
    
    except WebSocketDisconnect:
        await manager.disconnect(connection_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await manager.disconnect(connection_id)


# === FastAPI Integration ===


def add_websocket_routes(
    app,
    ping_interval: Optional[int] = None,
    ping_timeout: Optional[int] = None,
    max_connections: Optional[int] = None,
):
    """
    Add WebSocket routes to a FastAPI application.
    
    Args:
        app: FastAPI application instance
        ping_interval: Optional ping interval override (seconds)
        ping_timeout: Optional ping timeout override (seconds)
        max_connections: Optional max connections override
    
    Returns:
        The app with WebSocket routes added
    """
    # Configure manager if custom settings provided
    if any([ping_interval, ping_timeout, max_connections]):
        configure_manager(
            ping_interval=ping_interval or 30,
            ping_timeout=ping_timeout or 10,
            max_connections=max_connections or 100,
        )
    
    @app.on_event("startup")
    async def start_websocket_manager():
        """Start the WebSocket connection manager on app startup."""
        await manager.start()
        logger.info("WebSocket manager started")
    
    @app.on_event("shutdown")
    async def stop_websocket_manager():
        """Stop the WebSocket connection manager on app shutdown."""
        await manager.stop()
        logger.info("WebSocket manager stopped")
    
    @app.websocket("/ws")
    async def ws_endpoint(websocket: WebSocket):
        await websocket_endpoint(websocket)
    
    @app.websocket("/ws/{client_id}")
    async def ws_endpoint_with_id(websocket: WebSocket, client_id: str):
        await websocket_endpoint(websocket, client_id)
    
    @app.get("/ws/status")
    async def ws_status():
        """Get WebSocket connection status."""
        return manager.get_connection_info()
    
    return app


# === Utilities ===


def get_emitter() -> EventEmitter:
    """Get the global event emitter."""
    return emitter


def get_manager() -> ConnectionManager:
    """Get the global connection manager."""
    return manager


async def broadcast_event(event_type: EventType, data: dict[str, Any], topic: Optional[str] = None):
    """Convenience function to broadcast an event."""
    await emitter.emit(event_type, data, topic)

