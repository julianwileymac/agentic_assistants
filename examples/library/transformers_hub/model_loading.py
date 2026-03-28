# requires: transformers, torch
"""AutoTokenizer / AutoModel loading, sequence classification head, pipeline (tiny Hub models)."""

from __future__ import annotations


def main() -> None:
    try:
        import torch
        from transformers import (
            AutoConfig,
            AutoModel,
            AutoModelForSequenceClassification,
            AutoTokenizer,
            pipeline,
        )
    except ImportError:
        print("Install: pip install transformers torch")
        return

    model_id = "hf-internal-testing/tiny-random-bert"

    print(f"Loading tokenizer and models from: {model_id}")
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        config = AutoConfig.from_pretrained(model_id)
        base = AutoModel.from_pretrained(model_id)
        clf = AutoModelForSequenceClassification.from_pretrained(model_id, num_labels=2)
    except Exception as exc:
        print(f"Could not download or load model (offline or network): {exc}")
        print("Expected: Hugging Face Hub access for this tiny test checkpoint.")
        return

    print("\nTokenizer")
    print(f"  vocab_size: {tokenizer.vocab_size}")
    print(f"  model_max_length: {getattr(tokenizer, 'model_max_length', 'n/a')}")
    print(f"  special tokens map: {dict(list(tokenizer.special_tokens_map.items())[:4])} ...")

    print("\nConfig (subset)")
    for k in ("model_type", "hidden_size", "num_hidden_layers", "num_attention_heads"):
        if hasattr(config, k):
            print(f"  {k}: {getattr(config, k)}")

    text = "This is a short synthetic example sentence."
    enc = tokenizer(text, return_tensors="pt")
    with torch.no_grad():
        out_base = base(**enc)
        out_clf = clf(**enc)
    print("\nForward passes")
    print(f"  base last_hidden_state shape: {tuple(out_base.last_hidden_state.shape)}")
    print(f"  clf logits shape: {tuple(out_clf.logits.shape)}")

    print("\nPipeline (sentiment-style classification on tiny random weights)")
    try:
        clf_pipe = pipeline(
            "text-classification",
            model=clf,
            tokenizer=tokenizer,
            top_k=None,
        )
        result = clf_pipe("positive vibes only")[0]
        print(f"  pipeline output (first item): {result}")
    except Exception as exc:
        print(f"  pipeline setup failed: {exc}")


if __name__ == "__main__":
    main()
