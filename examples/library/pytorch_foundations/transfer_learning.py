# requires: torch, torchvision
"""Transfer learning: ResNet18, freeze backbone, replace classifier; trainable vs frozen counts."""

from __future__ import annotations


def main() -> None:
    try:
        import torch
        import torch.nn as nn
        import torchvision.models as models
    except ImportError:
        print("Install: pip install torch torchvision")
        return

    def count_by_requires_grad(module: nn.Module) -> tuple[int, int]:
        trainable = frozen = 0
        for p in module.parameters():
            n = p.numel()
            if p.requires_grad:
                trainable += n
            else:
                frozen += n
        return trainable, frozen

    # Random weights only — no pretrained download
    model = models.resnet18(weights=None)
    num_features = model.fc.in_features
    model.fc = nn.Linear(num_features, 5)

    # Freeze all layers except the new head
    for p in model.parameters():
        p.requires_grad = False
    for p in model.fc.parameters():
        p.requires_grad = True

    tr, fr = count_by_requires_grad(model)
    print("ResNet18 transfer-learning style setup (weights=None, no download)")
    print(f"Trainable parameters: {tr:,}")
    print(f"Frozen parameters:    {fr:,}")
    print(f"Classifier head: Linear({num_features}, 5)")

    model.eval()
    x = torch.randn(2, 3, 64, 64)
    with torch.no_grad():
        logits = model(x)
    print(f"Forward pass output shape: {tuple(logits.shape)}")

    print("\nPattern summary:")
    print("  1) Load backbone with pretrained weights when available (e.g. ResNet18_Weights.IMAGENET1K_V1).")
    print("  2) Replace model.fc (or add a head) for your num_classes.")
    print("  3) Freeze backbone: for p in model.parameters(): p.requires_grad = False")
    print("  4) Unfreeze head (and optionally last blocks) for fine-tuning.")


if __name__ == "__main__":
    main()
