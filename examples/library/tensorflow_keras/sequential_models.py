"""Demonstrates the Keras Sequential API for a dense MLP classifier on synthetic tabular data.

Builds a stack of Dense layers with `tf.keras.Sequential`, compiles with an optimizer and
loss, fits with validation split, evaluates on held-out data, and prints the model summary
plus key training-history metrics.
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

    rng = np.random.default_rng(42)
    tf.random.set_seed(42)

    n_samples = 800
    n_features = 12
    n_classes = 4

    x = rng.standard_normal((n_samples, n_features)).astype(np.float32)
    logits = x @ rng.standard_normal((n_features, n_classes))
    y = np.argmax(logits + 0.15 * rng.standard_normal((n_samples, n_classes)), axis=1)

    split = int(0.8 * n_samples)
    x_train, x_val = x[:split], x[split:]
    y_train, y_val = y[:split], y[split:]

    model = keras.Sequential(
        [
            layers.Input(shape=(n_features,)),
            layers.Dense(64, activation="relu"),
            layers.Dense(32, activation="relu"),
            layers.Dense(n_classes, activation="softmax"),
        ],
        name="synthetic_mlp",
    )

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=1e-3),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )

    print("Model summary")
    print("-" * 60)
    model.summary()
    print("-" * 60)
    print()

    history = model.fit(
        x_train,
        y_train,
        validation_data=(x_val, y_val),
        epochs=12,
        batch_size=32,
        verbose=0,
    )

    loss, acc = model.evaluate(x_val, y_val, verbose=0)
    print("Training history (last 3 epochs)")
    for name in ("loss", "val_loss", "accuracy", "val_accuracy"):
        vals = history.history[name]
        print(f"  {name}: ... {vals[-3]}, {vals[-2]}, {vals[-1]}")
    print()
    print(f"Final evaluate on validation: loss={loss:.4f}, accuracy={acc:.4f}")


if __name__ == "__main__":
    main()
