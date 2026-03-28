"""Synthetic QA pair generation from plain text: chunking, prompts, Alpaca SFT rows.

Uses short in-memory documents and rule-based "answers" so the script runs without an LLM.
The prompt templates match what you would send to a model for real QA generation.
"""

# requires: unsloth

from __future__ import annotations

import re
import textwrap
from typing import Iterator


def chunk_by_paragraphs(text: str, max_chars: int = 280) -> list[str]:
    """Split on blank lines, then merge pieces until max_chars (simple chunking)."""
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks: list[str] = []
    buf: list[str] = []
    size = 0
    for p in paras:
        if size + len(p) > max_chars and buf:
            chunks.append("\n\n".join(buf))
            buf = [p]
            size = len(p)
        else:
            buf.append(p)
            size += len(p) + 2
    if buf:
        chunks.append("\n\n".join(buf))
    return chunks


QA_GENERATION_PROMPT = textwrap.dedent(
    """\
    You are generating training data. Given the passage below, write ONE factual question
    and a short answer that can be verified from the passage only.

    Passage:
    ---
    {chunk}
    ---

    Respond in this exact format:
    Question: <question>
    Answer: <answer>
    """
)


def fake_llm_generate_qa(chunk: str) -> tuple[str, str]:
    """Stub: derive a trivial QA pair from the first sentence (replace with API call in production)."""
    first = chunk.split(".")[0].strip() + ("." if "." not in chunk[:200] else "")
    question = "What is this passage mainly about?"
    answer = first[:200]
    return question, answer


def to_alpaca_row(instruction: str, inp: str, output: str) -> dict[str, str]:
    """Alpaca-style columns for HF datasets / SFTTrainer.dataset_text_field formatting."""
    return {"instruction": instruction, "input": inp, "output": output}


def iter_sft_text_rows(alpaca_rows: list[dict[str, str]], eos_token: str = "</s>") -> Iterator[dict[str, str]]:
    """Expand Alpaca dicts into a single `text` field (same pattern as sft_training.py)."""
    for row in alpaca_rows:
        instruction = row["instruction"].strip()
        input_text = row["input"].strip()
        output = row["output"].strip()
        if input_text:
            prompt = (
                "Below is an instruction that describes a task, paired with an input that provides "
                "further context. Write a response that appropriately completes the request.\n\n"
                f"### Instruction:\n{instruction}\n\n### Input:\n{input_text}\n\n### Response:\n"
            )
        else:
            prompt = (
                "Below is an instruction that describes a task. Write a response that appropriately "
                f"completes the request.\n\n### Instruction:\n{instruction}\n\n### Response:\n"
            )
        yield {"text": prompt + output + eos_token}


def main() -> None:
    try:
        from unsloth import FastLanguageModel  # noqa: F401
    except ImportError:
        print(
            "Install: pip install unsloth\n"
            "(Listed in # requires for this folder; chunking and Alpaca rows below run without it.)"
        )

    document_a = textwrap.dedent(
        """\
        The Orion capsule uses a heat shield and parachutes for re-entry.
        NASA tests abort systems to protect crew during launch anomalies.

        Artemis missions aim to return humans to the lunar surface.
        """
    )
    document_b = "Machine learning models need clean data. Evaluation uses held-out test sets."

    all_chunks: list[str] = []
    for doc in (document_a, document_b):
        all_chunks.extend(chunk_by_paragraphs(doc, max_chars=220))

    print("=== Chunks ===")
    for i, c in enumerate(all_chunks):
        print(f"\n--- chunk {i} ---\n{c}\n")

    print("=== QA generation prompt template (fill {chunk}) ===\n")
    print(QA_GENERATION_PROMPT.format(chunk="<your chunk here>"))

    alpaca_rows: list[dict[str, str]] = []
    for chunk in all_chunks:
        q, a = fake_llm_generate_qa(chunk)
        user_prompt = QA_GENERATION_PROMPT.format(chunk=chunk)
        alpaca_rows.append(
            to_alpaca_row(
                instruction="Answer the question using only the passage in the input.",
                inp=user_prompt,
                output=f"Question: {q}\nAnswer: {a}",
            )
        )

    print("\n=== Alpaca-format dataset rows (instruction / input / output) ===")
    for row in alpaca_rows:
        print(row)

    print("\n=== SFT `text` field examples (eos_token shown as </s>) ===")
    for item in list(iter_sft_text_rows(alpaca_rows, eos_token="</s>"))[:2]:
        print(textwrap.shorten(item["text"], width=500, placeholder="..."))


if __name__ == "__main__":
    main()
