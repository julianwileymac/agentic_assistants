"""
Web ingestion pipeline template.

Pipeline for fetching, processing, and storing web content.
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from agentic_assistants.pipelines.pipeline import Pipeline
from agentic_assistants.pipelines.node import Node
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class WebIngestionConfig:
    """Configuration for web ingestion pipeline."""
    
    urls: List[str] = field(default_factory=list)
    collection: str = "web_content"
    render_js: bool = False
    max_pages_per_url: int = 1
    follow_links: Optional[str] = None
    selectors: Optional[Dict[str, str]] = None
    
    # Processing
    chunk_size: int = 1024
    chunk_overlap: int = 128
    chunking_strategy: str = "text"
    
    # Storage
    store_as_files: bool = True
    store_in_vectordb: bool = True
    artifacts_dir: str = "./data/web_artifacts"
    
    # Rate limiting
    delay_between_requests: float = 1.0


def fetch_web_content(
    urls: List[str],
    render_js: bool = False,
    selectors: Optional[Dict[str, str]] = None,
    max_pages: int = 1,
    delay: float = 1.0,
) -> List[Dict[str, Any]]:
    """
    Fetch content from web URLs.
    
    Args:
        urls: List of URLs to fetch
        render_js: Whether to render JavaScript
        selectors: CSS selectors for extraction
        max_pages: Maximum pages per URL
        delay: Delay between requests
        
    Returns:
        List of content dictionaries
    """
    import time
    from agentic_assistants.data.datasets import WebsiteDataset
    
    results = []
    
    for url in urls:
        try:
            dataset = WebsiteDataset(
                url=url,
                selectors=selectors or {"content": "body"},
                render_js=render_js,
                max_pages=max_pages,
                load_args={"delay_between_requests": delay},
            )
            
            data = dataset.load()
            results.append({
                "url": url,
                "content": data,
                "success": True,
            })
            
            logger.info(f"Fetched: {url}")
            
            if len(urls) > 1:
                time.sleep(delay)
                
        except Exception as e:
            logger.error(f"Failed to fetch {url}: {e}")
            results.append({
                "url": url,
                "content": None,
                "success": False,
                "error": str(e),
            })
    
    return results


def process_web_content(
    fetched_content: List[Dict[str, Any]],
    chunk_size: int = 1024,
    chunk_overlap: int = 128,
    chunking_strategy: str = "text",
) -> List[Dict[str, Any]]:
    """
    Process and chunk web content.
    
    Args:
        fetched_content: Output from fetch_web_content
        chunk_size: Target chunk size
        chunk_overlap: Overlap between chunks
        chunking_strategy: Chunking strategy to use
        
    Returns:
        List of processed content with chunks
    """
    from agentic_assistants.data.rag.chunkers import get_chunker
    
    chunker = get_chunker(
        chunking_strategy,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    
    processed = []
    
    for item in fetched_content:
        if not item.get("success") or not item.get("content"):
            processed.append({
                **item,
                "chunks": [],
            })
            continue
        
        # Extract text from content
        content = item["content"]
        if isinstance(content, dict):
            text = " ".join(str(v) for v in content.values() if v)
        else:
            text = str(content)
        
        # Chunk the content
        chunks = chunker.chunk(text, {"source_url": item["url"]})
        
        processed.append({
            **item,
            "text": text,
            "chunks": [c.to_dict() for c in chunks],
            "chunk_count": len(chunks),
        })
        
        logger.info(f"Processed {item['url']}: {len(chunks)} chunks")
    
    return processed


def augment_web_content(
    processed_content: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Augment web content with metadata and annotations.
    
    Args:
        processed_content: Output from process_web_content
        
    Returns:
        Augmented content
    """
    from agentic_assistants.data.rag.augmenters import create_default_augmenter
    from agentic_assistants.data.rag.annotators import create_default_annotator
    from agentic_assistants.data.rag.chunkers import Chunk
    
    augmenter = create_default_augmenter()
    annotator = create_default_annotator()
    
    augmented = []
    
    for item in processed_content:
        if not item.get("chunks"):
            augmented.append(item)
            continue
        
        context = {"source": item.get("url", ""), "source_type": "website"}
        
        # Reconstruct Chunk objects
        chunks = []
        for chunk_dict in item["chunks"]:
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
        
        item["chunks"] = [c.to_dict() for c in chunks]
        augmented.append(item)
    
    return augmented


def store_web_content(
    augmented_content: List[Dict[str, Any]],
    collection: str,
    store_as_files: bool = True,
    store_in_vectordb: bool = True,
    artifacts_dir: str = "./data/web_artifacts",
) -> Dict[str, Any]:
    """
    Store processed web content.
    
    Args:
        augmented_content: Output from augment_web_content
        collection: Vector store collection name
        store_as_files: Save as JSON files
        store_in_vectordb: Store in vector database
        artifacts_dir: Directory for file artifacts
        
    Returns:
        Storage statistics
    """
    import json
    import hashlib
    from datetime import datetime
    from pathlib import Path
    
    stats = {
        "total_items": len(augmented_content),
        "successful_items": 0,
        "total_chunks": 0,
        "stored_in_vectordb": 0,
        "file_paths": [],
    }
    
    # File storage
    if store_as_files:
        artifacts_path = Path(artifacts_dir) / collection
        artifacts_path.mkdir(parents=True, exist_ok=True)
        
        for item in augmented_content:
            if not item.get("success"):
                continue
            
            stats["successful_items"] += 1
            stats["total_chunks"] += len(item.get("chunks", []))
            
            # Create filename
            url_hash = hashlib.sha256(item["url"].encode()).hexdigest()[:12]
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{url_hash}.json"
            filepath = artifacts_path / filename
            
            with open(filepath, "w") as f:
                json.dump(item, f, indent=2)
            
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
            
            for item in augmented_content:
                if not item.get("success"):
                    continue
                
                for chunk in item.get("chunks", []):
                    all_documents.append(chunk["content"])
                    metadata = chunk.get("metadata", {})
                    metadata["source_url"] = item["url"]
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


def create_web_ingestion_pipeline(
    config: Optional[WebIngestionConfig] = None,
    urls: Optional[List[str]] = None,
    collection: str = "web_content",
    **kwargs,
) -> Pipeline:
    """
    Create a web ingestion pipeline.
    
    Args:
        config: Pipeline configuration
        urls: URLs to ingest (if not using config)
        collection: Vector store collection
        **kwargs: Additional configuration
        
    Returns:
        Configured Pipeline instance
    """
    if config is None:
        config = WebIngestionConfig(
            urls=urls or [],
            collection=collection,
            **kwargs,
        )
    
    # Create nodes
    fetch_node = Node(
        func=fetch_web_content,
        inputs=["urls", "render_js", "selectors", "max_pages", "delay"],
        outputs=["fetched_content"],
        name="fetch_web_content",
        tags=["fetch", "web"],
    )
    
    process_node = Node(
        func=process_web_content,
        inputs=["fetched_content", "chunk_size", "chunk_overlap", "chunking_strategy"],
        outputs=["processed_content"],
        name="process_web_content",
        tags=["process", "chunk"],
    )
    
    augment_node = Node(
        func=augment_web_content,
        inputs=["processed_content"],
        outputs=["augmented_content"],
        name="augment_web_content",
        tags=["augment", "annotate"],
    )
    
    store_node = Node(
        func=store_web_content,
        inputs=["augmented_content", "collection", "store_as_files", "store_in_vectordb", "artifacts_dir"],
        outputs=["storage_stats"],
        name="store_web_content",
        tags=["store", "vectordb"],
    )
    
    pipeline = Pipeline(
        nodes=[fetch_node, process_node, augment_node, store_node],
        name="web_ingestion",
        tags=["ingestion", "web"],
    )
    
    return pipeline
