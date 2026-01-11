"""
Dataset ingestion pipeline template.

Pipeline for processing structured datasets from various sources.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

from agentic_assistants.pipelines.pipeline import Pipeline
from agentic_assistants.pipelines.node import Node
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class DatasetIngestionConfig:
    """Configuration for dataset ingestion pipeline."""
    
    # Source configuration
    source_type: str = "url"  # url, kaggle, s3, file
    source_config: Dict[str, Any] = field(default_factory=dict)
    
    # Column for text content
    text_column: Optional[str] = None
    combine_columns: Optional[List[str]] = None
    
    # Processing
    collection: str = "datasets"
    chunk_size: int = 1024
    chunk_overlap: int = 128
    max_rows: Optional[int] = None
    
    # Storage
    store_as_files: bool = True
    store_in_vectordb: bool = True
    artifacts_dir: str = "./data/dataset_artifacts"


def fetch_dataset(
    source_type: str,
    source_config: Dict[str, Any],
    max_rows: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Fetch dataset from source.
    
    Args:
        source_type: Type of data source
        source_config: Source configuration
        max_rows: Maximum rows to fetch
        
    Returns:
        Dataset info with data
    """
    try:
        if source_type == "url":
            from agentic_assistants.data.datasets import URLDataset
            dataset = URLDataset(**source_config)
            data = dataset.load()
            
        elif source_type == "kaggle":
            from agentic_assistants.data.datasets import KaggleDataset
            dataset = KaggleDataset(**source_config)
            data = dataset.load()
            
        elif source_type == "s3":
            from agentic_assistants.data.datasets import S3PublicDataset
            dataset = S3PublicDataset(**source_config)
            data = dataset.load()
            
        elif source_type == "file":
            from pathlib import Path
            import pandas as pd
            
            file_path = source_config.get("filepath", source_config.get("path"))
            path = Path(file_path)
            
            if path.suffix.lower() == ".csv":
                data = pd.read_csv(path)
            elif path.suffix.lower() == ".parquet":
                data = pd.read_parquet(path)
            elif path.suffix.lower() == ".json":
                data = pd.read_json(path)
            else:
                raise ValueError(f"Unsupported file format: {path.suffix}")
        
        else:
            raise ValueError(f"Unknown source type: {source_type}")
        
        # Limit rows if specified
        if max_rows is not None:
            try:
                import pandas as pd
                if isinstance(data, pd.DataFrame):
                    data = data.head(max_rows)
                elif isinstance(data, list):
                    data = data[:max_rows]
            except ImportError:
                if isinstance(data, list):
                    data = data[:max_rows]
        
        return {
            "source_type": source_type,
            "source_config": source_config,
            "data": data,
            "success": True,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch dataset: {e}")
        return {
            "source_type": source_type,
            "source_config": source_config,
            "data": None,
            "success": False,
            "error": str(e),
        }


def extract_text_from_dataset(
    fetched_dataset: Dict[str, Any],
    text_column: Optional[str] = None,
    combine_columns: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """
    Extract text content from dataset rows.
    
    Args:
        fetched_dataset: Output from fetch_dataset
        text_column: Column containing text
        combine_columns: Columns to combine for text
        
    Returns:
        List of row dictionaries with text content
    """
    if not fetched_dataset.get("success"):
        return []
    
    data = fetched_dataset["data"]
    rows = []
    
    try:
        import pandas as pd
        
        if isinstance(data, pd.DataFrame):
            for idx, row in data.iterrows():
                row_dict = row.to_dict()
                
                if text_column and text_column in row_dict:
                    text = str(row_dict[text_column])
                elif combine_columns:
                    text_parts = [str(row_dict.get(col, "")) for col in combine_columns if row_dict.get(col)]
                    text = " ".join(text_parts)
                else:
                    # Combine all string columns
                    text_parts = [str(v) for v in row_dict.values() if v and isinstance(v, str)]
                    text = " ".join(text_parts)
                
                if text.strip():
                    rows.append({
                        "row_id": idx,
                        "text": text,
                        "metadata": row_dict,
                    })
        
        elif isinstance(data, list):
            for idx, item in enumerate(data):
                if isinstance(item, dict):
                    if text_column and text_column in item:
                        text = str(item[text_column])
                    elif combine_columns:
                        text_parts = [str(item.get(col, "")) for col in combine_columns if item.get(col)]
                        text = " ".join(text_parts)
                    else:
                        text_parts = [str(v) for v in item.values() if v and isinstance(v, str)]
                        text = " ".join(text_parts)
                    
                    if text.strip():
                        rows.append({
                            "row_id": idx,
                            "text": text,
                            "metadata": item,
                        })
                else:
                    rows.append({
                        "row_id": idx,
                        "text": str(item),
                        "metadata": {},
                    })
                    
    except ImportError:
        # Handle without pandas
        if isinstance(data, list):
            for idx, item in enumerate(data):
                text = str(item)
                rows.append({
                    "row_id": idx,
                    "text": text,
                    "metadata": item if isinstance(item, dict) else {},
                })
    
    logger.info(f"Extracted {len(rows)} rows with text content")
    return rows


def process_dataset_rows(
    extracted_rows: List[Dict[str, Any]],
    chunk_size: int = 1024,
    chunk_overlap: int = 128,
) -> List[Dict[str, Any]]:
    """
    Process and optionally chunk dataset rows.
    
    Args:
        extracted_rows: Output from extract_text_from_dataset
        chunk_size: Target chunk size
        chunk_overlap: Overlap between chunks
        
    Returns:
        Processed rows with chunks
    """
    from agentic_assistants.data.rag.chunkers import TextChunker
    
    chunker = TextChunker(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    
    processed = []
    
    for row in extracted_rows:
        text = row["text"]
        
        if len(text) <= chunk_size:
            # No chunking needed
            processed.append({
                **row,
                "chunks": [{
                    "content": text,
                    "index": 0,
                    "start_char": 0,
                    "end_char": len(text),
                    "metadata": {"row_id": row["row_id"]},
                }],
            })
        else:
            # Chunk the text
            chunks = chunker.chunk(text, {"row_id": row["row_id"]})
            processed.append({
                **row,
                "chunks": [c.to_dict() for c in chunks],
            })
    
    total_chunks = sum(len(r.get("chunks", [])) for r in processed)
    logger.info(f"Processed {len(processed)} rows into {total_chunks} chunks")
    
    return processed


def augment_dataset_content(
    processed_rows: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Augment dataset content with metadata.
    
    Args:
        processed_rows: Output from process_dataset_rows
        
    Returns:
        Augmented rows
    """
    from agentic_assistants.data.rag.augmenters import MetadataAugmenter, KeywordAugmenter, ChainedAugmenter
    from agentic_assistants.data.rag.chunkers import Chunk
    
    augmenter = ChainedAugmenter([
        MetadataAugmenter(),
        KeywordAugmenter(max_keywords=5),
    ])
    
    augmented = []
    
    for row in processed_rows:
        if not row.get("chunks"):
            augmented.append(row)
            continue
        
        context = {
            "source": "dataset",
            "source_type": "structured_data",
            "row_id": row.get("row_id"),
        }
        
        # Reconstruct Chunk objects
        chunks = []
        for chunk_dict in row["chunks"]:
            chunk = Chunk(
                content=chunk_dict["content"],
                index=chunk_dict["index"],
                start_char=chunk_dict["start_char"],
                end_char=chunk_dict["end_char"],
                metadata=chunk_dict.get("metadata", {}),
            )
            chunks.append(chunk)
        
        # Augment
        chunks = augmenter.augment_batch(chunks, context)
        
        row["chunks"] = [c.to_dict() for c in chunks]
        augmented.append(row)
    
    return augmented


def store_dataset_content(
    augmented_rows: List[Dict[str, Any]],
    collection: str,
    store_as_files: bool = True,
    store_in_vectordb: bool = True,
    artifacts_dir: str = "./data/dataset_artifacts",
) -> Dict[str, Any]:
    """
    Store processed dataset content.
    
    Args:
        augmented_rows: Output from augment_dataset_content
        collection: Vector store collection name
        store_as_files: Save as JSON files
        store_in_vectordb: Store in vector database
        artifacts_dir: Directory for file artifacts
        
    Returns:
        Storage statistics
    """
    import json
    from datetime import datetime
    from pathlib import Path
    
    stats = {
        "total_rows": len(augmented_rows),
        "total_chunks": sum(len(r.get("chunks", [])) for r in augmented_rows),
        "stored_in_vectordb": 0,
        "file_path": None,
    }
    
    # File storage - save all rows in one file
    if store_as_files:
        artifacts_path = Path(artifacts_dir) / collection
        artifacts_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_dataset.json"
        filepath = artifacts_path / filename
        
        # Prepare data for saving
        save_data = {
            "ingested_at": datetime.utcnow().isoformat(),
            "collection": collection,
            "row_count": len(augmented_rows),
            "chunk_count": stats["total_chunks"],
            "rows": augmented_rows,
        }
        
        with open(filepath, "w") as f:
            json.dump(save_data, f, indent=2, default=str)
        
        stats["file_path"] = str(filepath)
    
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
            
            for row in augmented_rows:
                for chunk in row.get("chunks", []):
                    all_documents.append(chunk["content"])
                    metadata = chunk.get("metadata", {})
                    metadata["row_id"] = row.get("row_id")
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


def create_dataset_ingestion_pipeline(
    config: Optional[DatasetIngestionConfig] = None,
    source_type: str = "url",
    source_config: Optional[Dict[str, Any]] = None,
    collection: str = "datasets",
    **kwargs,
) -> Pipeline:
    """
    Create a dataset ingestion pipeline.
    
    Args:
        config: Pipeline configuration
        source_type: Type of data source
        source_config: Source configuration
        collection: Vector store collection
        **kwargs: Additional configuration
        
    Returns:
        Configured Pipeline instance
    """
    if config is None:
        config = DatasetIngestionConfig(
            source_type=source_type,
            source_config=source_config or {},
            collection=collection,
            **kwargs,
        )
    
    # Create nodes
    fetch_node = Node(
        func=fetch_dataset,
        inputs=["source_type", "source_config", "max_rows"],
        outputs=["fetched_dataset"],
        name="fetch_dataset",
        tags=["fetch", "dataset"],
    )
    
    extract_node = Node(
        func=extract_text_from_dataset,
        inputs=["fetched_dataset", "text_column", "combine_columns"],
        outputs=["extracted_rows"],
        name="extract_text_from_dataset",
        tags=["extract", "dataset"],
    )
    
    process_node = Node(
        func=process_dataset_rows,
        inputs=["extracted_rows", "chunk_size", "chunk_overlap"],
        outputs=["processed_rows"],
        name="process_dataset_rows",
        tags=["process", "chunk"],
    )
    
    augment_node = Node(
        func=augment_dataset_content,
        inputs=["processed_rows"],
        outputs=["augmented_rows"],
        name="augment_dataset_content",
        tags=["augment"],
    )
    
    store_node = Node(
        func=store_dataset_content,
        inputs=["augmented_rows", "collection", "store_as_files", "store_in_vectordb", "artifacts_dir"],
        outputs=["storage_stats"],
        name="store_dataset_content",
        tags=["store", "vectordb"],
    )
    
    pipeline = Pipeline(
        nodes=[fetch_node, extract_node, process_node, augment_node, store_node],
        name="dataset_ingestion",
        tags=["ingestion", "dataset"],
    )
    
    return pipeline
