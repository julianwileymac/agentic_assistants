# Chunk: 091ceea00cab_3

- source: `src/agentic_assistants/knowledge/hybrid_kb.py`
- lines: 242-324
- chunk: 4/4

```
   # Use ingestion pipeline
            pipeline = IngestionPipeline()
            
            if isinstance(data, str):
                result = pipeline.ingest(
                    source=data,
                    source_type="text",
                    collection=self.config.collection,
                )
                return result.chunks_stored
            elif isinstance(data, dict):
                # Convert to text
                text = "\n".join(f"{k}: {v}" for k, v in data.items())
                result = pipeline.ingest(
                    source=text,
                    source_type="text",
                    collection=self.config.collection,
                )
                return result.chunks_stored
            
            return 0
            
        except Exception as e:
            logger.error(f"Failed to add from data source: {e}")
            return 0
    
    def add_from_dataset(self, dataset_name: str, text_column: str) -> int:
        """Add documents from a dataset."""
        try:
            from agentic_assistants.data.catalog import DataCatalog
            
            catalog = DataCatalog()
            
            # Load dataset
            df = catalog.load(dataset_name)
            
            if df is None or text_column not in df.columns:
                return 0
            
            # Extract texts
            documents = df[text_column].dropna().astype(str).tolist()
            
            # Build metadata from other columns
            metadatas = []
            for _, row in df.iterrows():
                metadata = {
                    col: str(row[col])
                    for col in df.columns
                    if col != text_column and row[col] is not None
                }
                metadata["dataset"] = dataset_name
                metadatas.append(metadata)
            
            return self.add_documents(documents, metadatas)
            
        except Exception as e:
            logger.error(f"Failed to add from dataset: {e}")
            return 0
    
    def sync_data_sources(self) -> Dict[str, int]:
        """Sync all configured data sources."""
        results = {}
        
        for source_id in self.config.data_sources:
            count = self.add_from_data_source(source_id)
            results[source_id] = count
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get knowledge base statistics."""
        base_stats = self._rag_kb.get_stats()
        
        return {
            **base_stats,
            "type": "hybrid",
            "data_sources": self.config.data_sources,
            "datasets": self.config.datasets,
            "feature_views": self.config.feature_views,
            "use_reranking": self.config.use_reranking,
            "reranker_available": self._reranker is not None,
        }
```
