# requires: jax, flax
"""Flax Linen: MLP and CNN modules, init, apply, parameter tree inspection."""

from __future__ import annotations

from typing import Any


def main() -> None:
    try:
        import jax
        import jax.numpy as jnp
        from flax import linen as nn
    except ImportError:
        print("Install: pip install jax flax")
        return

    class MLP(nn.Module):
        hidden: int
        out_dim: int

        @nn.compact
        def __call__(self, x: jnp.ndarray) -> jnp.ndarray:
            x = nn.Dense(self.hidden)(x)
            x = nn.relu(x)
            x = nn.Dense(self.out_dim)(x)
            return x

    class TinyCNN(nn.Module):
        num_classes: int

        @nn.compact
        def __call__(self, x: jnp.ndarray, train: bool = False) -> jnp.ndarray:
            x = nn.Conv(features=16, kernel_size=(3, 3), padding="SAME")(x)
            x = nn.relu(x)
            x = nn.max_pool(x, window_shape=(2, 2), strides=(2, 2))
            x = nn.Conv(features=32, kernel_size=(3, 3), padding="SAME")(x)
            x = nn.relu(x)
            x = jnp.mean(x, axis=(1, 2))
            x = nn.Dense(self.num_classes)(x)
            return x

    key = jax.random.PRNGKey(0)
    key_mlp, key_cnn = jax.random.split(key)

    mlp = MLP(hidden=32, out_dim=4)
    x_vec = jax.random.normal(key_mlp, (2, 12))
    variables = mlp.init(key_mlp, x_vec)
    y_mlp = mlp.apply(variables, x_vec)

    print("MLP")
    print(f"  output shape: {y_mlp.shape}")
    print("  params (nested shapes):")
    shapes = jax.tree_util.tree_map(lambda a: getattr(a, "shape", ()), variables["params"])

    def print_nested(obj: Any, prefix: str = "") -> None:
        if isinstance(obj, dict):
            for k, v in obj.items():
                print_nested(v, prefix + k + "/")
        else:
            print(f"    {prefix.rstrip('/')}: {obj}")

    print_nested(shapes)

    cnn = TinyCNN(num_classes=5)
    x_img = jax.random.normal(key_cnn, (2, 8, 8, 3))
    variables_c = cnn.init(key_cnn, x_img)
    y_cnn = cnn.apply(variables_c, x_img)

    print("\nTinyCNN (NHWC)")
    print(f"  output shape: {y_cnn.shape}")

    def count_params(params) -> int:
        return int(sum(jnp.size(x) for x in jax.tree_util.tree_leaves(params)))

    print(f"  total params: {count_params(variables_c['params']):,}")


if __name__ == "__main__":
    main()
