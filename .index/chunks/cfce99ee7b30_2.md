# Chunk: cfce99ee7b30_2

- source: `src/agentic_assistants/indexing/chunker.py`
- lines: 161-253
- chunk: 3/5

```
metadata.start_line,
                "end_line": metadata.end_line,
                "chunk_index": metadata.chunk_index,
                "total_chunks": metadata.total_chunks,
                **metadata.extra,
            },
        )

    def chunk_text(
        self,
        text: str,
        metadata: Optional[dict] = None,
        language: Optional[str] = None,
    ) -> list[Document]:
        """
        Chunk a text string into documents.
        
        Args:
            text: Text to chunk
            metadata: Additional metadata for chunks
            language: Programming language (for code_aware strategy)
        
        Returns:
            List of Document objects
        """
        from llama_index.core import Document as LlamaDocument
        
        splitter = self._get_splitter(language)
        
        # Create LlamaIndex document
        llama_doc = LlamaDocument(text=text, metadata=metadata or {})
        
        # Split into nodes
        nodes = splitter.get_nodes_from_documents([llama_doc])
        
        # Convert to our Document format
        documents = []
        for i, node in enumerate(nodes):
            chunk_meta = ChunkMetadata(
                file_path=metadata.get("file_path", "") if metadata else "",
                language=language,
                start_line=node.metadata.get("start_line", 0) if hasattr(node, "metadata") else 0,
                end_line=node.metadata.get("end_line", 0) if hasattr(node, "metadata") else 0,
                chunk_index=i,
                total_chunks=len(nodes),
                extra=metadata or {},
            )
            
            documents.append(self._create_document(node.text, chunk_meta))
        
        return documents

    def chunk_file(
        self,
        path: Union[str, Path],
        additional_metadata: Optional[dict] = None,
    ) -> list[Document]:
        """
        Chunk a file into documents.
        
        Args:
            path: Path to the file
            additional_metadata: Additional metadata to include
        
        Returns:
            List of Document objects
        """
        loaded = self.file_loader.load_file(path)
        if loaded is None:
            return []
        
        return self.chunk_loaded_file(loaded, additional_metadata)

    def chunk_loaded_file(
        self,
        loaded_file: LoadedFile,
        additional_metadata: Optional[dict] = None,
    ) -> list[Document]:
        """
        Chunk a LoadedFile into documents.
        
        Args:
            loaded_file: LoadedFile instance
            additional_metadata: Additional metadata to include
        
        Returns:
            List of Document objects
        """
        metadata = {
            "file_path": str(loaded_file.path),
            "file_name": loaded_file.name,
            "extension": loaded_file.extension,
```
