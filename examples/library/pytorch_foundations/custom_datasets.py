# requires: torch
"""Custom Dataset, DataLoader (batch/shuffle), transforms: tabular + image-like tensors."""

from __future__ import annotations


def main() -> None:
    try:
        import torch
        from torch.utils.data import DataLoader, Dataset
    except ImportError:
        print("Install: pip install torch")
        return

    torch.manual_seed(7)

    class TabularSyntheticDataset(Dataset):
        """Rows of random features with a synthetic binary label."""

        def __init__(self, n: int, dim: int, transform_features=None, transform_label=None) -> None:
            self.x = torch.randn(n, dim)
            # label = sign of first feature + noise threshold
            logits = self.x[:, 0] + 0.25 * torch.randn(n)
            self.y = (logits > 0).long()
            self.t_feat = transform_features or (lambda t: t)
            self.t_lab = transform_label or (lambda t: t)

        def __len__(self) -> int:
            return self.x.shape[0]

        def __getitem__(self, idx: int):
            xi = self.t_feat(self.x[idx].clone())
            yi = self.t_lab(self.y[idx].clone())
            return xi, yi

    class ImageLikeTensorDataset(Dataset):
        """Fake CxHxW tensors with random class ids."""

        def __init__(self, n: int, channels: int, h: int, w: int, num_classes: int, transform=None) -> None:
            self.images = torch.randn(n, channels, h, w)
            self.labels = torch.randint(0, num_classes, (n,))
            self.transform = transform or (lambda img: img)

        def __len__(self) -> int:
            return self.images.shape[0]

        def __getitem__(self, idx: int):
            img = self.images[idx].clone()
            img = self.transform(img)
            return img, int(self.labels[idx].item())

    def standardize_features(x: torch.Tensor) -> torch.Tensor:
        # per-sample z-score (toy transform)
        m = x.mean()
        s = x.std().clamp(min=1e-6)
        return (x - m) / s

    def add_noise_channel(img: torch.Tensor) -> torch.Tensor:
        c, h, w = img.shape
        noise = 0.05 * torch.randn(1, h, w)
        return torch.cat([img, noise], dim=0)

    tab_ds = TabularSyntheticDataset(
        n=200,
        dim=8,
        transform_features=standardize_features,
        transform_label=lambda t: t,
    )
    tab_loader = DataLoader(tab_ds, batch_size=16, shuffle=True, drop_last=True)

    print("Tabular synthetic dataset (first batch):")
    xb, yb = next(iter(tab_loader))
    print(f"  batch x shape: {tuple(xb.shape)}, y shape: {tuple(yb.shape)}")
    print(f"  y unique in batch: {torch.unique(yb).tolist()}")

    img_ds = ImageLikeTensorDataset(
        n=64,
        channels=3,
        h=16,
        w=16,
        num_classes=5,
        transform=add_noise_channel,
    )
    img_loader = DataLoader(img_ds, batch_size=8, shuffle=True)

    print("\nImage-like tensor dataset (first batch):")
    ib, lb = next(iter(img_loader))
    print(f"  batch image shape (C added by transform): {tuple(ib.shape)}")
    print(f"  labels: {lb.tolist()}")


if __name__ == "__main__":
    main()
