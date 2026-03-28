"""GGUF export, LoRA merge, and Ollama deployment: CLI and HTTP API patterns.

Documents Unsloth/llama.cpp export flows and how to register a model with Ollama.
This script does not run conversion binaries unless you execute the printed commands yourself.
"""

# requires: unsloth

from __future__ import annotations

import textwrap


def main() -> None:
    try:
        from unsloth import FastLanguageModel  # noqa: F401
    except ImportError:
        print("Install: pip install unsloth (for in-process export helpers in your own projects).")
    print(
        textwrap.dedent(
            """\
            === 1) Save merged 16-bit (or float) weights after training ===
            In your training script, after LoRA adaptation:

              model.save_pretrained_merged("merged_model", save_method="merged_16bit")
              tokenizer.save_pretrained("merged_model")

            Other save_method values often documented by Unsloth include "merged_4bit"
            (depends on your Unsloth version — check current docs).

            === 2) Export to GGUF (llama.cpp compatible) ===
            Unsloth typically exposes a helper on the model, e.g.:

              model.save_pretrained_gguf("model_gguf", tokenizer, quantization_method="q4_k_m")

            CLI alternative (if you use llama.cpp converters outside Python):

              python convert_hf_to_gguf.py --outfile model.gguf merged_model/

            (Exact script path/name follows the llama.cpp revision you installed.)

            === 3) Ollama: create a Modelfile and build ===
            Place your .gguf next to a Modelfile containing:

              FROM ./your_model.Q4_K_M.gguf
              PARAMETER temperature 0.7

            Then:

              ollama create my-lora-merged -f Modelfile

            Run:

              ollama run my-lora-merged "Hello from local GGUF"

            === 4) Ollama HTTP API (local default base) ===
            List models:

              curl http://localhost:11434/api/tags

            Chat completion (OpenAI-compatible):

              curl http://localhost:11434/v1/chat/completions \\
                -H "Content-Type: application/json" \\
                -d "{\\"model\\": \\"my-lora-merged\\", \\"messages\\": [{\\"role\\": \\"user\\", \\"content\\": \\"Hi\\"}]}"

            Native generate API:

              curl http://localhost:11434/api/generate \\
                -d '{\\"model\\": \\"my-lora-merged\\", \\"prompt\\": \\"Why is the sky blue?\\", \\"stream\\": false}'
            """
        )
    )


if __name__ == "__main__":
    main()
