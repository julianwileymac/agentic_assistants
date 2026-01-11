# Chunk: 091ceea00cab_1

- source: `src/agentic_assistants/knowledge/hybrid_kb.py`
- lines: 84-176
- chunk: 2/4

```

        """
        Search the knowledge base with optional reranking.
        
        Args:
            query: Search query
            top_k: Number of results to return
            filters: Metadata filters
            rerank: Override reranking setting
            
        Returns:
            List of search results
        """
        k = top_k or self.config.top_k
        
        # Get more results for reranking
        fetch_k = k * 3 if (rerank or self.config.use_reranking) else k
        
        # Vector search
        results = self._rag_kb.search(query, top_k=fetch_k, filters=filters)
        
        # Rerank if enabled
        should_rerank = rerank if rerank is not None else self.config.use_reranking
        if should_rerank and self._reranker and len(results) > 1:
            results = self._rerank_results(query, results)
        
        return results[:k]
    
    def _rerank_results(
        self,
        query: str,
        results: List[SearchResult],
    ) -> List[SearchResult]:
        """Rerank results using cross-encoder."""
        if not self._reranker:
            return results
        
        # Prepare pairs for reranking
        pairs = [(query, r.content) for r in results]
        
        # Get reranking scores
        scores = self._reranker.predict(pairs)
        
        # Update scores and sort
        for result, score in zip(results, scores):
            result.score = float(score)
        
        results.sort(key=lambda x: x.score, reverse=True)
        
        return results
    
    def query(
        self,
        question: str,
        context_docs: Optional[int] = None,
        include_features: bool = False,
    ) -> str:
        """
        Query the knowledge base with RAG.
        
        Args:
            question: Question to answer
            context_docs: Number of context documents
            include_features: Include feature store data in context
            
        Returns:
            Generated answer
        """
        # Get vector search results
        k = context_docs or self.config.top_k
        results = self.search(question, top_k=k)
        
        # Build context
        context_parts = []
        
        # Add vector search results
        for i, result in enumerate(results, 1):
            source = result.source or f"Source {i}"
            context_parts.append(f"[{source}]\n{result.content}")
        
        # Add features if requested and configured
        if include_features and self.config.feature_views:
            feature_context = self._get_feature_context(question)
            if feature_context:
                context_parts.append(f"[Feature Data]\n{feature_context}")
        
        # Generate answer
        if not context_parts:
            return "I couldn't find any relevant information."
        
        context = "\n\n".join(context_parts)
        
```
