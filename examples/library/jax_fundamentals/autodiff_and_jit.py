# requires: jax, jaxlib
"""jax.grad, jax.jit, jax.vmap on simple polynomials and losses; timing jitted vs eager."""

from __future__ import annotations

import time


def main() -> None:
    try:
        import jax
        import jax.numpy as jnp
    except ImportError:
        print("Install: pip install jax jaxlib")
        return

    def poly(x: jnp.ndarray) -> jnp.ndarray:
        return 3.0 * x**3 - 2.0 * x**2 + x + 1.0

    def mse_loss(params: tuple[jnp.ndarray, jnp.ndarray], x: jnp.ndarray, y: jnp.ndarray) -> jnp.ndarray:
        w, b = params
        pred = w * x + b
        return jnp.mean((pred - y) ** 2)

    x0 = jnp.array(2.0)
    g_poly = jax.grad(poly)
    print("poly(x) = 3x^3 - 2x^2 + x + 1")
    print(f"  poly({float(x0):.2f}) = {float(poly(x0)):.6f}")
    print(f"  grad at x={float(x0):.2f} = {float(g_poly(x0)):.6f}")

    key = jax.random.PRNGKey(0)
    w = jax.random.normal(key, ())
    b = jnp.array(0.5)
    xs = jax.random.normal(jax.random.split(key)[0], (8,))
    ys = 1.7 * xs + 0.3 + 0.1 * jax.random.normal(jax.random.split(key)[1], (8,))
    params = (w, b)
    loss_val = mse_loss(params, xs, ys)
    grad_fn = jax.grad(mse_loss)
    grads = grad_fn(params, xs, ys)
    print("\nLinear MSE loss on synthetic (x, y)")
    print(f"  loss = {float(loss_val):.6f}")
    print(f"  dL/dw = {float(grads[0]):.6f}, dL/db = {float(grads[1]):.6f}")

    # vmap: batch scalar inputs for poly
    xs_batch = jnp.linspace(-1.0, 1.0, 5)
    poly_vec = jax.vmap(poly)(xs_batch)
    grad_vec = jax.vmap(g_poly)(xs_batch)
    print("\njax.vmap(poly) and vmap(grad(poly)) on batch:")
    print(f"  x: {xs_batch}")
    print(f"  poly(x): {poly_vec}")
    print(f"  grad:    {grad_vec}")

    def heavy(x: jnp.ndarray) -> jnp.ndarray:
        y = x
        for _ in range(200):
            y = jnp.tanh(y @ x)
        return jnp.sum(y)

    x_mat = jax.random.normal(key, (32, 32))

    def timeit(fn, n_warmup: int = 3, n_run: int = 10) -> float:
        for _ in range(n_warmup):
            _ = fn(x_mat).block_until_ready()
        t0 = time.perf_counter()
        for _ in range(n_run):
            out = fn(x_mat).block_until_ready()
        return (time.perf_counter() - t0) / n_run

    eager_ms = timeit(heavy) * 1000
    jitted = jax.jit(heavy)
    _ = jitted(x_mat).block_until_ready()  # compile
    jit_ms = timeit(jitted) * 1000
    print("\nTiming (32x32 mat, 200 tanh steps, mean over 10 runs after warmup):")
    print(f"  eager: {eager_ms:.3f} ms / call")
    print(f"  jitted: {jit_ms:.3f} ms / call")


if __name__ == "__main__":
    main()
