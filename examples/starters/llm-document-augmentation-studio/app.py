"""LLM document augmentation studio starter."""

import httpx

from agentic_assistants.data.rag.augmenters import QAGenerationAugmenter, SummaryAugmenter
from agentic_assistants.data.rag.chunkers import TextChunker


def _llm(prompt: str) -> str:
    response = httpx.post(
        "http://localhost:11434/api/generate",
        json={"model": "llama3.2", "prompt": prompt, "stream": False},
        timeout=60.0,
    )
    response.raise_for_status()
    return response.json().get("response", "")


def main() -> None:
    chunk = TextChunker(chunk_size=200, chunk_overlap=0).chunk(
        "LLM augmentation can add summaries and query variants to improve retrieval."
    )[0]
    chunk = SummaryAugmenter(use_llm=True, llm_fn=_llm).augment(chunk, {})
    chunk = QAGenerationAugmenter(num_questions=3, llm_fn=_llm).augment(chunk, {})
    print(chunk.to_dict())


if __name__ == "__main__":
    main()

