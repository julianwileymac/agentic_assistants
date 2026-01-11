# Chunk: cfce99ee7b30_1

- source: `src/agentic_assistants/indexing/chunker.py`
- lines: 91-172
- chunk: 2/5

```
amaIndex components lazily
        self._splitter = None

    def _get_splitter(self, language: Optional[str] = None):
        """Get the appropriate text splitter for the strategy."""
        from llama_index.core.node_parser import (
            SentenceSplitter,
            CodeSplitter,
            SemanticSplitterNodeParser,
        )
        
        if self.strategy == ChunkingStrategy.CODE_AWARE and language:
            # Use code splitter for programming languages
            try:
                return CodeSplitter(
                    language=language,
                    chunk_lines=40,
                    chunk_lines_overlap=5,
                    max_chars=self.chunk_size,
                )
            except Exception as e:
                logger.warning(f"Code splitter not available for {language}: {e}")
                # Fall back to sentence splitter
                return SentenceSplitter(
                    chunk_size=self.chunk_size,
                    chunk_overlap=self.chunk_overlap,
                )
        
        elif self.strategy == ChunkingStrategy.SEMANTIC:
            # Semantic splitting requires embeddings
            try:
                from llama_index.embeddings.ollama import OllamaEmbedding
                
                embed_model = OllamaEmbedding(
                    model_name=self.config.vectordb.embedding_model,
                    base_url=self.config.ollama.host,
                )
                return SemanticSplitterNodeParser(
                    buffer_size=1,
                    breakpoint_percentile_threshold=95,
                    embed_model=embed_model,
                )
            except Exception as e:
                logger.warning(f"Semantic splitter failed, falling back to sentence: {e}")
                return SentenceSplitter(
                    chunk_size=self.chunk_size,
                    chunk_overlap=self.chunk_overlap,
                )
        
        else:
            # Default to sentence splitter
            return SentenceSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
            )

    def _create_document(
        self,
        content: str,
        metadata: ChunkMetadata,
    ) -> Document:
        """Create a Document from chunk content and metadata."""
        doc_id = str(uuid.uuid4())
        
        return Document(
            id=doc_id,
            content=content,
            metadata={
                "file_path": metadata.file_path,
                "language": metadata.language,
                "start_line": metadata.start_line,
                "end_line": metadata.end_line,
                "chunk_index": metadata.chunk_index,
                "total_chunks": metadata.total_chunks,
                **metadata.extra,
            },
        )

    def chunk_text(
        self,
        text: str,
```
