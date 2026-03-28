# requires: torch
"""Synthetic regression: DataLoader, Adam, StepLR, logging, validation, early stopping."""

from __future__ import annotations


def main() -> None:
    try:
        import torch
        import torch.nn as nn
        from torch.utils.data import DataLoader, TensorDataset
    except ImportError:
        print("Install: pip install torch")
        return

    torch.manual_seed(42)

    n_train, n_val, dim = 512, 128, 16
    true_w = torch.randn(dim, 1)

    def make_split(n: int) -> TensorDataset:
        x = torch.randn(n, dim)
        noise = 0.1 * torch.randn(n, 1)
        y = x @ true_w + noise
        return TensorDataset(x, y)

    train_ds = make_split(n_train)
    val_ds = make_split(n_val)

    train_loader = DataLoader(train_ds, batch_size=32, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=64, shuffle=False)

    model = nn.Sequential(nn.Linear(dim, 32), nn.ReLU(), nn.Linear(32, 1))
    opt = torch.optim.Adam(model.parameters(), lr=0.05)
    scheduler = torch.optim.lr_scheduler.StepLR(opt, step_size=2, gamma=0.5)
    loss_fn = nn.MSELoss()

    max_epochs = 12
    patience = 3
    best_val = float("inf")
    stall = 0

    print("Training (synthetic linear target + MLP)")
    print(f"Epochs (max): {max_epochs}, early stopping patience: {patience}")
    print()

    for epoch in range(1, max_epochs + 1):
        model.train()
        running = 0.0
        n_seen = 0
        for xb, yb in train_loader:
            opt.zero_grad()
            pred = model(xb)
            loss = loss_fn(pred, yb)
            loss.backward()
            opt.step()
            running += loss.item() * xb.size(0)
            n_seen += xb.size(0)
        train_loss = running / n_seen

        model.eval()
        vsum, vcount = 0.0, 0
        with torch.no_grad():
            for xb, yb in val_loader:
                pred = model(xb)
                vsum += loss_fn(pred, yb).item() * xb.size(0)
                vcount += xb.size(0)
        val_loss = vsum / vcount

        lr = opt.param_groups[0]["lr"]
        print(f"Epoch {epoch:2d}  train_loss={train_loss:.6f}  val_loss={val_loss:.6f}  lr={lr:.6f}")

        scheduler.step()

        if val_loss < best_val - 1e-6:
            best_val = val_loss
            stall = 0
        else:
            stall += 1
            if stall >= patience:
                print(f"\nEarly stopping at epoch {epoch} (no val improvement for {patience} epochs).")
                print(f"Best validation loss: {best_val:.6f}")
                break
    else:
        print(f"\nFinished {max_epochs} epochs. Best validation loss: {best_val:.6f}")


if __name__ == "__main__":
    main()
