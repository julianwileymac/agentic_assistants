"""Unsloth QLoRA setup: FastLanguageModel.from_pretrained and get_peft_model patterns.

This module documents 4-bit loading and LoRA hyperparameters (r, alpha, target_modules)
without running training or downloading weights unless you opt in.
"""

# requires: unsloth

from __future__ import annotations

import json
from typing import Any


def _print_api_reference() -> None:
    """Static reference for readers without Unsloth installed."""
    print(
        """
=== FastLanguageModel.from_pretrained (typical kwargs) ===
  model_name: str          # e.g. "unsloth/Meta-Llama-3.1-8B-bnb-4bit"
  max_seq_length: int      # context length cap used by Unsloth optimizations
  dtype: Optional[type]    # often None (auto) or torch.float16 / bfloat16
  load_in_4bit: bool       # True for NF4 4-bit base weights (QLoRA)

=== FastLanguageModel.get_peft_model (typical LoRA / QLoRA kwargs) ===
  r: int                   # LoRA rank (e.g. 16)
  lora_alpha: int          # scaling (often equal to r, e.g. 16)
  lora_dropout: float      # e.g. 0.0
  target_modules: list[str] # attention/MLP projection layers to adapt
  bias: str                # usually "none"
  use_gradient_checkpointing: str | bool  # "unsloth" enables Unsloth's variant
  random_state: int
  use_rslora: bool
  loftq_config: Any | None

Common Llama/Mistral-style target_modules:
  ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
"""
    )


def _demo_config_dicts() -> dict[str, Any]:
    from_pretrained: dict[str, Any] = {
        "model_name": "unsloth/Meta-Llama-3.1-8B-bnb-4bit",
        "max_seq_length": 2048,
        "dtype": None,
        "load_in_4bit": True,
    }
    lora: dict[str, Any] = {
        "r": 16,
        "lora_alpha": 16,
        "lora_dropout": 0.0,
        "target_modules": [
            "q_proj",
            "k_proj",
            "v_proj",
            "o_proj",
            "gate_proj",
            "up_proj",
            "down_proj",
        ],
        "bias": "none",
        "use_gradient_checkpointing": "unsloth",
        "random_state": 3407,
        "use_rslora": False,
        "loftq_config": None,
    }
    return {"from_pretrained": from_pretrained, "get_peft_model": lora}


def main() -> None:
    _print_api_reference()
    configs = _demo_config_dicts()
    print("\n=== Serializable demo configs (no weights loaded) ===")
    print(json.dumps(configs, indent=2))

    try:
        import torch
        from unsloth import FastLanguageModel
    except ImportError:
        print(
            "\nInstall stack (GPU recommended): pip install unsloth\n"
            "Then you can run from_pretrained + get_peft_model as below.\n"
        )
        return

    print("\n=== Live import check ===")
    print(f"torch.cuda.is_available(): {torch.cuda.is_available()}")
    print(f"FastLanguageModel: {FastLanguageModel}")

    print(
        "\nTo load weights (downloads large checkpoints), run in your own script:\n"
        "  model, tokenizer = FastLanguageModel.from_pretrained(**from_pretrained_kwargs)\n"
        "  model = FastLanguageModel.get_peft_model(model, **lora_kwargs)\n"
        "  trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)\n"
        "  all_params = sum(p.numel() for p in model.parameters())\n"
        "  print(trainable_params, all_params)\n"
    )


if __name__ == "__main__":
    main()
