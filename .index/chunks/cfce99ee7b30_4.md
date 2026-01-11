# Chunk: cfce99ee7b30_4

- source: `src/agentic_assistants/indexing/chunker.py`
- lines: 334-399
- chunk: 5/5

```
    """
        Initialize the simple chunker.
        
        Args:
            chunk_size: Target chunk size in characters
            chunk_overlap: Overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_text(
        self,
        text: str,
        metadata: Optional[dict] = None,
    ) -> list[Document]:
        """
        Chunk text using simple character-based splitting.
        
        Args:
            text: Text to chunk
            metadata: Metadata for chunks
        
        Returns:
            List of Document objects
        """
        if not text:
            return []
        
        chunks = []
        start = 0
        chunk_index = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # Try to break at a newline if possible
            if end < len(text):
                newline_pos = text.rfind("\n", start + self.chunk_size // 2, end)
                if newline_pos > start:
                    end = newline_pos + 1
            
            chunk_text = text[start:end].strip()
            
            if chunk_text:
                doc = Document(
                    id=str(uuid.uuid4()),
                    content=chunk_text,
                    metadata={
                        **(metadata or {}),
                        "chunk_index": chunk_index,
                        "start_char": start,
                        "end_char": end,
                    },
                )
                chunks.append(doc)
                chunk_index += 1
            
            start = end - self.chunk_overlap
        
        # Update total chunks
        for doc in chunks:
            doc.metadata["total_chunks"] = len(chunks)
        
        return chunks

```
