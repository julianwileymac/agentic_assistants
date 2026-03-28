# requires: torch
"""Custom nn.Module patterns: linear, MLP, ConvNet; params; save/load state_dict."""

from __future__ import annotations


def main() -> None:
    try:
        import io
        import torch
        import torch.nn as nn
    except ImportError:
        print("Install: pip install torch")
        return

    torch.manual_seed(0)

    class SimpleLinear(nn.Module):
        def __init__(self, in_features: int, out_features: int) -> None:
            super().__init__()
            self.linear = nn.Linear(in_features, out_features)

        def forward(self, x: torch.Tensor) -> torch.Tensor:
            return self.linear(x)

    class MultiLayerPerceptron(nn.Module):
        def __init__(self, in_dim: int, hidden: int, out_dim: int) -> None:
            super().__init__()
            self.net = nn.Sequential(
                nn.Linear(in_dim, hidden),
                nn.ReLU(),
                nn.Linear(hidden, hidden),
                nn.ReLU(),
                nn.Linear(hidden, out_dim),
            )

        def forward(self, x: torch.Tensor) -> torch.Tensor:
            return self.net(x)

    class ConvNet(nn.Module):
        def __init__(self, in_ch: int = 3, num_classes: int = 10) -> None:
            super().__init__()
            self.features = nn.Sequential(
                nn.Conv2d(in_ch, 16, kernel_size=3, padding=1),
                nn.ReLU(),
                nn.MaxPool2d(2),
                nn.Conv2d(16, 32, kernel_size=3, padding=1),
                nn.ReLU(),
                nn.AdaptiveAvgPool2d((1, 1)),
            )
            self.head = nn.Linear(32, num_classes)

        def forward(self, x: torch.Tensor) -> torch.Tensor:
            h = self.features(x)
            h = h.flatten(1)
            return self.head(h)

    def count_parameters(module: nn.Module) -> int:
        return sum(p.numel() for p in module.parameters())

    def print_model_summary(name: str, module: nn.Module, sample_input: torch.Tensor) -> None:
        print(f"\n--- {name} ---")
        print(f"Total parameters: {count_parameters(module):,}")
        print("Layers:")
        for child_name, child in module.named_children():
            n = sum(p.numel() for p in child.parameters())
            print(f"  {child_name}: {child.__class__.__name__} ({n:,} params)")
        module.eval()
        with torch.no_grad():
            out = module(sample_input)
        print(f"Sample output shape: {tuple(out.shape)}")

    in_features, batch = 20, 4
    x_vec = torch.randn(batch, in_features)
    x_img = torch.randn(batch, 3, 8, 8)

    linear = SimpleLinear(in_features, 5)
    mlp = MultiLayerPerceptron(in_features, 32, 3)
    cnn = ConvNet(in_ch=3, num_classes=10)

    print_model_summary("SimpleLinear", linear, x_vec)
    print_model_summary("MultiLayerPerceptron", mlp, x_vec)
    print_model_summary("ConvNet", cnn, x_img)

    # Save / load state_dict (in-memory buffer to avoid disk I/O in examples)
    buf = io.BytesIO()
    torch.save(mlp.state_dict(), buf)
    buf.seek(0)
    mlp2 = MultiLayerPerceptron(in_features, 32, 3)
    before = mlp(x_vec).detach().clone()
    try:
        state = torch.load(buf, weights_only=True)
    except TypeError:
        buf.seek(0)
        state = torch.load(buf)
    mlp2.load_state_dict(state)
    after_load = mlp2(x_vec)
    print("\n--- state_dict round-trip ---")
    print(f"Outputs match after load: {torch.allclose(before, after_load)}")


if __name__ == "__main__":
    main()
