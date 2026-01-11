# Chunk: fccdb5c84ee6_0

- source: `src/agentic_assistants/data/corpus/lexicon.py`
- lines: 1-104
- chunk: 1/4

```
"""
Lexicon building and management.
"""

import json
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Set


@dataclass
class LexiconEntry:
    """A single lexicon entry."""
    
    term: str
    frequency: int = 0
    document_frequency: int = 0
    pos_tags: List[str] = field(default_factory=list)
    synonyms: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def idf(self) -> float:
        """Inverse document frequency (requires total docs)."""
        return self.metadata.get("idf", 0.0)


class Lexicon:
    """
    Domain-specific lexicon/vocabulary.
    
    Provides:
    - Term frequency statistics
    - IDF computation
    - Synonym management
    - Export for model training
    """
    
    def __init__(self, name: str = "default"):
        """
        Initialize lexicon.
        
        Args:
            name: Lexicon name
        """
        self.name = name
        self._entries: Dict[str, LexiconEntry] = {}
        self._total_docs = 0
    
    def add_term(
        self,
        term: str,
        frequency: int = 1,
        doc_frequency: int = 1,
    ) -> LexiconEntry:
        """Add or update a term in the lexicon."""
        term_lower = term.lower()
        
        if term_lower in self._entries:
            entry = self._entries[term_lower]
            entry.frequency += frequency
            entry.document_frequency = max(entry.document_frequency, doc_frequency)
        else:
            entry = LexiconEntry(
                term=term_lower,
                frequency=frequency,
                document_frequency=doc_frequency,
            )
            self._entries[term_lower] = entry
        
        return entry
    
    def get_term(self, term: str) -> Optional[LexiconEntry]:
        """Get a term entry."""
        return self._entries.get(term.lower())
    
    def contains(self, term: str) -> bool:
        """Check if term is in lexicon."""
        return term.lower() in self._entries
    
    def add_synonym(self, term: str, synonym: str) -> bool:
        """Add a synonym for a term."""
        entry = self.get_term(term)
        if entry:
            if synonym.lower() not in entry.synonyms:
                entry.synonyms.append(synonym.lower())
            return True
        return False
    
    def get_synonyms(self, term: str) -> List[str]:
        """Get synonyms for a term."""
        entry = self.get_term(term)
        return entry.synonyms if entry else []
    
    def compute_idf(self, total_docs: int) -> None:
        """Compute IDF scores for all terms."""
        import math
        
        self._total_docs = total_docs
        
        for entry in self._entries.values():
```
