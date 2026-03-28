# requires: torch
"""Device selection (CPU/CUDA), model.to(device), DataParallel usage pattern."""

from __future__ import annotations


def main() -> None:
    try:
        import torch
        import torch.nn as nn
    except ImportError:
        print("Install: pip install torch")
        return

    cuda_available = torch.cuda.is_available()
    device = torch.device("cuda" if cuda_available else "cpu")

    print("Device info")
    print(f"  torch.cuda.is_available(): {cuda_available}")
    print(f"  Selected device: {device}")
    if cuda_available:
        print(f"  torch.cuda.device_count(): {torch.cuda.device_count()}")
        print(f"  torch.cuda.get_device_name(0): {torch.cuda.get_device_name(0)}")

    model = nn.Sequential(nn.Linear(10, 8), nn.ReLU(), nn.Linear(8, 2))
    model = model.to(device)
    x = torch.randn(4, 10, device=device)
    y = model(x)
    print(f"\nmodel.to({device!s}) — forward output shape: {tuple(y.shape)}")

    # DataParallel: only meaningful with multiple GPUs
    if cuda_available and torch.cuda.device_count() > 1:
        dp_model = nn.DataParallel(model)
        y2 = dp_model(x)
        print(f"\nDataParallel on {torch.cuda.device_count()} GPUs, output shape: {tuple(y2.shape)}")
    else:
        print("\nDataParallel pattern (single or no CUDA):")
        print("  model = nn.DataParallel(model)  # uses all visible GPUs")
        print("  # Or: nn.DataParallel(model, device_ids=[0, 1])")
        print("  # Training: tensors must be on cuda:0 for DP default.")


if __name__ == "__main__":
    main()
