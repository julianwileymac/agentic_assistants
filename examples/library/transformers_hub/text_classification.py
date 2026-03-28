# requires: transformers, torch, datasets
"""Fine-tune a tiny BERT on a synthetic binary dataset: Trainer + 1 epoch + eval."""

from __future__ import annotations

import tempfile


def main() -> None:
    try:
        import numpy as np
        import torch
        from datasets import Dataset
        from transformers import (
            AutoModelForSequenceClassification,
            AutoTokenizer,
            Trainer,
            TrainingArguments,
        )
    except ImportError:
        print("Install: pip install transformers torch datasets")
        return

    model_id = "hf-internal-testing/tiny-random-bert"
    rng = np.random.default_rng(0)

    try:
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        model = AutoModelForSequenceClassification.from_pretrained(model_id, num_labels=2)
    except Exception as exc:
        print(f"Could not load model: {exc}")
        return

    n = 48
    texts_pos = [f"synthetic ok review number {i}" for i in range(n // 2)]
    texts_neg = [f"synthetic bad review number {i}" for i in range(n // 2)]
    labels = [1] * (n // 2) + [0] * (n // 2)
    texts = texts_pos + texts_neg
    order = rng.permutation(n)
    texts = [texts[i] for i in order]
    labels = [labels[i] for i in order]

    raw = {"text": texts, "labels": labels}
    ds = Dataset.from_dict(raw).train_test_split(test_size=0.25, seed=42)
    train_ds, eval_ds = ds["train"], ds["test"]

    def tokenize(batch):
        return tokenizer(batch["text"], truncation=True, padding="max_length", max_length=32)

    train_t = train_ds.map(tokenize, batched=True)
    eval_t = eval_ds.map(tokenize, batched=True)
    train_t.set_format(type="torch", columns=["input_ids", "attention_mask", "labels"])
    eval_t.set_format(type="torch", columns=["input_ids", "attention_mask", "labels"])

    with tempfile.TemporaryDirectory() as tmp:
        ta_kwargs = dict(
            output_dir=tmp,
            num_train_epochs=1,
            per_device_train_batch_size=8,
            per_device_eval_batch_size=8,
            logging_steps=10,
            save_strategy="no",
            report_to=[],
        )
        try:
            args = TrainingArguments(eval_strategy="epoch", **ta_kwargs)
        except TypeError:
            args = TrainingArguments(evaluation_strategy="epoch", **ta_kwargs)
        trainer = Trainer(
            model=model,
            args=args,
            train_dataset=train_t,
            eval_dataset=eval_t,
        )
        print("Training 1 epoch on synthetic text (tiny-random-bert)...")
        train_out = trainer.train()
        print(f"  training loss (logged): {train_out.training_loss:.6f}")

        metrics = trainer.evaluate()
        print("Evaluation on held-out synthetic split:")
        for k in sorted(metrics):
            if isinstance(metrics[k], float):
                print(f"  {k}: {metrics[k]:.6f}")


if __name__ == "__main__":
    main()
