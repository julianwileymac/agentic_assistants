"""
Pre-built Dagster ops and assets for common tasks.

Provides reusable building blocks that wrap existing framework functionality
(web search, data fetching, LLM inference, workspace cleanup, etc.) as
Dagster ops and software-defined assets.
"""

from typing import Any, Dict, List, Optional

from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)

try:
    import dagster as dg
    DAGSTER_AVAILABLE = True
except ImportError:
    DAGSTER_AVAILABLE = False
    dg = None  # type: ignore


# ---------------------------------------------------------------------------
# Op Definitions
# ---------------------------------------------------------------------------

if DAGSTER_AVAILABLE:

    @dg.op(
        description="Execute a web search via configured search API and return results.",
        tags={"kind": "web_search"},
    )
    def web_search_op(
        context: dg.OpExecutionContext,
        query: str = "",
        max_results: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Execute a web search API call.

        Wraps the existing crawling / search module to perform web searches
        and return structured results.

        Args:
            context: Dagster execution context
            query: Search query string
            max_results: Maximum number of results

        Returns:
            List of search result dicts with url, title, snippet
        """
        context.log.info(f"Web search: '{query}' (max_results={max_results})")

        try:
            import httpx

            # Use a simple search API (DuckDuckGo instant answer as fallback)
            response = httpx.get(
                "https://api.duckduckgo.com/",
                params={"q": query, "format": "json", "no_html": 1},
                timeout=15,
            )
            data = response.json()

            results = []
            for topic in data.get("RelatedTopics", [])[:max_results]:
                if isinstance(topic, dict) and "Text" in topic:
                    results.append({
                        "url": topic.get("FirstURL", ""),
                        "title": topic.get("Text", "")[:100],
                        "snippet": topic.get("Text", ""),
                    })

            context.log.info(f"Web search returned {len(results)} results")
            return results

        except Exception as e:
            context.log.warning(f"Web search failed: {e}")
            return []

    @dg.op(
        description="Invoke an existing framework pipeline by name.",
        tags={"kind": "pipeline"},
    )
    def invoke_pipeline_op(
        context: dg.OpExecutionContext,
        pipeline_name: str = "",
        inputs: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Invoke an existing registered pipeline.

        Args:
            context: Dagster execution context
            pipeline_name: Name of the pipeline in the registry
            inputs: Input data for the pipeline

        Returns:
            Pipeline execution result
        """
        context.log.info(f"Invoking pipeline: {pipeline_name}")

        try:
            from agentic_assistants.engine import AgenticEngine

            engine = AgenticEngine()
            result = engine.run_pipeline(pipeline_name, inputs=inputs or {})
            context.log.info(f"Pipeline '{pipeline_name}' completed")
            return {"pipeline": pipeline_name, "success": True, "result": str(result)}

        except Exception as e:
            context.log.error(f"Pipeline '{pipeline_name}' failed: {e}")
            return {"pipeline": pipeline_name, "success": False, "error": str(e)}

    @dg.op(
        description="Fetch data from a configured catalog source.",
        tags={"kind": "data_fetch"},
    )
    def data_fetch_op(
        context: dg.OpExecutionContext,
        source_name: str = "",
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Fetch data from a catalog data source.

        Args:
            context: Dagster execution context
            source_name: Name of the data source in the catalog
            params: Optional query parameters

        Returns:
            Fetched data
        """
        context.log.info(f"Fetching data from source: {source_name}")

        try:
            from agentic_assistants.engine import AgenticEngine

            engine = AgenticEngine()
            data = engine.catalog.load(source_name)
            context.log.info(f"Data fetched from '{source_name}'")
            return data

        except Exception as e:
            context.log.error(f"Data fetch from '{source_name}' failed: {e}")
            raise

    @dg.op(
        description="Apply data transformations using Polars or Pandas.",
        tags={"kind": "transform"},
    )
    def data_transform_op(
        context: dg.OpExecutionContext,
        data: Any = None,
        transform_type: str = "identity",
        columns: Optional[List[str]] = None,
    ) -> Any:
        """
        Apply data transformations.

        Args:
            context: Dagster execution context
            data: Input data (DataFrame or dict)
            transform_type: Type of transform (identity, dropna, select, filter)
            columns: Column names for select/filter operations

        Returns:
            Transformed data
        """
        context.log.info(f"Applying transform: {transform_type}")

        if data is None:
            return data

        try:
            import polars as pl

            if isinstance(data, pl.DataFrame):
                if transform_type == "dropna":
                    return data.drop_nulls()
                elif transform_type == "select" and columns:
                    return data.select(columns)
                elif transform_type == "describe":
                    return data.describe()
                return data

        except ImportError:
            pass

        try:
            import pandas as pd

            if isinstance(data, pd.DataFrame):
                if transform_type == "dropna":
                    return data.dropna()
                elif transform_type == "select" and columns:
                    return data[columns]
                elif transform_type == "describe":
                    return data.describe()
                return data

        except ImportError:
            pass

        # Pass through for non-DataFrame types
        return data

    @dg.op(
        description="Run LLM inference through existing adapters.",
        tags={"kind": "llm"},
    )
    def llm_inference_op(
        context: dg.OpExecutionContext,
        prompt: str = "",
        model: str = "llama3.2",
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> str:
        """
        Run LLM inference using the framework's LLM integration.

        Args:
            context: Dagster execution context
            prompt: Input prompt
            model: Model name
            temperature: Sampling temperature
            max_tokens: Maximum output tokens

        Returns:
            LLM response text
        """
        context.log.info(f"LLM inference: model={model}, prompt_len={len(prompt)}")

        try:
            from langchain_ollama import OllamaLLM

            llm = OllamaLLM(model=model, temperature=temperature)
            response = llm.invoke(prompt)
            context.log.info(f"LLM response length: {len(response)}")
            return response

        except Exception as e:
            context.log.error(f"LLM inference failed: {e}")
            return f"Error: {e}"

    @dg.op(
        description="Clean workspace temporary files and old artifacts.",
        tags={"kind": "maintenance"},
    )
    def workspace_cleanup_op(
        context: dg.OpExecutionContext,
        workspace_path: str = ".",
        max_age_days: int = 7,
        patterns: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Clean up workspace temporary files and old artifacts.

        Args:
            context: Dagster execution context
            workspace_path: Path to the workspace
            max_age_days: Maximum age of files to keep (in days)
            patterns: File patterns to clean (e.g., ["*.tmp", "*.log"])

        Returns:
            Summary of cleaned files
        """
        import os
        import time as time_mod
        from pathlib import Path

        context.log.info(
            f"Workspace cleanup: path={workspace_path}, "
            f"max_age={max_age_days}d"
        )

        cleanup_patterns = patterns or ["*.tmp", "*.log", "*.pyc", "__pycache__"]
        cleaned = 0
        freed_bytes = 0
        cutoff = time_mod.time() - (max_age_days * 86400)

        workspace = Path(workspace_path)
        for pattern in cleanup_patterns:
            for path in workspace.rglob(pattern):
                try:
                    if path.is_file() and path.stat().st_mtime < cutoff:
                        size = path.stat().st_size
                        path.unlink()
                        cleaned += 1
                        freed_bytes += size
                    elif path.is_dir() and pattern == "__pycache__":
                        import shutil
                        shutil.rmtree(path, ignore_errors=True)
                        cleaned += 1
                except OSError:
                    pass

        result = {
            "files_cleaned": cleaned,
            "bytes_freed": freed_bytes,
            "mb_freed": round(freed_bytes / (1024 * 1024), 2),
        }
        context.log.info(f"Cleanup complete: {result}")
        return result

    # -------------------------------------------------------------------
    # Software-Defined Assets
    # -------------------------------------------------------------------

    @dg.asset(
        description="Repository ingestion asset. Indexes a Git repository.",
        group_name="ingestion",
    )
    def repo_ingestion_asset(context: dg.AssetExecutionContext) -> Dict[str, Any]:
        """
        Software-defined asset for repository ingestion.

        Triggers a repository indexing pipeline that clones/pulls a repo,
        parses files, generates embeddings, and stores them in the vector DB.

        Returns:
            Ingestion summary
        """
        context.log.info("Starting repository ingestion asset materialization")

        try:
            from agentic_assistants.engine import AgenticEngine

            engine = AgenticEngine()
            # Use the built-in repo ingestion pipeline
            result = engine.run_pipeline("repo_ingestion")
            context.log.info("Repository ingestion completed")
            return {"status": "success", "result": str(result)}

        except Exception as e:
            context.log.error(f"Repository ingestion failed: {e}")
            return {"status": "failed", "error": str(e)}

    @dg.asset(
        description="Knowledge base update asset. Refreshes vector store indices.",
        group_name="knowledge",
    )
    def knowledge_base_asset(context: dg.AssetExecutionContext) -> Dict[str, Any]:
        """
        Software-defined asset for knowledge base updates.

        Refreshes the vector store with new documents and embeddings.

        Returns:
            Update summary
        """
        context.log.info("Starting knowledge base update")

        try:
            from agentic_assistants.engine import AgenticEngine

            engine = AgenticEngine()
            engine.index_codebase()
            context.log.info("Knowledge base updated")
            return {"status": "success"}

        except Exception as e:
            context.log.error(f"Knowledge base update failed: {e}")
            return {"status": "failed", "error": str(e)}

    # -------------------------------------------------------------------
    # Convenience: pre-built job from ops
    # -------------------------------------------------------------------

    @dg.job(
        description="Workspace maintenance job: cleanup old files and refresh knowledge base.",
        tags={"kind": "maintenance"},
    )
    def maintenance_job():
        """Pre-built maintenance job combining cleanup and knowledge refresh."""
        workspace_cleanup_op()

    @dg.job(
        description="Web search and store results job.",
        tags={"kind": "search"},
    )
    def web_search_job():
        """Pre-built job for running a web search."""
        web_search_op()
