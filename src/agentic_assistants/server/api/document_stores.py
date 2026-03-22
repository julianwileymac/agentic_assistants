"""
Document Stores API - Ephemeral, lightweight document collections.

Unlike knowledge bases (persistent, multi-topic, project-linked), document stores
are transient, single-purpose collections with optional TTL auto-expiry.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter()

# ---------------------------------------------------------------------------
# In-memory store (swap for DB / Redis in production)
# ---------------------------------------------------------------------------

_doc_stores: dict[str, dict] = {}
_doc_store_documents: dict[str, list[dict]] = {}


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class CreateDocumentStoreRequest(BaseModel):
    name: str
    description: Optional[str] = None
    source_type: Optional[str] = None
    source_value: Optional[str] = None
    ttl_hours: Optional[int] = None
    tags: list[str] = Field(default_factory=list)
    populate_via_dagster: bool = False


class UpdateDocumentStoreRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    ttl_hours: Optional[int] = None
    tags: Optional[list[str]] = None


class AddDocumentRequest(BaseModel):
    title: str
    content: str
    source: Optional[str] = None
    metadata: Optional[dict] = None


class SearchRequest(BaseModel):
    query: str
    top_k: int = 10


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _compute_status(store: dict) -> str:
    if not store.get("expires_at"):
        return "active"
    expires = datetime.fromisoformat(store["expires_at"])
    now = datetime.now(timezone.utc)
    if expires <= now:
        return "expired"
    if (expires - now).total_seconds() < 3600:
        return "expiring"
    return "active"


def _enrich(store: dict) -> dict:
    return {**store, "status": _compute_status(store)}


# ---------------------------------------------------------------------------
# CRUD endpoints
# ---------------------------------------------------------------------------

@router.get("")
async def list_document_stores():
    """List all document stores."""
    stores = [_enrich(s) for s in _doc_stores.values()]
    return {"stores": stores, "total": len(stores)}


@router.post("")
async def create_document_store(req: CreateDocumentStoreRequest):
    """Create a new document store."""
    store_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    expires_at = (now + timedelta(hours=req.ttl_hours)).isoformat() if req.ttl_hours else None

    store = {
        "id": store_id,
        "name": req.name,
        "description": req.description,
        "source_type": req.source_type,
        "source_value": req.source_value,
        "document_count": 0,
        "ttl_hours": req.ttl_hours,
        "created_at": now.isoformat(),
        "expires_at": expires_at,
        "tags": req.tags,
        "dagster_run_id": None,
        "datahub_urn": None,
    }
    _doc_stores[store_id] = store
    _doc_store_documents[store_id] = []

    if req.populate_via_dagster and req.source_value:
        store["dagster_run_id"] = f"pending-{store_id[:8]}"

    return _enrich(store)


@router.get("/{store_id}")
async def get_document_store(store_id: str):
    """Get a document store by ID."""
    store = _doc_stores.get(store_id)
    if not store:
        raise HTTPException(status_code=404, detail="Document store not found")
    return _enrich(store)


@router.put("/{store_id}")
async def update_document_store(store_id: str, req: UpdateDocumentStoreRequest):
    """Update a document store."""
    store = _doc_stores.get(store_id)
    if not store:
        raise HTTPException(status_code=404, detail="Document store not found")

    if req.name is not None:
        store["name"] = req.name
    if req.description is not None:
        store["description"] = req.description
    if req.tags is not None:
        store["tags"] = req.tags
    if req.ttl_hours is not None:
        store["ttl_hours"] = req.ttl_hours
        now = datetime.now(timezone.utc)
        store["expires_at"] = (now + timedelta(hours=req.ttl_hours)).isoformat() if req.ttl_hours else None

    return _enrich(store)


@router.delete("/{store_id}")
async def delete_document_store(store_id: str):
    """Delete a document store and its documents."""
    if store_id not in _doc_stores:
        raise HTTPException(status_code=404, detail="Document store not found")
    name = _doc_stores[store_id]["name"]
    del _doc_stores[store_id]
    _doc_store_documents.pop(store_id, None)
    return {"status": "deleted", "id": store_id, "name": name}


# ---------------------------------------------------------------------------
# Document management
# ---------------------------------------------------------------------------

@router.get("/{store_id}/documents")
async def list_documents(store_id: str):
    """List documents in a store."""
    if store_id not in _doc_stores:
        raise HTTPException(status_code=404, detail="Document store not found")
    docs = _doc_store_documents.get(store_id, [])
    return {"documents": docs, "total": len(docs)}


@router.post("/{store_id}/documents")
async def add_document(store_id: str, req: AddDocumentRequest):
    """Add a document to a store."""
    if store_id not in _doc_stores:
        raise HTTPException(status_code=404, detail="Document store not found")

    doc_id = str(uuid.uuid4())
    doc = {
        "id": doc_id,
        "title": req.title,
        "content_preview": req.content[:200] if req.content else None,
        "source": req.source,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "metadata": req.metadata or {},
    }
    _doc_store_documents.setdefault(store_id, []).append(doc)
    _doc_stores[store_id]["document_count"] = len(_doc_store_documents[store_id])
    return doc


@router.delete("/{store_id}/documents/{doc_id}")
async def delete_document(store_id: str, doc_id: str):
    """Remove a document from a store."""
    if store_id not in _doc_stores:
        raise HTTPException(status_code=404, detail="Document store not found")
    docs = _doc_store_documents.get(store_id, [])
    _doc_store_documents[store_id] = [d for d in docs if d["id"] != doc_id]
    _doc_stores[store_id]["document_count"] = len(_doc_store_documents[store_id])
    return {"status": "deleted", "id": doc_id}


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------

@router.post("/{store_id}/search")
async def search_documents(store_id: str, req: SearchRequest):
    """Search documents in a store (simple text matching fallback)."""
    if store_id not in _doc_stores:
        raise HTTPException(status_code=404, detail="Document store not found")

    docs = _doc_store_documents.get(store_id, [])
    query_lower = req.query.lower()

    results = [
        d for d in docs
        if query_lower in (d.get("title", "") or "").lower()
        or query_lower in (d.get("content_preview", "") or "").lower()
    ]
    return {"results": results[:req.top_k], "total": len(results)}
