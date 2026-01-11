# Chunk: fccdb5c84ee6_2

- source: `src/agentic_assistants/data/corpus/lexicon.py`
- lines: 173-263
- chunk: 3/4

```
for term, entry in self._entries.items()
            },
        }
        
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
    
    @classmethod
    def load(cls, path: str) -> "Lexicon":
        """Load lexicon from file."""
        with open(path, "r") as f:
            data = json.load(f)
        
        lexicon = cls(data.get("name", "loaded"))
        lexicon._total_docs = data.get("total_docs", 0)
        
        for term, entry_data in data.get("entries", {}).items():
            entry = LexiconEntry(
                term=term,
                frequency=entry_data.get("frequency", 0),
                document_frequency=entry_data.get("document_frequency", 0),
                synonyms=entry_data.get("synonyms", []),
                metadata=entry_data.get("metadata", {}),
            )
            lexicon._entries[term] = entry
        
        return lexicon


class LexiconBuilder:
    """
    Build a lexicon from text corpus.
    """
    
    # Common stop words
    STOP_WORDS: Set[str] = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
        "being", "have", "has", "had", "do", "does", "did", "will", "would",
        "could", "should", "may", "might", "must", "shall", "can", "need",
        "this", "that", "these", "those", "it", "its",
    }
    
    def __init__(
        self,
        name: str = "corpus_lexicon",
        min_term_length: int = 2,
        lowercase: bool = True,
        remove_stopwords: bool = True,
        min_frequency: int = 2,
    ):
        """
        Initialize lexicon builder.
        
        Args:
            name: Name for the resulting lexicon
            min_term_length: Minimum term length
            lowercase: Convert to lowercase
            remove_stopwords: Filter stop words
            min_frequency: Minimum term frequency
        """
        self.name = name
        self.min_term_length = min_term_length
        self.lowercase = lowercase
        self.remove_stopwords = remove_stopwords
        self.min_frequency = min_frequency
        
        self._term_counts: Counter = Counter()
        self._doc_counts: Counter = Counter()
        self._total_docs = 0
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into terms."""
        # Basic tokenization
        tokens = re.findall(r'\b\w+\b', text)
        
        if self.lowercase:
            tokens = [t.lower() for t in tokens]
        
        # Filter by length
        tokens = [t for t in tokens if len(t) >= self.min_term_length]
        
        # Remove stop words
        if self.remove_stopwords:
            tokens = [t for t in tokens if t not in self.STOP_WORDS]
        
        return tokens
    
    def add_document(self, text: str) -> int:
        """
```
