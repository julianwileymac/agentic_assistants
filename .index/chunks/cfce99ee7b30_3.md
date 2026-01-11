# Chunk: cfce99ee7b30_3

- source: `src/agentic_assistants/indexing/chunker.py`
- lines: 244-345
- chunk: 4/5

```
    additional_metadata: Additional metadata to include
        
        Returns:
            List of Document objects
        """
        metadata = {
            "file_path": str(loaded_file.path),
            "file_name": loaded_file.name,
            "extension": loaded_file.extension,
            "size_bytes": loaded_file.size_bytes,
        }
        if additional_metadata:
            metadata.update(additional_metadata)
        
        return self.chunk_text(
            loaded_file.content,
            metadata=metadata,
            language=loaded_file.language,
        )

    def chunk_directory(
        self,
        directory: Union[str, Path],
        patterns: Optional[list[str]] = None,
        recursive: bool = True,
        additional_metadata: Optional[dict] = None,
    ) -> list[Document]:
        """
        Chunk all files in a directory.
        
        Args:
            directory: Directory path
            patterns: File patterns to include (e.g., ["*.py"])
            recursive: Whether to recurse into subdirectories
            additional_metadata: Additional metadata to include
        
        Returns:
            List of Document objects
        """
        files = self.file_loader.load_directory(
            directory,
            patterns=patterns,
            recursive=recursive,
        )
        
        all_documents = []
        for loaded_file in files:
            documents = self.chunk_loaded_file(loaded_file, additional_metadata)
            all_documents.extend(documents)
        
        logger.info(f"Created {len(all_documents)} chunks from {len(files)} files")
        return all_documents

    def estimate_chunks(
        self,
        text: str,
        language: Optional[str] = None,
    ) -> int:
        """
        Estimate the number of chunks for a text.
        
        Args:
            text: Text to estimate
            language: Programming language
        
        Returns:
            Estimated number of chunks
        """
        # Simple estimation based on chunk size
        text_length = len(text)
        effective_chunk_size = self.chunk_size - self.chunk_overlap
        
        if effective_chunk_size <= 0:
            return 1
        
        return max(1, (text_length + effective_chunk_size - 1) // effective_chunk_size)


class SimpleChunker:
    """
    Simple text chunker without LlamaIndex dependency.
    
    Use this when LlamaIndex is not available or for simple use cases.
    """

    def __init__(
        self,
        chunk_size: int = 1024,
        chunk_overlap: int = 128,
    ):
        """
        Initialize the simple chunker.
        
        Args:
            chunk_size: Target chunk size in characters
            chunk_overlap: Overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_text(
```
