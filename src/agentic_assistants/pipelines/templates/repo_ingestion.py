"""
Repository ingestion pipeline template.

This pipeline clones/pulls remote Git repositories, indexes code into the
vector store, optionally augments with local agents, and writes plaintext
summaries for every ingestion run.
"""

from __future__ import annotations

import json
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from agentic_assistants.config import AgenticConfig
from agentic_assistants.crews import RepositoryIndexingCrew
from agentic_assistants.data.telemetry import get_metrics, trace_operation
from agentic_assistants.indexing.codebase import CodebaseIndexer
from agentic_assistants.integrations.git_ops import GitOperations
from agentic_assistants.pipelines.node import Node
from agentic_assistants.pipelines.pipeline import Pipeline
from agentic_assistants.utils.logging import get_logger
from agentic_assistants.vectordb.base import Document, VectorStore

logger = get_logger(__name__)


@dataclass
class RepoIngestionConfig:
    """Configuration for repository ingestion pipeline."""

    collection: str = "global-knowledgebase"
    repos_manifest: str = "repos.yaml"
    cache_dir: str = "./data/repo_cache"
    summary_output: str = "./data/repo_summaries"

    chunk_size: int = 1200
    chunk_overlap: int = 200
    chunking_strategy: str = "code"
    include_hidden: bool = False
    force_reindex: bool = False
    respect_manual_override: bool = True
    only_repos: Optional[List[str]] = None

    augment_strategy: str = "crew"  # crew | langchain | none
    global_tags: List[str] = field(default_factory=list)
    global_context: Optional[str] = None

    scheduling_default_cron: str = "0 */6 * * *"
    scheduling_timezone: str = "UTC"

    vectordb_backend: Optional[str] = None
    vectordb_path: Optional[str] = None
    vectordb_embedding_model: Optional[str] = None
    vectordb_embedding_dimension: Optional[int] = None

    crew_model: Optional[str] = None
    crew_verbose: bool = False
    langchain_model: Optional[str] = None
    langchain_temperature: float = 0.2

    def to_dict(self) -> Dict[str, Any]:
        return {
            "collection": self.collection,
            "repos_manifest": self.repos_manifest,
            "cache_dir": self.cache_dir,
            "summary_output": self.summary_output,
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "chunking_strategy": self.chunking_strategy,
            "include_hidden": self.include_hidden,
            "force_reindex": self.force_reindex,
            "respect_manual_override": self.respect_manual_override,
            "only_repos": self.only_repos,
            "augment_strategy": self.augment_strategy,
            "global_tags": self.global_tags,
            "global_context": self.global_context,
            "scheduling_default_cron": self.scheduling_default_cron,
            "scheduling_timezone": self.scheduling_timezone,
            "vectordb_backend": self.vectordb_backend,
            "vectordb_path": self.vectordb_path,
            "vectordb_embedding_model": self.vectordb_embedding_model,
            "vectordb_embedding_dimension": self.vectordb_embedding_dimension,
            "crew_model": self.crew_model,
            "crew_verbose": self.crew_verbose,
            "langchain_model": self.langchain_model,
            "langchain_temperature": self.langchain_temperature,
        }


def _resolve_path(path_str: str, base_dir: Path) -> str:
    path = Path(path_str).expanduser()
    if not path.is_absolute():
        path = base_dir / path
    return str(path.resolve())


def _load_yaml(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def load_repo_ingestion_config(
    config_path: str,
    overrides: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Load config YAML and normalize paths."""
    with trace_operation("repo_ingestion.load_config", component="pipeline"):
        config_file = Path(config_path).expanduser().resolve()
        raw = _load_yaml(config_file)
        overrides = overrides or {}

        ingestion = raw.get("ingestion", {})
        scheduling = raw.get("scheduling", {})
        augmentation = raw.get("augmentation", {})
        vectordb = raw.get("vectordb", {})

        config = RepoIngestionConfig(
            collection=raw.get("collection", "global-knowledgebase"),
            repos_manifest=raw.get("repos_manifest", "repos.yaml"),
            cache_dir=raw.get("cache_dir", "./data/repo_cache"),
            summary_output=ingestion.get("summary_output", "./data/repo_summaries"),
            chunk_size=ingestion.get("chunk_size", 1200),
            chunk_overlap=ingestion.get("chunk_overlap", 200),
            chunking_strategy=ingestion.get("chunking_strategy", "code"),
            include_hidden=ingestion.get("include_hidden", False),
            force_reindex=ingestion.get("force_reindex", False),
            respect_manual_override=ingestion.get("respect_manual_override", True),
            augment_strategy=ingestion.get("augment_strategy", "crew"),
            global_tags=ingestion.get("tags", []),
            global_context=ingestion.get("context"),
            scheduling_default_cron=scheduling.get("default_cron", "0 */6 * * *"),
            scheduling_timezone=scheduling.get("timezone", "UTC"),
            vectordb_backend=vectordb.get("backend"),
            vectordb_path=vectordb.get("path"),
            vectordb_embedding_model=vectordb.get("embedding_model"),
            vectordb_embedding_dimension=vectordb.get("embedding_dimension"),
            crew_model=augmentation.get("crew", {}).get("model"),
            crew_verbose=augmentation.get("crew", {}).get("verbose", False),
            langchain_model=augmentation.get("langchain", {}).get("model"),
            langchain_temperature=augmentation.get("langchain", {}).get("temperature", 0.2),
        )

        # Apply runtime overrides
        for key, value in overrides.items():
            if hasattr(config, key):
                setattr(config, key, value)

        if config.chunking_strategy == "code":
            config.chunking_strategy = "code_aware"

        base_dir = config_file.parent
        config.repos_manifest = _resolve_path(config.repos_manifest, base_dir)
        config.cache_dir = _resolve_path(config.cache_dir, base_dir)
        config.summary_output = _resolve_path(config.summary_output, base_dir)
        if config.vectordb_path:
            config.vectordb_path = _resolve_path(config.vectordb_path, base_dir)

        logger.info(
            "Loaded repo ingestion config from %s (collection=%s)",
            config_file,
            config.collection,
        )

        return {
            "config_path": str(config_file),
            "config_dir": str(base_dir),
            **config.to_dict(),
        }


def load_repo_manifest(ingestion_config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Load repo manifest with repo entries."""
    with trace_operation("repo_ingestion.load_manifest", component="pipeline"):
        manifest_path = Path(ingestion_config["repos_manifest"])
        manifest = _load_yaml(manifest_path)
        repos = manifest.get("repos", [])
        if not isinstance(repos, list):
            raise ValueError("repos.yaml must define a list under 'repos'")
        return repos


def prepare_repo_queue(
    ingestion_config: Dict[str, Any],
    repo_manifest: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Normalize repo entries and apply defaults."""
    with trace_operation("repo_ingestion.prepare_queue", component="pipeline"):
        default_cron = ingestion_config.get("scheduling_default_cron")
        global_tags = ingestion_config.get("global_tags", [])
        global_context = ingestion_config.get("global_context")

        queue = []
        only_repos = ingestion_config.get("only_repos")
        for repo in repo_manifest:
            url = repo.get("url")
            if not url:
                logger.warning("Skipping repo entry without URL: %s", repo)
                continue

            name = repo.get("name") or Path(url.rstrip("/")).stem.replace(".git", "")
            if only_repos and name not in only_repos:
                continue
            tags = repo.get("tags", [])
            schedule = repo.get("schedule") or default_cron
            entry = {
                "name": name,
                "url": url,
                "branch": repo.get("branch", "main"),
                "tags": list(dict.fromkeys(global_tags + tags)),
                "context": repo.get("context") or global_context,
                "schedule": schedule,
                "manual_override": bool(repo.get("manual_override", False)),
                "enabled": repo.get("enabled", True),
                "depth": repo.get("depth"),
            }
            queue.append(entry)

        return queue


def _state_path(cache_dir: str, repo_name: str) -> Path:
    sanitized = repo_name.replace("/", "_")
    return Path(cache_dir) / ".agentic" / f"{sanitized}.json"


def _load_repo_state(state_path: Path) -> Dict[str, Any]:
    if not state_path.exists():
        return {}
    try:
        return json.loads(state_path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_repo_state(state_path: Path, state: Dict[str, Any]) -> None:
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")


def _collect_repo_context(repo_path: Path, max_depth: int = 2) -> str:
    """Collect a lightweight repo summary for LLM prompts."""
    import os

    lines = []
    readme_snippet = ""
    repo_path = repo_path.resolve()

    for root, dirs, files in os.walk(repo_path):
        rel = Path(root).relative_to(repo_path)
        depth = len(rel.parts)
        if depth > max_depth:
            dirs[:] = []
            continue

        if depth <= max_depth:
            indent = "  " * depth
            for name in sorted(files):
                if name.lower().startswith("readme") and not readme_snippet:
                    try:
                        readme_path = Path(root) / name
                        readme_snippet = readme_path.read_text(encoding="utf-8")[:3000]
                    except Exception:
                        pass
                lines.append(f"{indent}- {Path(root).relative_to(repo_path) / name}")

    context = "Repo file list (depth <= 2):\n" + "\n".join(lines[:200])
    if readme_snippet:
        context += "\n\nREADME snippet:\n" + readme_snippet
    return context


def sync_repos(
    ingestion_config: Dict[str, Any],
    repo_queue: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Clone or pull repositories into the cache folder."""
    with trace_operation("repo_ingestion.sync_repos", component="pipeline"):
        cache_dir = Path(ingestion_config["cache_dir"])
        cache_dir.mkdir(parents=True, exist_ok=True)

        git_ops = GitOperations()
        results = []

        for repo in repo_queue:
            if not repo.get("enabled", True):
                results.append({**repo, "status": "disabled"})
                continue

            repo_path = cache_dir / repo["name"]
            state_path = _state_path(str(cache_dir), repo["name"])
            state = _load_repo_state(state_path)

            status = "unknown"
            error = None
            commit_sha = None

            try:
                if repo_path.exists() and git_ops.is_git_repo(str(repo_path)):
                    pull_result = git_ops.pull(
                        repo_path=str(repo_path),
                        branch=repo.get("branch"),
                    )
                    status = "updated" if pull_result.success else "error"
                    if not pull_result.success:
                        error = pull_result.error or pull_result.message
                else:
                    if repo_path.exists():
                        status = "error"
                        error = f"Destination exists but is not a Git repo: {repo_path}"
                    else:
                        clone_result = git_ops.clone(
                            url=repo["url"],
                            dest_path=str(repo_path),
                            branch=repo.get("branch"),
                            depth=repo.get("depth"),
                        )
                        status = "cloned" if clone_result.success else "error"
                        if not clone_result.success:
                            error = clone_result.error or clone_result.message

                if status != "error":
                    commits = git_ops.get_commits(str(repo_path), limit=1)
                    if commits:
                        commit_sha = commits[0].sha

            except Exception as exc:
                status = "error"
                error = str(exc)

            result = {
                **repo,
                "local_path": str(repo_path),
                "status": status,
                "commit_sha": commit_sha,
                "last_ingested_commit": state.get("last_ingested_commit"),
                "error": error,
                "state_path": str(state_path),
            }
            results.append(result)

        return results


def index_repos(
    ingestion_config: Dict[str, Any],
    repo_sync_results: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Index repositories into the vector store."""
    with trace_operation("repo_ingestion.index_repos", component="pipeline"):
        metrics = get_metrics()
        config = AgenticConfig()
        vectordb_kwargs = {}
        if ingestion_config.get("vectordb_path"):
            vectordb_kwargs["path"] = ingestion_config["vectordb_path"]
        if ingestion_config.get("vectordb_embedding_model"):
            vectordb_kwargs["embedding_model"] = ingestion_config["vectordb_embedding_model"]
        if ingestion_config.get("vectordb_embedding_dimension"):
            vectordb_kwargs["embedding_dimension"] = ingestion_config["vectordb_embedding_dimension"]

        vector_store = VectorStore.create(
            backend=ingestion_config.get("vectordb_backend"),
            config=config,
            **vectordb_kwargs,
        )

        indexer = CodebaseIndexer(
            vector_store=vector_store,
            chunking_strategy=ingestion_config.get("chunking_strategy", "code"),
            chunk_size=ingestion_config.get("chunk_size", 1200),
            chunk_overlap=ingestion_config.get("chunk_overlap", 200),
            config=config,
        )

        results = []
        for repo in repo_sync_results:
            repo_name = repo["name"]
            if repo.get("status") == "error":
                results.append({
                    "name": repo_name,
                    "status": "error",
                    "error": repo.get("error"),
                })
                continue

            if ingestion_config.get("respect_manual_override") and repo.get("manual_override"):
                results.append({
                    "name": repo_name,
                    "status": "manual_override",
                    "skipped": True,
                })
                continue

            commit_sha = repo.get("commit_sha")
            if not ingestion_config.get("force_reindex") and commit_sha:
                if repo.get("last_ingested_commit") == commit_sha:
                    results.append({
                        "name": repo_name,
                        "status": "unchanged",
                        "skipped": True,
                        "commit_sha": commit_sha,
                    })
                    continue

            additional_metadata = {
                "repo_name": repo_name,
                "repo_url": repo.get("url"),
                "repo_branch": repo.get("branch"),
                "repo_commit": commit_sha,
                "tags": repo.get("tags", []),
                "context": repo.get("context"),
            }

            stats = indexer.index_directory(
                directory=repo["local_path"],
                collection=ingestion_config["collection"],
                force=ingestion_config.get("force_reindex", False),
                additional_metadata=additional_metadata,
            )

            metrics.increment(
                "repo_ingestion.files_indexed",
                stats.files_processed,
                tags={"repo": repo_name},
            )
            metrics.record(
                "repo_ingestion.chunks_indexed",
                stats.chunks_indexed,
                tags={"repo": repo_name},
            )

            results.append({
                "name": repo_name,
                "status": "indexed",
                "commit_sha": commit_sha,
                "stats": stats.to_dict(),
            })

            # Persist last ingested commit
            if commit_sha and repo.get("state_path"):
                _save_repo_state(
                    Path(repo["state_path"]),
                    {
                        "last_ingested_commit": commit_sha,
                        "last_ingested_at": datetime.utcnow().isoformat(),
                        "stats": stats.to_dict(),
                    },
                )

        return results


def augment_repos(
    ingestion_config: Dict[str, Any],
    repo_sync_results: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Augment repository content with agent analysis."""
    with trace_operation("repo_ingestion.augment_repos", component="pipeline"):
        strategy = ingestion_config.get("augment_strategy", "none")
        if strategy == "none":
            return []

        config = AgenticConfig()
        results = []

        if strategy == "crew":
            for repo in repo_sync_results:
                if repo.get("status") == "error":
                    continue
                if ingestion_config.get("respect_manual_override") and repo.get("manual_override"):
                    continue

                try:
                    crew = RepositoryIndexingCrew(
                        config=config,
                        model=ingestion_config.get("crew_model"),
                        verbose=ingestion_config.get("crew_verbose", False),
                    )
                    tags = {
                        "repo_name": repo["name"],
                        "repo_tags": ",".join(repo.get("tags", [])),
                    }
                    if repo.get("context"):
                        tags["repo_context"] = str(repo.get("context"))[:100]
                    output = crew.run(
                        repo_path=repo["local_path"],
                        collection=ingestion_config["collection"],
                        experiment_name=f"repo-augmentation-{repo['name']}",
                        tags=tags,
                    )
                    results.append({
                        "name": repo["name"],
                        "strategy": "crew",
                        "success": output.success,
                        "stats": output.stats,
                    })
                except Exception as exc:
                    results.append({
                        "name": repo["name"],
                        "strategy": "crew",
                        "success": False,
                        "error": str(exc),
                    })

        elif strategy == "langchain":
            try:
                from langchain_ollama import ChatOllama
            except ImportError as exc:
                raise ImportError(
                    "langchain-ollama is required for langchain augmentation. "
                    "Install with: pip install langchain-ollama"
                ) from exc

            vector_store = VectorStore.create(
                backend=ingestion_config.get("vectordb_backend"),
                config=config,
                path=ingestion_config.get("vectordb_path"),
                embedding_model=ingestion_config.get("vectordb_embedding_model"),
                embedding_dimension=ingestion_config.get("vectordb_embedding_dimension"),
            )
            llm = ChatOllama(
                model=ingestion_config.get("langchain_model") or config.ollama.default_model,
                temperature=ingestion_config.get("langchain_temperature", 0.2),
                base_url=config.ollama.host,
            )

            for repo in repo_sync_results:
                if repo.get("status") == "error":
                    continue
                if ingestion_config.get("respect_manual_override") and repo.get("manual_override"):
                    continue

                context_hint = _collect_repo_context(Path(repo["local_path"]))
                prompt = (
                    "You are a senior codebase analyst. Provide a concise repository analysis with:\n"
                    "- overview\n- tech_stack\n- architecture\n- key_modules\n- notable_patterns\n"
                    "Return plain text with short sections.\n\n"
                    f"Repository path: {repo['local_path']}\n\n"
                    f"{context_hint}"
                )
                try:
                    response = llm.invoke(prompt)
                    content = response.content if hasattr(response, "content") else str(response)
                    doc = Document(
                        id=str(uuid.uuid4()),
                        content=content,
                        metadata={
                            "repo_name": repo["name"],
                            "repo_url": repo.get("url"),
                            "repo_branch": repo.get("branch"),
                            "repo_commit": repo.get("commit_sha"),
                            "strategy": "langchain",
                            "source_type": "repo_analysis",
                            "tags": repo.get("tags", []),
                            "context": repo.get("context"),
                        },
                    )
                    vector_store.add(doc, collection=ingestion_config["collection"])
                    results.append({
                        "name": repo["name"],
                        "strategy": "langchain",
                        "success": True,
                    })
                except Exception as exc:
                    results.append({
                        "name": repo["name"],
                        "strategy": "langchain",
                        "success": False,
                        "error": str(exc),
                    })

        return results


def write_ingestion_summary(
    ingestion_config: Dict[str, Any],
    repo_sync_results: List[Dict[str, Any]],
    indexing_results: List[Dict[str, Any]],
    augmentation_results: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Write plaintext summary for an ingestion run."""
    with trace_operation("repo_ingestion.write_summary", component="pipeline"):
        summary_dir = Path(ingestion_config["summary_output"])
        summary_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        summary_path = summary_dir / f"repo_ingestion_{timestamp}.txt"

        indexing_by_repo = {r["name"]: r for r in indexing_results}
        augmentation_by_repo = {r["name"]: r for r in augmentation_results}

        lines = []
        lines.append(f"Repo Ingestion Summary - {datetime.utcnow().isoformat()} UTC")
        lines.append(f"Collection: {ingestion_config['collection']}")
        lines.append(f"Augmentation: {ingestion_config.get('augment_strategy')}")
        lines.append("-" * 80)

        ingested_count = 0
        errors = []
        for repo in repo_sync_results:
            name = repo["name"]
            lines.append(f"Repo: {name}")
            lines.append(f"  URL: {repo.get('url')}")
            lines.append(f"  Branch: {repo.get('branch')}")
            lines.append(f"  Commit: {repo.get('commit_sha')}")
            lines.append(f"  Sync Status: {repo.get('status')}")
            if repo.get("manual_override"):
                lines.append("  Manual Override: true")

            index_result = indexing_by_repo.get(name, {})
            lines.append(f"  Index Status: {index_result.get('status')}")
            if index_result.get("stats"):
                stats = index_result["stats"]
                lines.append(f"  Files processed: {stats.get('files_processed')}")
                lines.append(f"  Chunks indexed: {stats.get('chunks_indexed')}")

            if index_result.get("status") == "indexed":
                ingested_count += 1

            aug_result = augmentation_by_repo.get(name)
            if aug_result:
                lines.append(
                    f"  Augmentation: {aug_result.get('strategy')} "
                    f"(success={aug_result.get('success')})"
                )

            if repo.get("error") or index_result.get("error"):
                errors.append(repo.get("error") or index_result.get("error"))
                lines.append(f"  Error: {repo.get('error') or index_result.get('error')}")

            lines.append("")

        summary_path.write_text("\n".join(lines), encoding="utf-8")
        logger.info("Wrote ingestion summary: %s", summary_path)

        return {
            "summary_path": str(summary_path),
            "repo_count": len(repo_sync_results),
            "ingested_count": ingested_count,
            "errors": [e for e in errors if e],
        }


def create_repo_ingestion_pipeline(
    config_path: Optional[str] = None,
    overrides: Optional[Dict[str, Any]] = None,
) -> Pipeline:
    """Create the repository ingestion pipeline."""
    config_path = config_path or os.environ.get(
        "AGENTIC_REPO_INGESTION_CONFIG",
        "examples/global-knowledgebase-starter/config.yaml",
    )

    def _load_config():
        return load_repo_ingestion_config(config_path, overrides)

    load_config_node = Node(
        func=_load_config,
        inputs=[],
        outputs=["ingestion_config"],
        name="load_repo_ingestion_config",
        tags=["repo", "config"],
    )

    load_manifest_node = Node(
        func=load_repo_manifest,
        inputs=["ingestion_config"],
        outputs=["repo_manifest"],
        name="load_repo_manifest",
        tags=["repo", "manifest"],
    )

    prepare_queue_node = Node(
        func=prepare_repo_queue,
        inputs=["ingestion_config", "repo_manifest"],
        outputs=["repo_queue"],
        name="prepare_repo_queue",
        tags=["repo", "queue"],
    )

    sync_repos_node = Node(
        func=sync_repos,
        inputs=["ingestion_config", "repo_queue"],
        outputs=["repo_sync_results"],
        name="sync_repos",
        tags=["repo", "sync"],
    )

    index_repos_node = Node(
        func=index_repos,
        inputs=["ingestion_config", "repo_sync_results"],
        outputs=["indexing_results"],
        name="index_repos",
        tags=["repo", "index"],
    )

    augment_repos_node = Node(
        func=augment_repos,
        inputs=["ingestion_config", "repo_sync_results"],
        outputs=["augmentation_results"],
        name="augment_repos",
        tags=["repo", "augment"],
    )

    summary_node = Node(
        func=write_ingestion_summary,
        inputs=["ingestion_config", "repo_sync_results", "indexing_results", "augmentation_results"],
        outputs=["summary_result"],
        name="write_ingestion_summary",
        tags=["repo", "summary"],
    )

    pipeline = Pipeline(
        nodes=[
            load_config_node,
            load_manifest_node,
            prepare_queue_node,
            sync_repos_node,
            index_repos_node,
            augment_repos_node,
            summary_node,
        ],
        name="global_repo_ingestion",
        tags={"ingestion", "repo"},
    )

    return pipeline
