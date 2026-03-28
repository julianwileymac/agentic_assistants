# requires: jax, optax
"""Optax (Adam, SGD + schedule), jitted train step, few steps on synthetic linear regression."""

from __future__ import annotations

from typing import Any


def main() -> None:
    try:
        import jax
        import jax.numpy as jnp
        import optax
    except ImportError:
        print("Install: pip install jax optax")
        return

    key = jax.random.PRNGKey(42)
    k1, k2 = jax.random.split(key)
    n, d = 128, 6
    true_w = jax.random.normal(k1, (d,))
    x = jax.random.normal(k2, (n, d))
    y = x @ true_w + 0.1 * jax.random.normal(jax.random.split(k2)[0], (n,))

    def predict(w: jnp.ndarray, xb: jnp.ndarray) -> jnp.ndarray:
        return xb @ w

    def loss_fn(w: jnp.ndarray, xb: jnp.ndarray, yb: jnp.ndarray) -> jnp.ndarray:
        err = predict(w, xb) - yb
        return jnp.mean(err**2)

    grad_fn = jax.grad(loss_fn)

    # Adam run
    w_adam = jnp.zeros((d,))
    tx_adam = optax.adam(learning_rate=0.05)

    @jax.jit
    def adam_step(w: jnp.ndarray, opt_state: Any, xb: jnp.ndarray, yb: jnp.ndarray):
        grads = grad_fn(w, xb, yb)
        updates, new_opt_state = tx_adam.update(grads, opt_state, w)
        new_w = optax.apply_updates(w, updates)
        return new_w, new_opt_state, loss_fn(w, xb, yb)

    opt_state = tx_adam.init(w_adam)
    print("Adam (jitted steps), full-batch synthetic linear regression")
    for step in range(1, 6):
        w_adam, opt_state, loss = adam_step(w_adam, opt_state, x, y)
        print(f"  step {step}: loss={float(loss):.6f}")

    # SGD with cosine decay schedule
    schedule = optax.cosine_decay_schedule(init_value=0.2, decay_steps=50, alpha=0.0)
    tx_sgd = optax.sgd(learning_rate=schedule)

    @jax.jit
    def sgd_step(w: jnp.ndarray, opt_state: Any, xb: jnp.ndarray, yb: jnp.ndarray):
        grads = grad_fn(w, xb, yb)
        updates, new_opt_state = tx_sgd.update(grads, opt_state, w)
        new_w = optax.apply_updates(w, updates)
        return new_w, new_opt_state, loss_fn(w, xb, yb)

    w_sgd = jnp.zeros((d,))
    opt_state_s = tx_sgd.init(w_sgd)
    print("\nSGD + cosine schedule (jitted), 5 steps")
    for step in range(5):
        w_sgd, opt_state_s, loss = sgd_step(w_sgd, opt_state_s, x, y)
        lr = float(schedule(step))
        print(f"  step {step + 1}: loss={float(loss):.6f}, schedule({step})={lr:.6f}")


if __name__ == "__main__":
    main()
