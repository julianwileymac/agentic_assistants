# requires: torch

"""
Mixed precision training: autocast, GradScaler, and a short FP32 vs AMP loop
comparison; reports CUDA memory when a GPU is present.
"""

from __future__ import annotations


def main() -> None:
    try:
        import torch
        import torch.nn as nn
    except ImportError:
        print("Install: pip install torch")
        return

    def train_steps(
        model: nn.Module,
        x: torch.Tensor,
        y: torch.Tensor,
        *,
        use_amp: bool,
        device: torch.device,
        scaler: torch.amp.GradScaler | None,
        n_steps: int = 60,
    ) -> float:
        opt = torch.optim.SGD(model.parameters(), lr=0.05, momentum=0.9)
        loss_fn = nn.MSELoss()
        model.train()
        last_loss = 0.0
        for _ in range(n_steps):
            opt.zero_grad(set_to_none=True)
            if use_amp and device.type == "cuda":
                with torch.amp.autocast("cuda", dtype=torch.float16):
                    pred = model(x)
                    loss = loss_fn(pred, y)
                assert scaler is not None
                scaler.scale(loss).backward()
                scaler.step(opt)
                scaler.update()
            else:
                pred = model(x)
                loss = loss_fn(pred, y)
                loss.backward()
                opt.step()
            last_loss = float(loss.detach())
        return last_loss

    torch.manual_seed(31)

    class TinyMLP(nn.Module):
        def __init__(self, dim: int = 512, hidden: int = 2048) -> None:
            super().__init__()
            self.net = nn.Sequential(
                nn.Linear(dim, hidden),
                nn.ReLU(),
                nn.Linear(hidden, hidden),
                nn.ReLU(),
                nn.Linear(hidden, 1),
            )

        def forward(self, x: torch.Tensor) -> torch.Tensor:
            return self.net(x)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    batch, dim = 256, 512
    x = torch.randn(batch, dim, device=device)
    y = torch.randn(batch, 1, device=device)

    print("=" * 60)
    print("torch.amp.autocast + GradScaler (CUDA) vs full FP32")
    print("=" * 60)
    print(f"  device: {device}")
    print(
        "  Pattern: with torch.amp.autocast('cuda', dtype=torch.float16):\n"
        "              loss = model(x); scaler.scale(loss).backward(); ..."
    )

    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats(device)
        torch.cuda.synchronize(device)
        m_fp32 = TinyMLP(dim).to(device)
        train_steps(m_fp32, x, y, use_amp=False, device=device, scaler=None, n_steps=80)
        torch.cuda.synchronize(device)
        mem_fp32 = torch.cuda.max_memory_allocated(device)
        torch.cuda.reset_peak_memory_stats(device)
        m_amp = TinyMLP(dim).to(device)
        scaler = torch.amp.GradScaler("cuda", enabled=True)
        train_steps(m_amp, x, y, use_amp=True, device=device, scaler=scaler, n_steps=80)
        torch.cuda.synchronize(device)
        mem_amp = torch.cuda.max_memory_allocated(device)
        print(f"  Peak CUDA memory (FP32 run):  {mem_fp32 / 1024**2:.2f} MiB")
        print(f"  Peak CUDA memory (AMP run):   {mem_amp / 1024**2:.2f} MiB")
    else:
        print("  CUDA not available - skipping torch.cuda.memory_allocated comparison.")
        print("  On GPU, compare torch.cuda.reset_peak_memory_stats before/after each loop.")

    print()
    print("=" * 60)
    print("Short training loss comparison (same synthetic data, CPU-safe)")
    print("=" * 60)
    cpu = torch.device("cpu")
    x_cpu = torch.randn(128, 256, device=cpu)
    y_cpu = torch.randn(128, 1, device=cpu)
    m1 = TinyMLP(dim=256, hidden=1024).to(cpu)
    m2 = TinyMLP(dim=256, hidden=1024).to(cpu)
    lf32 = train_steps(m1, x_cpu, y_cpu, use_amp=False, device=cpu, scaler=None, n_steps=50)
    lf32_b = train_steps(m2, x_cpu, y_cpu, use_amp=False, device=cpu, scaler=None, n_steps=50)
    print(f"  Final loss (run A, FP32): {lf32:.6f}")
    print(f"  Final loss (run B, FP32): {lf32_b:.6f}")
    print("  On CUDA, enable AMP in the loop above to compare throughput and memory.")


if __name__ == "__main__":
    main()
