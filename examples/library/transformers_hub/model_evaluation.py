# requires: transformers
"""Tiny-model evaluation patterns: perplexity, timing, MMLU-style MC scoring, size stats.

Illustrates measurement utilities on a Hub smoke-test checkpoint (random weights).
"""

from __future__ import annotations

import math
import time
from typing import Any


def _param_stats(model) -> dict[str, Any]:
    params = list(model.parameters())
    n_tensors = len(params)
    total = sum(p.numel() for p in params)
    trainable = sum(p.numel() for p in params if p.requires_grad)
    bytes_fp32 = total * 4
    return {
        "tensor_count": n_tensors,
        "total_params": total,
        "trainable_params": trainable,
        "approx_size_fp32_mb": bytes_fp32 / (1024 * 1024),
    }


def _perplexity_from_loss(loss: float) -> float:
    return float(math.exp(loss))


def _choice_score(
    model,
    tokenizer,
    device,
    stem: str,
    choice: str,
) -> float:
    """Higher is better: negative CE on the full concatenated prompt (conceptual MC)."""
    try:
        import torch
    except ImportError:
        raise RuntimeError("torch required for scoring") from None

    text = f"{stem}\nAnswer: {choice}"
    enc = tokenizer(text, return_tensors="pt", truncation=True, max_length=64)
    enc = {k: v.to(device) for k, v in enc.items()}
    with torch.no_grad():
        out = model(**enc, labels=enc["input_ids"])
    return float(-out.loss.item())


def main() -> None:
    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except ImportError:
        print("Install: pip install transformers torch")
        return

    model_id = "hf-internal-testing/tiny-random-gpt2"

    try:
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        model = AutoModelForCausalLM.from_pretrained(model_id)
    except Exception as exc:
        print(f"Could not load model: {exc}")
        return

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)
    model.eval()

    stats = _param_stats(model)
    print(f"Model: {model_id}")
    print(f"  tensors: {stats['tensor_count']}")
    print(f"  total parameters: {stats['total_params']:,}")
    print(f"  trainable parameters: {stats['trainable_params']:,}")
    print(f"  ~FP32 size (theoretical): {stats['approx_size_fp32_mb']:.4f} MiB")

    eval_texts = [
        "The quick brown fox jumps over the lazy dog.",
        "Tiny random weights are only useful for pipeline tests.",
    ]
    enc = tokenizer(
        eval_texts,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=48,
    )
    enc = {k: v.to(device) for k, v in enc.items()}

    with torch.no_grad():
        out = model(**enc, labels=enc["input_ids"])
    ppl = _perplexity_from_loss(float(out.loss.item()))
    print(f"\nPerplexity (exp(cross-entropy) on batch): {ppl:.4f}")

    torch.cuda.synchronize(device) if device.type == "cuda" else None
    t0 = time.perf_counter()
    n_runs = 20
    with torch.no_grad():
        for _ in range(n_runs):
            _ = model(**enc, labels=enc["input_ids"])
    torch.cuda.synchronize(device) if device.type == "cuda" else None
    elapsed = time.perf_counter() - t0
    print(
        f"\nInference timing: {n_runs} forward passes in {elapsed * 1000:.3f} ms "
        f"({elapsed / n_runs * 1000:.3f} ms / pass) on {device.type}"
    )

    print("\nMMLU-style multiple choice (conceptual; random model scores are meaningless):")
    mmlu_style = [
        {
            "question": "What is 2 + 2?",
            "choices": ["3", "4", "5", "22"],
            "gold_index": 1,
        },
        {
            "question": "Which planet is closest to the Sun?",
            "choices": ["Venus", "Mercury", "Earth", "Mars"],
            "gold_index": 1,
        },
    ]
    for item in mmlu_style:
        scores = [
            _choice_score(model, tokenizer, device, item["question"], c)
            for c in item["choices"]
        ]
        pred = int(max(range(len(scores)), key=lambda i: scores[i]))
        print(f"  Q: {item['question']}")
        print(f"    scores: {[round(s, 4) for s in scores]}")
        print(f"    predicted index: {pred} (gold: {item['gold_index']})")


if __name__ == "__main__":
    main()
