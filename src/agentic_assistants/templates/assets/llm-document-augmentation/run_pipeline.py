"""LLM document augmentation example."""

import httpx

from agentic_assistants.data.rag.augmenters import (
    ChainedAugmenter,
    MetadataAugmenter,
    QAGenerationAugmenter,
    SummaryAugmenter,
)
from agentic_assistants.data.rag.chunkers import Chunk, TextChunker


def _llm(prompt: str) -> str:
    response = httpx.post(
        "http://localhost:11434/api/generate",
        json={"model": "llama3.2", "prompt": prompt, "stream": False},
        timeout=60.0,
    )
    response.raise_for_status()
    return response.json().get("response", "")


def main() -> None:
    text = (
        "Document augmentation enriches chunks with metadata, summaries, and generated "
        "question variants so retrieval can match user intent more effectively."
    )
    chunks = TextChunker(chunk_size=120, chunk_overlap=20).chunk(
        text,
        metadata={"source": "inline"},
    )
    augmenter = ChainedAugmenter(
        [
            MetadataAugmenter(),
            SummaryAugmenter(use_llm=True, llm_fn=_llm, max_length=140),
            QAGenerationAugmenter(num_questions=3, llm_fn=_llm),
        ]
    )

    enriched = []
    for c in chunks:
        enriched.append(augmenter.augment(c, {"source": "inline", "source_type": "text"}))

    print("Augmented chunks:")
    for item in enriched:
        item = item if isinstance(item, Chunk) else item
        print(item.to_dict())


if __name__ == "__main__":
    main()

