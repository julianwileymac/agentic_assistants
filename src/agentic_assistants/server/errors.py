"""
Error handling utilities for the API server.

This module provides:
- VerboseError model for structured error responses
- Exception handlers for FastAPI
- Error ID tracking for correlation
- Development mode stack trace inclusion
"""

import os
import traceback
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from agentic_assistants.utils.logging import get_logger, StructuredLogger

logger = get_logger(__name__)
error_logger = StructuredLogger(__name__)


# === Error Models ===


class VerboseError(BaseModel):
    """Structured verbose error response."""

    error_id: str = Field(..., description="Unique error ID for tracking")
    message: str = Field(..., description="Human-readable error message")
    detail: Optional[str] = Field(default=None, description="Additional error details")
    error_type: str = Field(default="error", description="Error type/category")
    status_code: int = Field(default=500, description="HTTP status code")
    timestamp: str = Field(..., description="ISO timestamp of error")
    path: Optional[str] = Field(default=None, description="Request path")
    method: Optional[str] = Field(default=None, description="HTTP method")
    traceback: Optional[str] = Field(default=None, description="Stack trace (dev mode only)")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context")

    @classmethod
    def from_exception(
        cls,
        exc: Exception,
        request: Optional[Request] = None,
        status_code: int = 500,
        include_traceback: bool = False,
        context: Optional[Dict[str, Any]] = None,
    ) -> "VerboseError":
        """Create a VerboseError from an exception."""
        error_id = str(uuid.uuid4())[:8]
        
        # Determine message and detail
        message = str(exc)
        detail = None
        
        if isinstance(exc, HTTPException):
            message = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
            status_code = exc.status_code
        
        # Get traceback if requested
        tb = None
        if include_traceback:
            tb = traceback.format_exc()
        
        return cls(
            error_id=error_id,
            message=message,
            detail=detail,
            error_type=type(exc).__name__,
            status_code=status_code,
            timestamp=datetime.utcnow().isoformat() + "Z",
            path=str(request.url.path) if request else None,
            method=request.method if request else None,
            traceback=tb,
            context=context or {},
        )


class ErrorResponse(BaseModel):
    """API error response wrapper."""

    error: VerboseError
    success: bool = False


# === Error Store (for UI retrieval) ===


class ErrorStore:
    """
    Simple in-memory store for recent errors.
    
    Allows the UI to retrieve error details by ID.
    """

    _instance: Optional["ErrorStore"] = None
    MAX_ERRORS = 100

    def __init__(self):
        self._errors: Dict[str, VerboseError] = {}
        self._order: list[str] = []

    @classmethod
    def get_instance(cls) -> "ErrorStore":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def add(self, error: VerboseError) -> None:
        """Add an error to the store."""
        self._errors[error.error_id] = error
        self._order.append(error.error_id)

        # Trim old errors
        while len(self._order) > self.MAX_ERRORS:
            old_id = self._order.pop(0)
            self._errors.pop(old_id, None)

    def get(self, error_id: str) -> Optional[VerboseError]:
        """Get an error by ID."""
        return self._errors.get(error_id)

    def get_recent(self, limit: int = 20) -> list[VerboseError]:
        """Get recent errors."""
        recent_ids = self._order[-limit:][::-1]
        return [self._errors[eid] for eid in recent_ids if eid in self._errors]

    def clear(self) -> None:
        """Clear all errors."""
        self._errors.clear()
        self._order.clear()


# === Exception Handlers ===


def is_development_mode() -> bool:
    """Check if running in development mode."""
    return os.environ.get("AGENTIC_ENV", "development").lower() in ("development", "dev", "local")


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTPException with verbose error response."""
    include_tb = is_development_mode()
    
    error = VerboseError.from_exception(
        exc,
        request=request,
        status_code=exc.status_code,
        include_traceback=include_tb,
    )
    
    # Log the error
    error_logger.warning(
        f"HTTP {exc.status_code}: {error.message}",
        error_id=error.error_id,
        path=error.path,
        method=error.method,
        status_code=exc.status_code,
    )
    
    # Store for UI retrieval
    ErrorStore.get_instance().add(error)
    
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(error=error).model_dump(),
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle generic exceptions with verbose error response."""
    include_tb = is_development_mode()
    
    error = VerboseError.from_exception(
        exc,
        request=request,
        status_code=500,
        include_traceback=include_tb,
    )
    
    # Log the error with full traceback
    error_logger.exception(
        f"Unhandled exception: {error.message}",
        error_id=error.error_id,
        path=error.path,
        method=error.method,
    )
    
    # Store for UI retrieval
    ErrorStore.get_instance().add(error)
    
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(error=error).model_dump(),
    )


async def validation_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle validation exceptions."""
    from fastapi.exceptions import RequestValidationError
    
    include_tb = is_development_mode()
    
    # Extract validation details
    errors = []
    if isinstance(exc, RequestValidationError):
        for error in exc.errors():
            loc = " -> ".join(str(x) for x in error.get("loc", []))
            msg = error.get("msg", "")
            errors.append(f"{loc}: {msg}")
    
    error = VerboseError(
        error_id=str(uuid.uuid4())[:8],
        message="Request validation failed",
        detail="; ".join(errors) if errors else str(exc),
        error_type="ValidationError",
        status_code=422,
        timestamp=datetime.utcnow().isoformat() + "Z",
        path=str(request.url.path),
        method=request.method,
        traceback=traceback.format_exc() if include_tb else None,
        context={"validation_errors": errors},
    )
    
    error_logger.warning(
        f"Validation error: {error.detail}",
        error_id=error.error_id,
        path=error.path,
    )
    
    ErrorStore.get_instance().add(error)
    
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(error=error).model_dump(),
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers with the FastAPI app."""
    from fastapi.exceptions import RequestValidationError
    
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)


# === Error API Endpoints ===


def create_error_routes():
    """Create API routes for error management."""
    from fastapi import APIRouter
    
    router = APIRouter(prefix="/errors", tags=["errors"])
    
    @router.get("")
    async def list_recent_errors(limit: int = 20) -> dict:
        """List recent errors."""
        store = ErrorStore.get_instance()
        errors = store.get_recent(limit)
        return {
            "errors": [e.model_dump() for e in errors],
            "total": len(errors),
        }
    
    @router.get("/{error_id}")
    async def get_error(error_id: str) -> dict:
        """Get error details by ID."""
        store = ErrorStore.get_instance()
        error = store.get(error_id)
        
        if error is None:
            raise HTTPException(status_code=404, detail="Error not found")
        
        return {"error": error.model_dump()}
    
    @router.delete("")
    async def clear_errors() -> dict:
        """Clear all stored errors."""
        store = ErrorStore.get_instance()
        store.clear()
        return {"status": "cleared"}
    
    return router
