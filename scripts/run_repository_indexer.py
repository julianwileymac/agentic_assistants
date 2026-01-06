#!/usr/bin/env python3
"""
Repository Indexing Script

This script runs the multi-agent CrewAI crew to analyze, annotate, and index
a local code repository into vector stores.

Usage:
    python scripts/run_repository_indexer.py /path/to/repo
    python scripts/run_repository_indexer.py /path/to/repo --collection my-project
    python scripts/run_repository_indexer.py /path/to/repo --experiment indexing-v1 --model llama3.2

Options:
    --collection    Vector store collection name (default: repo folder name)
    --experiment    MLFlow experiment name (default: repository-indexing)
    --model         LLM model to use (default: from config)
    --backend       Vector store backend: lancedb, chroma, both (default: lancedb)
    --embedding     Embedding model (default: nomic-embed-text)
    --force         Force re-indexing even if already indexed
    --verbose       Enable verbose output
    --no-track      Disable MLFlow tracking

Environment Variables:
    OLLAMA_HOST             Ollama server URL
    MLFLOW_TRACKING_URI     MLFlow tracking URI
    VECTORDB_BACKEND        Vector store backend
    EMBEDDING_MODEL         Embedding model name

Examples:
    # Basic usage
    python scripts/run_repository_indexer.py ./my-project

    # With custom collection and experiment
    python scripts/run_repository_indexer.py ./my-project \\
        --collection my-project-v2 \\
        --experiment repo-analysis

    # Using both vector stores
    python scripts/run_repository_indexer.py ./my-project --backend both

    # With specific model
    python scripts/run_repository_indexer.py ./my-project --model mistral
"""

import argparse
import os
import sys
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agentic_assistants import AgenticConfig
from agentic_assistants.crews import RepositoryIndexingCrew
from agentic_assistants.crews.telemetry import get_crew_telemetry
from agentic_assistants.utils.logging import setup_logging, get_logger

logger = get_logger(__name__)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Index a code repository using multi-agent analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    
    parser.add_argument(
        "repo_path",
        type=str,
        help="Path to the repository to index",
    )
    
    parser.add_argument(
        "--collection",
        type=str,
        default=None,
        help="Vector store collection name (default: repo folder name)",
    )
    
    parser.add_argument(
        "--experiment",
        type=str,
        default="repository-indexing",
        help="MLFlow experiment name",
    )
    
    parser.add_argument(
        "--run-name",
        type=str,
        default=None,
        help="Name for this run (auto-generated if not provided)",
    )
    
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="LLM model to use for agents",
    )
    
    parser.add_argument(
        "--backend",
        type=str,
        choices=["lancedb", "chroma", "both"],
        default="lancedb",
        help="Vector store backend",
    )
    
    parser.add_argument(
        "--embedding",
        type=str,
        default=None,
        help="Embedding model name",
    )
    
    parser.add_argument(
        "--embedding-provider",
        type=str,
        choices=["ollama", "sentence_transformers", "openai"],
        default="ollama",
        help="Embedding provider",
    )
    
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-indexing",
    )
    
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output",
    )
    
    parser.add_argument(
        "--no-track",
        action="store_true",
        help="Disable MLFlow tracking",
    )
    
    parser.add_argument(
        "--no-telemetry",
        action="store_true",
        help="Disable OpenTelemetry tracing",
    )
    
    parser.add_argument(
        "--tags",
        type=str,
        nargs="*",
        help="Additional tags in key=value format",
    )
    
    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()
    
    # Setup logging
    log_level = "DEBUG" if args.verbose else "INFO"
    setup_logging(level=log_level)
    
    # Validate repo path
    repo_path = Path(args.repo_path).resolve()
    if not repo_path.exists():
        logger.error(f"Repository path does not exist: {repo_path}")
        sys.exit(1)
    
    if not repo_path.is_dir():
        logger.error(f"Repository path is not a directory: {repo_path}")
        sys.exit(1)
    
    # Determine collection name
    collection = args.collection or repo_path.name
    
    # Parse tags
    tags = {}
    if args.tags:
        for tag in args.tags:
            if "=" in tag:
                key, value = tag.split("=", 1)
                tags[key] = value
    
    # Create configuration
    config = AgenticConfig(
        mlflow_enabled=not args.no_track,
        telemetry_enabled=not args.no_telemetry,
    )
    
    logger.info("=" * 60)
    logger.info("Repository Indexing Crew")
    logger.info("=" * 60)
    logger.info(f"Repository: {repo_path}")
    logger.info(f"Collection: {collection}")
    logger.info(f"Experiment: {args.experiment}")
    logger.info(f"Backend: {args.backend}")
    logger.info(f"Model: {args.model or 'default'}")
    logger.info(f"Embedding: {args.embedding or 'default'}")
    logger.info(f"MLFlow tracking: {'disabled' if args.no_track else 'enabled'}")
    logger.info(f"Telemetry: {'disabled' if args.no_telemetry else 'enabled'}")
    logger.info("=" * 60)
    
    # Initialize telemetry
    telemetry = get_crew_telemetry(config)
    
    try:
        # Create and run the crew
        with telemetry.trace_crew_run(
            "repository-indexer",
            attributes={
                "repo_path": str(repo_path),
                "collection": collection,
                "backend": args.backend,
            },
        ):
            crew = RepositoryIndexingCrew(
                config=config,
                model=args.model,
                vector_backend=args.backend,
                embedding_model=args.embedding,
                verbose=args.verbose,
            )
            
            result = crew.run(
                repo_path=repo_path,
                collection=collection,
                experiment_name=args.experiment,
                run_name=args.run_name,
                tags=tags,
                force_reindex=args.force,
            )
        
        # Print results
        print("\n" + "=" * 60)
        print("INDEXING RESULTS")
        print("=" * 60)
        print(f"Success: {result.success}")
        print(f"Duration: {result.duration_seconds:.2f} seconds")
        print(f"Collection: {result.collection}")
        
        if result.stats:
            print("\nStatistics:")
            for key, value in result.stats.items():
                print(f"  {key}: {value}")
        
        if result.errors:
            print("\nErrors:")
            for error in result.errors:
                print(f"  - {error}")
        
        if result.experiment_run_id:
            print(f"\nMLFlow Run ID: {result.experiment_run_id}")
            print(f"View at: {config.mlflow.tracking_uri}/#/experiments")
        
        print("=" * 60)
        
        # Exit with appropriate code
        sys.exit(0 if result.success else 1)
        
    except KeyboardInterrupt:
        logger.info("\nIndexing cancelled by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Indexing failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

