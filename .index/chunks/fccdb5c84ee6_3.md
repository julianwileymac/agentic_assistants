# Chunk: fccdb5c84ee6_3

- source: `src/agentic_assistants/data/corpus/lexicon.py`
- lines: 253-321
- chunk: 4/4

```
= [t for t in tokens if len(t) >= self.min_term_length]
        
        # Remove stop words
        if self.remove_stopwords:
            tokens = [t for t in tokens if t not in self.STOP_WORDS]
        
        return tokens
    
    def add_document(self, text: str) -> int:
        """
        Add a document to the builder.
        
        Args:
            text: Document text
            
        Returns:
            Number of unique terms
        """
        tokens = self._tokenize(text)
        
        # Update term counts
        self._term_counts.update(tokens)
        
        # Update document counts (unique per doc)
        unique_tokens = set(tokens)
        self._doc_counts.update(unique_tokens)
        
        self._total_docs += 1
        
        return len(unique_tokens)
    
    def add_documents(self, documents: List[str]) -> int:
        """Add multiple documents."""
        total_terms = 0
        for doc in documents:
            total_terms += self.add_document(doc)
        return total_terms
    
    def build(self) -> Lexicon:
        """
        Build the lexicon from added documents.
        
        Returns:
            Built Lexicon instance
        """
        lexicon = Lexicon(self.name)
        
        for term, freq in self._term_counts.items():
            if freq >= self.min_frequency:
                doc_freq = self._doc_counts[term]
                lexicon.add_term(term, frequency=freq, doc_frequency=doc_freq)
        
        # Compute IDF
        lexicon.compute_idf(self._total_docs)
        
        return lexicon
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get builder statistics."""
        return {
            "total_documents": self._total_docs,
            "unique_terms": len(self._term_counts),
            "total_terms": sum(self._term_counts.values()),
            "terms_above_threshold": sum(
                1 for freq in self._term_counts.values()
                if freq >= self.min_frequency
            ),
        }
```
