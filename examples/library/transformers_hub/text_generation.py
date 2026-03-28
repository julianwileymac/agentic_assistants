# requires: transformers, torch
"""Causal LM generate(): greedy, sampling, top_k, top_p, beam — tiny GPT-2 style model."""

from __future__ import annotations


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

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model.eval()
    prompt = "The answer is"
    inputs = tokenizer(prompt, return_tensors="pt")
    max_new = 12

    def decode(gen_ids: torch.Tensor) -> str:
        return tokenizer.decode(gen_ids[0], skip_special_tokens=True)

    with torch.no_grad():
        out_greedy = model.generate(
            **inputs,
            max_new_tokens=max_new,
            do_sample=False,
            pad_token_id=tokenizer.pad_token_id,
        )
        print("Greedy:")
        print(f"  {decode(out_greedy)!r}")

        torch.manual_seed(0)
        out_sample = model.generate(
            **inputs,
            max_new_tokens=max_new,
            do_sample=True,
            temperature=0.9,
            top_k=0,
            pad_token_id=tokenizer.pad_token_id,
        )
        print("\nSampling (temperature=0.9):")
        print(f"  {decode(out_sample)!r}")

        torch.manual_seed(1)
        out_topk = model.generate(
            **inputs,
            max_new_tokens=max_new,
            do_sample=True,
            top_k=8,
            temperature=0.8,
            pad_token_id=tokenizer.pad_token_id,
        )
        print("\nTop-k sampling (k=8):")
        print(f"  {decode(out_topk)!r}")

        torch.manual_seed(2)
        out_topp = model.generate(
            **inputs,
            max_new_tokens=max_new,
            do_sample=True,
            top_p=0.85,
            top_k=0,
            temperature=0.8,
            pad_token_id=tokenizer.pad_token_id,
        )
        print("\nNucleus (top_p=0.85):")
        print(f"  {decode(out_topp)!r}")

        out_beam = model.generate(
            **inputs,
            max_new_tokens=max_new,
            num_beams=4,
            do_sample=False,
            early_stopping=True,
            pad_token_id=tokenizer.pad_token_id,
        )
        print("\nBeam search (num_beams=4):")
        print(f"  {decode(out_beam)!r}")


if __name__ == "__main__":
    main()
