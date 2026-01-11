# Chunk: fccdb5c84ee6_1

- source: `src/agentic_assistants/data/corpus/lexicon.py`
- lines: 94-184
- chunk: 2/4

```
f.get_term(term)
        return entry.synonyms if entry else []
    
    def compute_idf(self, total_docs: int) -> None:
        """Compute IDF scores for all terms."""
        import math
        
        self._total_docs = total_docs
        
        for entry in self._entries.values():
            if entry.document_frequency > 0:
                idf = math.log(total_docs / entry.document_frequency)
                entry.metadata["idf"] = idf
    
    def get_top_terms(
        self,
        n: int = 100,
        by: str = "frequency",
    ) -> List[LexiconEntry]:
        """Get top N terms by frequency or IDF."""
        entries = list(self._entries.values())
        
        if by == "frequency":
            entries.sort(key=lambda x: x.frequency, reverse=True)
        elif by == "idf":
            entries.sort(key=lambda x: x.idf, reverse=True)
        elif by == "tf_idf":
            entries.sort(key=lambda x: x.frequency * x.idf, reverse=True)
        
        return entries[:n]
    
    def filter_by_frequency(
        self,
        min_freq: int = 1,
        max_freq: Optional[int] = None,
    ) -> "Lexicon":
        """Create a filtered lexicon."""
        filtered = Lexicon(f"{self.name}_filtered")
        
        for entry in self._entries.values():
            if entry.frequency >= min_freq:
                if max_freq is None or entry.frequency <= max_freq:
                    filtered._entries[entry.term] = entry
        
        filtered._total_docs = self._total_docs
        return filtered
    
    def __len__(self) -> int:
        return len(self._entries)
    
    def __iter__(self) -> Iterator[str]:
        return iter(self._entries.keys())
    
    def __contains__(self, term: str) -> bool:
        return self.contains(term)
    
    def to_vocabulary(self) -> List[str]:
        """Export as vocabulary list."""
        return sorted(self._entries.keys())
    
    def to_frequency_dict(self) -> Dict[str, int]:
        """Export as term frequency dictionary."""
        return {
            entry.term: entry.frequency
            for entry in self._entries.values()
        }
    
    def save(self, path: str) -> None:
        """Save lexicon to file."""
        data = {
            "name": self.name,
            "total_docs": self._total_docs,
            "entries": {
                term: {
                    "frequency": entry.frequency,
                    "document_frequency": entry.document_frequency,
                    "synonyms": entry.synonyms,
                    "metadata": entry.metadata,
                }
                for term, entry in self._entries.items()
            },
        }
        
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
    
    @classmethod
    def load(cls, path: str) -> "Lexicon":
        """Load lexicon from file."""
        with open(path, "r") as f:
```
