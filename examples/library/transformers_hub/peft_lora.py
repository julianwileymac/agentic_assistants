# requires: transformers peft
"""PEFT LoRA on a tiny Hub model: attach adapters, one train step, merge, save.

Uses a small random-init checkpoint so the demo is quick; shows trainable parameter
reduction versus the full base weights.
"""

from __future__ import annotations

import tempfile
from pathlib import Path


def _count_params(model) -> tuple[int, int]:
    total = sum(p.numel() for p in model.parameters())
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    return total, trainable


def main() -> None:
    try:
        import torch
        from peft import LoraConfig, TaskType, get_peft_model
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except ImportError:
        print("Install: pip install transformers peft torch")
        return

    model_id = "hf-internal-testing/tiny-random-gpt2"

    try:
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        base = AutoModelForCausalLM.from_pretrained(model_id)
    except Exception as exc:
        print(f"Could not load model: {exc}")
        return

    if tokenizer.pad_token is None and tokenizer.eos_token is not None:
        tokenizer.pad_token = tokenizer.eos_token

    lora_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=8,
        lora_alpha=16,
        lora_dropout=0.05,
        target_modules=["c_attn", "c_proj"],
        bias="none",
    )

    base_total, base_train = _count_params(base)
    model = get_peft_model(base, lora_config)
    _, peft_train = _count_params(model)

    print(f"Base model: {model_id}")
    print(f"  all parameters: {base_total:,}")
    print(f"  trainable before LoRA: {base_train:,}")
    print("LoRA config:")
    print(f"  r={lora_config.r}, lora_alpha={lora_config.lora_alpha}, target_modules={lora_config.target_modules}")
    print(f"  trainable with LoRA adapters: {peft_train:,}")
    if base_total:
        print(f"  trainable fraction: {peft_train / base_total:.4%}")

    mock_texts = [
        "mock training sentence one",
        "mock training sentence two",
    ]
    enc = tokenizer(
        mock_texts,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=32,
    )
    device = torch.device("cpu")
    model = model.to(device)
    enc = {k: v.to(device) for k, v in enc.items()}

    model.train()
    opt = torch.optim.AdamW((p for p in model.parameters() if p.requires_grad), lr=1e-3)
    opt.zero_grad()
    out = model(**enc, labels=enc["input_ids"])
    loss = out.loss
    loss.backward()
    opt.step()
    print(f"\nSingle optimization step complete; loss={loss.item():.6f}")

    merged = model.merge_and_unload()
    merged_total, merged_train = _count_params(merged)
    print("\nAfter merge_and_unload():")
    print(f"  parameters: {merged_total:,} (trainable: {merged_train:,})")

    out_dir = Path(tempfile.mkdtemp(prefix="peft_lora_demo_"))
    merged.save_pretrained(out_dir)
    tokenizer.save_pretrained(out_dir)
    print(f"\nSaved merged model + tokenizer to:\n  {out_dir.resolve()}")


if __name__ == "__main__":
    main()
