"""Demonstrates a custom training loop with `tf.GradientTape`, a custom loss, and LR scheduling.

Uses synthetic regression data, applies a hand-rolled Huber-style loss, optimizes with Adam
using `tf.keras.optimizers.schedules.ExponentialDecay`, and tracks mean absolute error manually
each epoch (no `model.fit`).
"""

# requires: tensorflow

from __future__ import annotations

import numpy as np


def main() -> None:
    try:
        import tensorflow as tf
        from tensorflow import keras
        from tensorflow.keras import layers
    except ImportError:
        print(
            "This example requires TensorFlow. Install with:\n"
            "  pip install tensorflow"
        )
        return

    rng = np.random.default_rng(123)
    tf.random.set_seed(123)

    n = 512
    dim = 8
    x = rng.standard_normal((n, dim)).astype(np.float32)
    true_w = rng.standard_normal((dim, 1)).astype(np.float32)
    y = (x @ true_w + 0.08 * rng.standard_normal((n, 1))).astype(np.float32)

    ds = (
        tf.data.Dataset.from_tensor_slices((x, y))
        .shuffle(n)
        .batch(32)
        .prefetch(tf.data.AUTOTUNE)
    )

    model = keras.Sequential(
        [
            layers.Input(shape=(dim,)),
            layers.Dense(32, activation="relu"),
            layers.Dense(1),
        ]
    )

    initial_lr = 0.05
    lr_schedule = keras.optimizers.schedules.ExponentialDecay(
        initial_learning_rate=initial_lr,
        decay_steps=30,
        decay_rate=0.9,
        staircase=True,
    )
    optimizer = keras.optimizers.Adam(learning_rate=lr_schedule)

    delta = 0.5

    def custom_huber(y_true: tf.Tensor, y_pred: tf.Tensor) -> tf.Tensor:
        err = y_true - y_pred
        abs_err = tf.abs(err)
        quadratic = tf.minimum(abs_err, delta)
        linear = abs_err - quadratic
        return tf.reduce_mean(0.5 * tf.square(quadratic) + delta * linear)

    print("Custom training: GradientTape + custom loss + ExponentialDecay schedule")
    print(f"Huber delta={delta}, initial_lr={initial_lr}")
    print()

    for epoch in range(1, 11):
        epoch_loss = keras.metrics.Mean(name="epoch_loss")
        epoch_mae = keras.metrics.Mean(name="epoch_mae")

        for xb, yb in ds:
            with tf.GradientTape() as tape:
                preds = model(xb, training=True)
                loss = custom_huber(yb, preds)

            grads = tape.gradient(loss, model.trainable_variables)
            optimizer.apply_gradients(zip(grads, model.trainable_variables))

            mae = tf.reduce_mean(tf.abs(yb - preds))
            epoch_loss.update_state(loss)
            epoch_mae.update_state(mae)

        step = int(optimizer.iterations.numpy())
        current_lr = optimizer.learning_rate(step)
        if hasattr(current_lr, "numpy"):
            lr_val = float(current_lr.numpy())
        else:
            lr_val = float(current_lr)

        print(
            f"Epoch {epoch:2d}  loss={float(epoch_loss.result().numpy()):.5f}  "
            f"mae={float(epoch_mae.result().numpy()):.5f}  lr={lr_val:.6f}"
        )


if __name__ == "__main__":
    main()
