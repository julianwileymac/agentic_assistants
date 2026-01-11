"""
REST API endpoints for data management operations.

These routes provide HTTP access to:
- Data catalog operations
- Knowledge base queries
- Feature store operations
- Job scheduling
- Corpus management
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

router = APIRouter(prefix="/data", tags=["data"])


# ============================================================================
# Request/Response Models
# ============================================================================

class DataSourceRequest(BaseModel):
    """Request to create a data source from template."""
    template_id: str
    name: str
    params: Dict[str, Any] = Field(default_factory=dict)


class SearchRequest(BaseModel):
    """Request to search a knowledge base."""
    query: str
    knowledge_base: str = "default"
    top_k: int = 5
    filters: Optional[Dict[str, Any]] = None


class QueryRequest(BaseModel):
    """Request to query a knowledge base with RAG."""
    question: str
    knowledge_base: str = "default"
    context_docs: int = 5


class FeatureRequest(BaseModel):
    """Request to get online features."""
    feature_refs: List[str]
    entity_keys: List[Dict[str, Any]]


class JobRequest(BaseModel):
    """Request to create a scheduled job."""
    job_type: str  # rss_monitor, website_monitor, data_sync, feature_materialization
    config: Dict[str, Any] = Field(default_factory=dict)
    trigger: str = "interval"
    trigger_args: Dict[str, Any] = Field(default_factory=dict)


class IngestRequest(BaseModel):
    """Request to ingest data."""
    source: str
    source_type: str = "url"
    collection: str = "default"
    metadata: Optional[Dict[str, Any]] = None


# ============================================================================
# Data Catalog Routes
# ============================================================================

@router.get("/catalog/datasets")
async def list_datasets():
    """List all datasets in the catalog."""
    from agentic_assistants.data.catalog import DataCatalog
    
    catalog = DataCatalog()
    datasets = catalog.list_datasets()
    
    return {"datasets": datasets, "count": len(datasets)}


@router.get("/catalog/templates")
async def list_templates(category: Optional[str] = None):
    """List available data source templates."""
    from agentic_assistants.data.templates import get_registry
    
    registry = get_registry()
    
    if category:
        templates = registry.list_by_category(category)
    else:
        templates = registry.list_all()
    
    return {"templates": templates, "count": len(templates)}


@router.get("/catalog/templates/{template_id}")
async def get_template(template_id: str):
    """Get details about a template."""
    from agentic_assistants.data.templates import get_registry
    
    registry = get_registry()
    template = registry.get(template_id)
    
    if not template:
        raise HTTPException(status_code=404, detail=f"Template not found: {template_id}")
    
    return template.to_dict()


@router.post("/catalog/create-from-template")
async def create_from_template(request: DataSourceRequest):
    """Create a dataset from a template."""
    from agentic_assistants.data.catalog import DataCatalog
    
    try:
        catalog = DataCatalog()
        dataset = catalog.create_from_template(
            name=request.name,
            template_id=request.template_id,
            params=request.params,
        )
        
        return {
            "success": True,
            "name": request.name,
            "template_id": request.template_id,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# Knowledge Base Routes
# ============================================================================

@router.get("/knowledge-bases")
async def list_knowledge_bases():
    """List all knowledge bases."""
    from agentic_assistants.knowledge import list_knowledge_bases
    
    return {"knowledge_bases": list_knowledge_bases()}


@router.post("/knowledge-bases/{kb_name}/search")
async def search_knowledge_base(kb_name: str, request: SearchRequest):
    """Search a knowledge base."""
    from agentic_assistants.knowledge import get_knowledge_base
    
    try:
        kb = get_knowledge_base(kb_name)
        results = kb.search(
            query=request.query,
            top_k=request.top_k,
            filters=request.filters,
        )
        
        return {
            "results": [r.to_dict() for r in results],
            "count": len(results),
            "knowledge_base": kb_name,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/knowledge-bases/{kb_name}/query")
async def query_knowledge_base(kb_name: str, request: QueryRequest):
    """Query a knowledge base with RAG."""
    from agentic_assistants.knowledge import get_knowledge_base
    
    try:
        kb = get_knowledge_base(kb_name)
        answer = kb.query(
            question=request.question,
            context_docs=request.context_docs,
        )
        
        return {
            "answer": answer,
            "knowledge_base": kb_name,
            "question": request.question,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/knowledge-bases/{kb_name}/stats")
async def get_knowledge_base_stats(kb_name: str):
    """Get knowledge base statistics."""
    from agentic_assistants.knowledge import get_knowledge_base
    
    try:
        kb = get_knowledge_base(kb_name)
        return kb.get_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Feature Store Routes
# ============================================================================

@router.get("/features/views")
async def list_feature_views():
    """List all feature views."""
    from agentic_assistants.features import get_feature_store
    
    store = get_feature_store()
    views = store.list_feature_views()
    
    return {"feature_views": views, "count": len(views)}


@router.get("/features/views/{view_name}")
async def get_feature_view(view_name: str):
    """Get details about a feature view."""
    from agentic_assistants.features import get_feature_store
    
    store = get_feature_store()
    view = store.get_feature_view(view_name)
    
    if not view:
        raise HTTPException(status_code=404, detail=f"Feature view not found: {view_name}")
    
    return view.to_dict()


@router.post("/features/online")
async def get_online_features(request: FeatureRequest):
    """Get online feature values."""
    from agentic_assistants.features import get_feature_store
    
    try:
        store = get_feature_store()
        vectors = store.get_online_features(
            feature_refs=request.feature_refs,
            entity_keys=request.entity_keys,
        )
        
        return {
            "features": [v.to_dict() for v in vectors],
            "count": len(vectors),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/features/materialize")
async def materialize_features(
    background_tasks: BackgroundTasks,
    feature_views: Optional[List[str]] = None,
):
    """Materialize features to online store."""
    from agentic_assistants.features import get_feature_store
    
    def do_materialize():
        store = get_feature_store()
        return store.materialize(feature_views=feature_views)
    
    background_tasks.add_task(do_materialize)
    
    return {
        "status": "started",
        "feature_views": feature_views or "all",
    }


@router.get("/features/stats")
async def get_feature_store_stats():
    """Get feature store statistics."""
    from agentic_assistants.features import get_feature_store
    
    store = get_feature_store()
    return store.get_stats()


# ============================================================================
# Ingestion Routes
# ============================================================================

@router.post("/ingest")
async def ingest_data(
    request: IngestRequest,
    background_tasks: BackgroundTasks,
):
    """Ingest data from a source."""
    from agentic_assistants.data.rag import IngestionPipeline
    
    def do_ingest():
        pipeline = IngestionPipeline()
        return pipeline.ingest(
            source=request.source,
            source_type=request.source_type,
            collection=request.collection,
            metadata=request.metadata,
        )
    
    background_tasks.add_task(do_ingest)
    
    return {
        "status": "started",
        "source": request.source[:100],
        "source_type": request.source_type,
        "collection": request.collection,
    }


# ============================================================================
# Job Scheduling Routes
# ============================================================================

@router.get("/jobs")
async def list_jobs():
    """List all scheduled jobs."""
    from agentic_assistants.scheduling import get_scheduler
    
    scheduler = get_scheduler()
    return {"jobs": scheduler.list_jobs()}


@router.post("/jobs")
async def create_job(request: JobRequest):
    """Create a scheduled job."""
    from agentic_assistants.scheduling import get_scheduler
    from agentic_assistants.scheduling.jobs import (
        RSSMonitorJob,
        WebsiteMonitorJob,
        DataSyncJob,
        FeatureMaterializationJob,
    )
    
    scheduler = get_scheduler()
    
    # Create job instance
    job_types = {
        "rss_monitor": RSSMonitorJob,
        "website_monitor": WebsiteMonitorJob,
        "data_sync": DataSyncJob,
        "feature_materialization": FeatureMaterializationJob,
    }
    
    job_class = job_types.get(request.job_type)
    if not job_class:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown job type: {request.job_type}"
        )
    
    try:
        job = job_class(**request.config)
        job_id = scheduler.add_job(
            job,
            trigger=request.trigger,
            **request.trigger_args,
        )
        
        return {
            "job_id": job_id,
            "job_type": request.job_type,
            "trigger": request.trigger,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/jobs/{job_id}")
async def get_job(job_id: str):
    """Get job details."""
    from agentic_assistants.scheduling import get_scheduler
    
    scheduler = get_scheduler()
    job = scheduler.get_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")
    
    return job


@router.post("/jobs/{job_id}/run")
async def run_job(job_id: str, background_tasks: BackgroundTasks):
    """Run a job immediately."""
    from agentic_assistants.scheduling import get_scheduler
    
    scheduler = get_scheduler()
    
    def do_run():
        scheduler.run_job(job_id)
    
    background_tasks.add_task(do_run)
    
    return {"status": "started", "job_id": job_id}


@router.post("/jobs/{job_id}/pause")
async def pause_job(job_id: str):
    """Pause a scheduled job."""
    from agentic_assistants.scheduling import get_scheduler
    
    scheduler = get_scheduler()
    success = scheduler.pause_job(job_id)
    
    return {"paused": success, "job_id": job_id}


@router.post("/jobs/{job_id}/resume")
async def resume_job(job_id: str):
    """Resume a paused job."""
    from agentic_assistants.scheduling import get_scheduler
    
    scheduler = get_scheduler()
    success = scheduler.resume_job(job_id)
    
    return {"resumed": success, "job_id": job_id}


@router.delete("/jobs/{job_id}")
async def delete_job(job_id: str):
    """Delete a scheduled job."""
    from agentic_assistants.scheduling import get_scheduler
    
    scheduler = get_scheduler()
    success = scheduler.remove_job(job_id)
    
    if not success:
        raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")
    
    return {"deleted": True, "job_id": job_id}


# ============================================================================
# Cache Routes
# ============================================================================

@router.get("/cache/stats")
async def get_cache_stats():
    """Get cache statistics."""
    from agentic_assistants.data.caching import get_cache
    
    cache = get_cache()
    return cache.stats.to_dict()


@router.post("/cache/clear")
async def clear_cache():
    """Clear the cache."""
    from agentic_assistants.data.caching import clear_cache
    
    clear_cache()
    return {"cleared": True}
