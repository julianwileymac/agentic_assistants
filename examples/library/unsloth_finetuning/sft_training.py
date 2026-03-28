"""Supervised fine-tuning setup with Unsloth + TRL: Alpaca and ChatML formatting.

Builds SFTTrainer, TrainingArguments, and dataset formatting functions.
Does not call trainer.train() so no long GPU run is started from this script.
"""

# requires: unsloth

from __future__ import annotations

from typing import Any


def _alpaca_format(example: dict[str, str]) -> dict[str, str]:
    """Map dataset columns instruction/input/output -> single text field."""
    instruction = example.get("instruction", "").strip()
    input_text = example.get("input", "").strip()
    output = example.get("output", "").strip()
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
    text = prompt + output + tokenizer.eos_token  # noqa: F821 — set in main after tokenizer load
    return {"text": text}


def _chatml_format(example: dict[str, str]) -> dict[str, str]:
    """ChatML-style single-string example (model-specific tokens may differ)."""
    user = example.get("instruction", "").strip()
    assistant = example.get("output", "").strip()
    text = (
        "<|im_start|>user\n"
        + user
        + f"{tokenizer.eos_token}\n"  # noqa: F821
        + "<|im_start|>assistant\n"
        + assistant
        + f"{tokenizer.eos_token}\n"
    )
    return {"text": text}


def main() -> None:
    try:
        from datasets import Dataset
        from transformers import TrainingArguments
        from trl import SFTTrainer
        from unsloth import FastLanguageModel
    except ImportError as exc:
        print(
            "Missing dependency. Typical install:\n"
            "  pip install unsloth datasets transformers trl\n\n"
            f"ImportError: {exc}"
        )
        return

    global tokenizer  # used by formatters for eos_token
    max_seq_length = 512
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name="unsloth/tinyllama-bnb-4bit",
        max_seq_length=max_seq_length,
        dtype=None,
        load_in_4bit=True,
    )
    model = FastLanguageModel.get_peft_model(
        model,
        r=16,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        lora_alpha=16,
        lora_dropout=0.0,
        bias="none",
        use_gradient_checkpointing="unsloth",
    )

    rows: list[dict[str, Any]] = [
        {
            "instruction": "Summarize the following in one sentence.",
            "input": "The cat sat on the mat.",
            "output": "A cat rested on a mat.",
        },
        {
            "instruction": "What is 2+2?",
            "input": "",
            "output": "4",
        },
    ]
    raw_ds = Dataset.from_list(rows)

    def alpaca_row(ex: dict[str, str]) -> dict[str, str]:
        instruction = ex.get("instruction", "").strip()
        input_text = ex.get("input", "").strip()
        output = ex.get("output", "").strip()
        eos = tokenizer.eos_token or ""
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
        return {"text": prompt + output + eos}

    def chatml_row(ex: dict[str, str]) -> dict[str, str]:
        user = ex.get("instruction", "").strip()
        assistant = ex.get("output", "").strip()
        eos = tokenizer.eos_token or ""
        text = (
            "<|im_start|>user\n"
            + user
            + eos
            + "\n<|im_start|>assistant\n"
            + assistant
            + eos
            + "\n"
        )
        return {"text": text}

    alpaca_ds = raw_ds.map(alpaca_row, remove_columns=raw_ds.column_names)
    chatml_ds = raw_ds.map(chatml_row, remove_columns=raw_ds.column_names)

    training_args = TrainingArguments(
        per_device_train_batch_size=1,
        gradient_accumulation_steps=2,
        warmup_steps=1,
        max_steps=3,
        learning_rate=2e-4,
        fp16=not hasattr(__import__("torch"), "float8_e4m3fn"),
        logging_steps=1,
        output_dir="outputs/sft_unsloth_demo",
        optim="adamw_8bit",
        weight_decay=0.01,
        lr_scheduler_type="linear",
        seed=3407,
        report_to="none",
    )

    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=alpaca_ds,
        dataset_text_field="text",
        max_seq_length=max_seq_length,
        args=training_args,
    )

    print("=== SFTTrainer constructed (train() not called) ===")
    print(f"  train_dataset size: {len(trainer.train_dataset)}")
    print(f"  max_seq_length: {max_seq_length}")
    print("\n--- Sample Alpaca-formatted row ---")
    print(alpaca_ds[0]["text"][:400], "...\n" if len(alpaca_ds[0]["text"]) > 400 else "\n")
    print("--- Sample ChatML-formatted row ---")
    print(chatml_ds[0]["text"][:400], "...\n" if len(chatml_ds[0]["text"]) > 400 else "\n")
    print("--- TrainingArguments (subset) ---")
    print(f"  output_dir: {training_args.output_dir}")
    print(f"  per_device_train_batch_size: {training_args.per_device_train_batch_size}")
    print(f"  max_steps: {training_args.max_steps}")
    print(f"  learning_rate: {training_args.learning_rate}")
    print("\nTo run training: trainer.train()")
    print("For HuggingFace Hub data: datasets.load_dataset('tatsu-lab/alpaca') or your JSON/CSV.")


if __name__ == "__main__":
    # Silence unused top-level formatters (documentation-only signatures).
    _ = (_alpaca_format, _chatml_format)
    main()
