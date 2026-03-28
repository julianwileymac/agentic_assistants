# requires: transformers, torch
"""Trainer with custom compute_metrics, data collator, and callbacks — synthetic sequence data."""

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
            DataCollatorWithPadding,
            Trainer,
            TrainerCallback,
            TrainingArguments,
        )
    except ImportError:
        print("Install: pip install transformers torch datasets")
        return

    model_id = "hf-internal-testing/tiny-random-bert"

    try:
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        model = AutoModelForSequenceClassification.from_pretrained(model_id, num_labels=2)
    except Exception as exc:
        print(f"Could not load model: {exc}")
        return

    rng = np.random.default_rng(1)
    n = 32
    texts = [f"doc {i} class synthetic" for i in range(n)]
    labels = (rng.random(n) > 0.5).astype(int).tolist()
    ds = Dataset.from_dict({"text": texts, "label": labels}).train_test_split(test_size=0.25, seed=0)
    train_ds, eval_ds = ds["train"], ds["test"]

    def tokenize(batch):
        return tokenizer(batch["text"], truncation=True, max_length=24)

    train_t = train_ds.map(tokenize, batched=True)
    eval_t = eval_ds.map(tokenize, batched=True)

    def compute_metrics(eval_pred):
        logits, labels_arr = eval_pred
        preds = np.argmax(logits, axis=-1)
        acc = float((preds == labels_arr).mean())
        return {"accuracy": acc}

    class LogStepCallback(TrainerCallback):
        def on_log(self, args, state, control, logs: dict[str, float] | None = None, **kwargs):
            if logs:
                loss = logs.get("loss")
                if loss is not None:
                    print(f"  [callback] step {state.global_step}: loss={loss:.6f}")

    collator = DataCollatorWithPadding(tokenizer=tokenizer)

    with tempfile.TemporaryDirectory() as tmp:
        args = TrainingArguments(
            output_dir=tmp,
            num_train_epochs=1,
            per_device_train_batch_size=8,
            per_device_eval_batch_size=8,
            logging_steps=1,
            eval_strategy="epoch",
            save_strategy="no",
            report_to=[],
        )
        trainer = Trainer(
            model=model,
            args=args,
            train_dataset=train_t,
            eval_dataset=eval_t,
            data_collator=collator,
            compute_metrics=compute_metrics,
            callbacks=[LogStepCallback()],
        )
        print("Custom Trainer run (collator + compute_metrics + callback)")
        trainer.train()
        ev = trainer.evaluate()
        print("Eval metrics:")
        for k, v in ev.items():
            if isinstance(v, float):
                print(f"  {k}: {v:.6f}")


if __name__ == "__main__":
    main()
