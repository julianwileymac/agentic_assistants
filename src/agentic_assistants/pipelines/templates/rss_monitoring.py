"""
RSS monitoring pipeline template.

Pipeline for continuously monitoring RSS feeds and ingesting new content.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set

from agentic_assistants.pipelines.pipeline import Pipeline
from agentic_assistants.pipelines.node import Node
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class RSSMonitoringConfig:
    """Configuration for RSS monitoring pipeline."""
    
    feeds: List[str] = field(default_factory=list)
    collection: str = "rss_content"
    
    # Polling settings
    max_entries_per_feed: int = 20
    check_interval_minutes: int = 60
    since_hours: Optional[float] = 24  # Only fetch entries from last N hours
    
    # Processing
    chunk_size: int = 1024
    chunk_overlap: int = 128
    
    # Deduplication
    deduplicate: bool = True
    
    # Storage
    store_as_files: bool = True
    store_in_vectordb: bool = True
    artifacts_dir: str = "./data/rss_artifacts"


# Track seen entry IDs for deduplication
_seen_entries: Set[str] = set()


def fetch_rss_feeds(
    feeds: List[str],
    max_entries: int = 20,
    since_hours: Optional[float] = None,
) -> List[Dict[str, Any]]:
    """
    Fetch entries from RSS feeds.
    
    Args:
        feeds: List of feed URLs
        max_entries: Maximum entries per feed
        since_hours: Only fetch entries from last N hours
        
    Returns:
        List of feed data dictionaries
    """
    from agentic_assistants.data.datasets import RSSDataset
    
    results = []
    
    for feed_url in feeds:
        try:
            dataset = RSSDataset(
                url=feed_url,
                max_entries=max_entries,
                since_hours=since_hours,
            )
            
            feed_data = dataset.load()
            
            results.append({
                "feed_url": feed_url,
                "feed_info": feed_data.get("feed", {}),
                "entries": feed_data.get("entries", []),
                "success": True,
                "fetched_at": datetime.utcnow().isoformat(),
            })
            
            logger.info(f"Fetched {len(feed_data.get('entries', []))} entries from {feed_url}")
            
        except Exception as e:
            logger.error(f"Failed to fetch {feed_url}: {e}")
            results.append({
                "feed_url": feed_url,
                "feed_info": {},
                "entries": [],
                "success": False,
                "error": str(e),
            })
    
    return results


def filter_new_entries(
    feed_results: List[Dict[str, Any]],
    deduplicate: bool = True,
) -> List[Dict[str, Any]]:
    """
    Filter to only new entries (not previously seen).
    
    Args:
        feed_results: Output from fetch_rss_feeds
        deduplicate: Whether to deduplicate entries
        
    Returns:
        Filtered feed results
    """
    global _seen_entries
    
    filtered = []
    
    for feed in feed_results:
        if not feed.get("success"):
            filtered.append(feed)
            continue
        
        new_entries = []
        for entry in feed.get("entries", []):
            entry_id = entry.get("id") or entry.get("link") or entry.get("title", "")
            
            if deduplicate:
                if entry_id in _seen_entries:
                    continue
                _seen_entries.add(entry_id)
            
            new_entries.append(entry)
        
        filtered.append({
            **feed,
            "entries": new_entries,
            "original_count": len(feed.get("entries", [])),
            "new_count": len(new_entries),
        })
        
        if new_entries:
            logger.info(f"Found {len(new_entries)} new entries from {feed['feed_url']}")
    
    return filtered


def process_rss_entries(
    filtered_feeds: List[Dict[str, Any]],
    chunk_size: int = 1024,
    chunk_overlap: int = 128,
) -> List[Dict[str, Any]]:
    """
    Process and chunk RSS entries.
    
    Args:
        filtered_feeds: Output from filter_new_entries
        chunk_size: Target chunk size
        chunk_overlap: Overlap between chunks
        
    Returns:
        Processed entries with chunks
    """
    from agentic_assistants.data.rag.chunkers import TextChunker
    
    chunker = TextChunker(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    
    processed = []
    
    for feed in filtered_feeds:
        if not feed.get("success"):
            processed.append(feed)
            continue
        
        processed_entries = []
        
        for entry in feed.get("entries", []):
            # Combine title and content
            title = entry.get("title", "")
            content = entry.get("content", entry.get("summary", ""))
            full_text = f"{title}\n\n{content}" if title else content
            
            # Chunk the content
            chunks = chunker.chunk(full_text, {
                "source_url": entry.get("link"),
                "published": entry.get("published"),
                "author": entry.get("author"),
                "feed_url": feed["feed_url"],
                "feed_title": feed.get("feed_info", {}).get("title", ""),
            })
            
            processed_entries.append({
                **entry,
                "full_text": full_text,
                "chunks": [c.to_dict() for c in chunks],
            })
        
        processed.append({
            **feed,
            "entries": processed_entries,
        })
    
    total_entries = sum(len(f.get("entries", [])) for f in processed)
    total_chunks = sum(
        sum(len(e.get("chunks", [])) for e in f.get("entries", []))
        for f in processed
    )
    logger.info(f"Processed {total_entries} entries into {total_chunks} chunks")
    
    return processed


def augment_rss_content(
    processed_feeds: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Augment RSS content with metadata.
    
    Args:
        processed_feeds: Output from process_rss_entries
        
    Returns:
        Augmented feeds
    """
    from agentic_assistants.data.rag.augmenters import MetadataAugmenter, KeywordAugmenter, ChainedAugmenter
    from agentic_assistants.data.rag.annotators import LanguageAnnotator, QualityAnnotator, ChainedAnnotator
    from agentic_assistants.data.rag.chunkers import Chunk
    
    augmenter = ChainedAugmenter([
        MetadataAugmenter(),
        KeywordAugmenter(max_keywords=5),
    ])
    
    annotator = ChainedAnnotator([
        LanguageAnnotator(),
        QualityAnnotator(),
    ])
    
    augmented = []
    
    for feed in processed_feeds:
        if not feed.get("success"):
            augmented.append(feed)
            continue
        
        augmented_entries = []
        
        for entry in feed.get("entries", []):
            if not entry.get("chunks"):
                augmented_entries.append(entry)
                continue
            
            context = {
                "source": entry.get("link", ""),
                "source_type": "rss",
                "feed_url": feed["feed_url"],
            }
            
            # Reconstruct Chunk objects
            chunks = []
            for chunk_dict in entry["chunks"]:
                chunk = Chunk(
                    content=chunk_dict["content"],
                    index=chunk_dict["index"],
                    start_char=chunk_dict["start_char"],
                    end_char=chunk_dict["end_char"],
                    metadata=chunk_dict.get("metadata", {}),
                )
                chunks.append(chunk)
            
            # Augment and annotate
            chunks = augmenter.augment_batch(chunks, context)
            chunks = annotator.annotate_batch(chunks, context)
            
            entry["chunks"] = [c.to_dict() for c in chunks]
            augmented_entries.append(entry)
        
        augmented.append({
            **feed,
            "entries": augmented_entries,
        })
    
    return augmented


def store_rss_content(
    augmented_feeds: List[Dict[str, Any]],
    collection: str,
    store_as_files: bool = True,
    store_in_vectordb: bool = True,
    artifacts_dir: str = "./data/rss_artifacts",
) -> Dict[str, Any]:
    """
    Store processed RSS content.
    
    Args:
        augmented_feeds: Output from augment_rss_content
        collection: Vector store collection name
        store_as_files: Save as JSON files
        store_in_vectordb: Store in vector database
        artifacts_dir: Directory for file artifacts
        
    Returns:
        Storage statistics
    """
    import json
    import hashlib
    from pathlib import Path
    
    stats = {
        "total_feeds": len(augmented_feeds),
        "total_entries": 0,
        "total_chunks": 0,
        "stored_in_vectordb": 0,
        "file_paths": [],
    }
    
    # Count totals
    for feed in augmented_feeds:
        if feed.get("success"):
            entries = feed.get("entries", [])
            stats["total_entries"] += len(entries)
            stats["total_chunks"] += sum(len(e.get("chunks", [])) for e in entries)
    
    # File storage
    if store_as_files:
        artifacts_path = Path(artifacts_dir) / collection
        artifacts_path.mkdir(parents=True, exist_ok=True)
        
        for feed in augmented_feeds:
            if not feed.get("success") or not feed.get("entries"):
                continue
            
            # Create filename from feed URL
            url_hash = hashlib.sha256(feed["feed_url"].encode()).hexdigest()[:12]
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{url_hash}.json"
            filepath = artifacts_path / filename
            
            with open(filepath, "w") as f:
                json.dump(feed, f, indent=2)
            
            stats["file_paths"].append(str(filepath))
    
    # Vector store
    if store_in_vectordb:
        try:
            from agentic_assistants.vectordb import LanceDBStore
            from agentic_assistants.config import AgenticConfig
            
            config = AgenticConfig()
            vector_store = LanceDBStore(
                db_path=str(config.vectordb.db_path),
                embedding_model=config.vectordb.embedding_model,
            )
            
            all_documents = []
            all_metadatas = []
            
            for feed in augmented_feeds:
                if not feed.get("success"):
                    continue
                
                for entry in feed.get("entries", []):
                    for chunk in entry.get("chunks", []):
                        all_documents.append(chunk["content"])
                        metadata = chunk.get("metadata", {})
                        metadata["entry_url"] = entry.get("link")
                        metadata["entry_title"] = entry.get("title")
                        metadata["feed_url"] = feed["feed_url"]
                        all_metadatas.append(metadata)
            
            if all_documents:
                vector_store.add(
                    collection=collection,
                    documents=all_documents,
                    metadatas=all_metadatas,
                )
                stats["stored_in_vectordb"] = len(all_documents)
                
        except Exception as e:
            logger.error(f"Failed to store in vector DB: {e}")
    
    return stats


def create_rss_monitoring_pipeline(
    config: Optional[RSSMonitoringConfig] = None,
    feeds: Optional[List[str]] = None,
    collection: str = "rss_content",
    **kwargs,
) -> Pipeline:
    """
    Create an RSS monitoring pipeline.
    
    Args:
        config: Pipeline configuration
        feeds: List of feed URLs (if not using config)
        collection: Vector store collection
        **kwargs: Additional configuration
        
    Returns:
        Configured Pipeline instance
    """
    if config is None:
        config = RSSMonitoringConfig(
            feeds=feeds or [],
            collection=collection,
            **kwargs,
        )
    
    # Create nodes
    fetch_node = Node(
        func=fetch_rss_feeds,
        inputs=["feeds", "max_entries", "since_hours"],
        outputs=["feed_results"],
        name="fetch_rss_feeds",
        tags=["fetch", "rss"],
    )
    
    filter_node = Node(
        func=filter_new_entries,
        inputs=["feed_results", "deduplicate"],
        outputs=["filtered_feeds"],
        name="filter_new_entries",
        tags=["filter", "deduplicate"],
    )
    
    process_node = Node(
        func=process_rss_entries,
        inputs=["filtered_feeds", "chunk_size", "chunk_overlap"],
        outputs=["processed_feeds"],
        name="process_rss_entries",
        tags=["process", "chunk"],
    )
    
    augment_node = Node(
        func=augment_rss_content,
        inputs=["processed_feeds"],
        outputs=["augmented_feeds"],
        name="augment_rss_content",
        tags=["augment", "annotate"],
    )
    
    store_node = Node(
        func=store_rss_content,
        inputs=["augmented_feeds", "collection", "store_as_files", "store_in_vectordb", "artifacts_dir"],
        outputs=["storage_stats"],
        name="store_rss_content",
        tags=["store", "vectordb"],
    )
    
    pipeline = Pipeline(
        nodes=[fetch_node, filter_node, process_node, augment_node, store_node],
        name="rss_monitoring",
        tags=["monitoring", "rss"],
    )
    
    return pipeline


def clear_seen_entries() -> None:
    """Clear the deduplication cache."""
    global _seen_entries
    _seen_entries.clear()


def get_seen_count() -> int:
    """Get the number of seen entry IDs."""
    return len(_seen_entries)
