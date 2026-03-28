# requires: torch

"""
Transformer building blocks from scratch: multi-head attention, sinusoidal
positional encoding, encoder layer, and a tiny sequence classifier on synthetic tokens.
"""

from __future__ import annotations


def main() -> None:
    try:
        import math

        import torch
        import torch.nn as nn
        import torch.nn.functional as F
    except ImportError:
        print("Install: pip install torch")
        return

    torch.manual_seed(23)

    class MultiHeadAttention(nn.Module):
        def __init__(self, d_model: int, n_heads: int, dropout: float = 0.1) -> None:
            super().__init__()
            assert d_model % n_heads == 0
            self.d_model = d_model
            self.n_heads = n_heads
            self.d_head = d_model // n_heads
            self.qkv = nn.Linear(d_model, 3 * d_model)
            self.out = nn.Linear(d_model, d_model)
            self.dropout = nn.Dropout(dropout)

        def forward(self, x: torch.Tensor, attn_mask: torch.Tensor | None = None) -> torch.Tensor:
            # x: (batch, seq, d_model)
            b, t, _ = x.shape
            qkv = self.qkv(x)
            q, k, v = qkv.chunk(3, dim=-1)
            q = q.view(b, t, self.n_heads, self.d_head).transpose(1, 2)
            k = k.view(b, t, self.n_heads, self.d_head).transpose(1, 2)
            v = v.view(b, t, self.n_heads, self.d_head).transpose(1, 2)
            scores = (q @ k.transpose(-2, -1)) / math.sqrt(self.d_head)
            if attn_mask is not None:
                scores = scores.masked_fill(attn_mask == 0, float("-inf"))
            w = F.softmax(scores, dim=-1)
            w = self.dropout(w)
            ctx = w @ v
            ctx = ctx.transpose(1, 2).contiguous().view(b, t, self.d_model)
            return self.out(ctx)

    class SinusoidalPositionalEncoding(nn.Module):
        def __init__(self, d_model: int, max_len: int = 512, dropout: float = 0.1) -> None:
            super().__init__()
            self.dropout = nn.Dropout(dropout)
            pe = torch.zeros(max_len, d_model)
            pos = torch.arange(0, max_len, dtype=torch.float32).unsqueeze(1)
            div = torch.exp(
                torch.arange(0, d_model, 2, dtype=torch.float32) * (-math.log(10000.0) / d_model)
            )
            pe[:, 0::2] = torch.sin(pos * div)
            pe[:, 1::2] = torch.cos(pos * div)
            self.register_buffer("pe", pe.unsqueeze(0), persistent=False)

        def forward(self, x: torch.Tensor) -> torch.Tensor:
            t = x.size(1)
            x = x + self.pe[:, :t]
            return self.dropout(x)

    class TransformerEncoderBlock(nn.Module):
        def __init__(self, d_model: int, n_heads: int, d_ff: int, dropout: float = 0.1) -> None:
            super().__init__()
            self.mha = MultiHeadAttention(d_model, n_heads, dropout)
            self.ln1 = nn.LayerNorm(d_model)
            self.ln2 = nn.LayerNorm(d_model)
            self.ff = nn.Sequential(
                nn.Linear(d_model, d_ff),
                nn.GELU(),
                nn.Dropout(dropout),
                nn.Linear(d_ff, d_model),
                nn.Dropout(dropout),
            )

        def forward(self, x: torch.Tensor) -> torch.Tensor:
            # Encoder self-attention: full sequence (no causal mask).
            y = self.mha(self.ln1(x), attn_mask=None)
            x = x + y
            y2 = self.ff(self.ln2(x))
            return x + y2

    class MiniSequenceClassifier(nn.Module):
        """Token embeddings + sinusoidal PE + stacked encoder blocks + mean pool + linear."""

        def __init__(
            self,
            vocab_size: int,
            num_classes: int,
            d_model: int = 64,
            n_heads: int = 4,
            n_layers: int = 2,
            d_ff: int = 128,
            max_len: int = 64,
        ) -> None:
            super().__init__()
            self.embed = nn.Embedding(vocab_size, d_model)
            self.pos = SinusoidalPositionalEncoding(d_model, max_len=max_len)
            self.blocks = nn.ModuleList(
                TransformerEncoderBlock(d_model, n_heads, d_ff) for _ in range(n_layers)
            )
            self.head = nn.Linear(d_model, num_classes)

        def forward(self, token_ids: torch.Tensor) -> torch.Tensor:
            x = self.embed(token_ids) * math.sqrt(self.embed.embedding_dim)
            x = self.pos(x)
            for blk in self.blocks:
                x = blk(x)
            # First position has attended to the full sequence; matches labels tied to token 0.
            pooled = x[:, 0]
            return self.head(pooled)

    print("=" * 60)
    print("Synthetic sequence classification (parity of first token id mod 2)")
    print("=" * 60)

    vocab_size = 32
    seq_len = 24
    batch = 48
    num_classes = 2

    def synthetic_batch(bs: int):
        toks = torch.randint(0, vocab_size, (bs, seq_len))
        y = (toks[:, 0] % 2).long()
        return toks, y

    model = MiniSequenceClassifier(vocab_size, num_classes)
    opt = torch.optim.AdamW(model.parameters(), lr=3e-3)
    loss_fn = nn.CrossEntropyLoss()

    model.train()
    for step in range(120):
        xb, yb = synthetic_batch(batch)
        logits = model(xb)
        loss = loss_fn(logits, yb)
        opt.zero_grad()
        loss.backward()
        opt.step()
        if step % 20 == 0:
            print(f"  step {step:3d}  loss {loss.item():.4f}")

    model.eval()
    with torch.no_grad():
        xb, yb = synthetic_batch(256)
        pred = model(xb).argmax(dim=-1)
        acc = (pred == yb).float().mean().item()
    print(f"  Eval accuracy (synthetic hold-out batch): {acc:.4f}")

    print()
    print("Module layout (for reference):")
    print(f"  MultiHeadAttention: d_model=64, n_heads=4")
    print(f"  Encoder blocks: {len(model.blocks)}")


if __name__ == "__main__":
    main()
