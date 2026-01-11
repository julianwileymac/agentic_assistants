# Chunk: 091ceea00cab_2

- source: `src/agentic_assistants/knowledge/hybrid_kb.py`
- lines: 167-250
- chunk: 3/4

```
     if feature_context:
                context_parts.append(f"[Feature Data]\n{feature_context}")
        
        # Generate answer
        if not context_parts:
            return "I couldn't find any relevant information."
        
        context = "\n\n".join(context_parts)
        
        # Use RAG KB for generation
        self._rag_kb._vector_kb = self._rag_kb._vector_kb  # Ensure same vector store
        prompt = self._rag_kb.query_template.format(
            context=context,
            question=question,
        )
        
        return self._rag_kb.llm_fn(prompt)
    
    def _get_feature_context(self, query: str) -> str:
        """Get relevant features for context."""
        try:
            from agentic_assistants.features import get_feature_store
            
            store = get_feature_store()
            
            context_parts = []
            for view_name in self.config.feature_views:
                view = store.get_feature_view(view_name)
                if view:
                    context_parts.append(
                        f"Feature View '{view_name}' contains: "
                        f"{', '.join(view.feature_names)}"
                    )
            
            return "\n".join(context_parts)
            
        except Exception as e:
            logger.debug(f"Could not get feature context: {e}")
            return ""
    
    def add_documents(
        self,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
    ) -> int:
        """Add documents to the knowledge base."""
        return self._rag_kb.add_documents(documents, metadatas, ids)
    
    def delete_documents(
        self,
        ids: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> int:
        """Delete documents from the knowledge base."""
        return self._rag_kb.delete_documents(ids, filters)
    
    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get a document by ID."""
        return self._rag_kb.get_document(doc_id)
    
    def add_from_data_source(self, source_id: str) -> int:
        """Add documents from a data source."""
        try:
            from agentic_assistants.data.catalog import DataCatalog
            from agentic_assistants.data.rag import IngestionPipeline
            
            catalog = DataCatalog()
            
            # Get dataset from catalog
            data = catalog.load(source_id)
            
            if data is None:
                return 0
            
            # Use ingestion pipeline
            pipeline = IngestionPipeline()
            
            if isinstance(data, str):
                result = pipeline.ingest(
                    source=data,
                    source_type="text",
                    collection=self.config.collection,
```
