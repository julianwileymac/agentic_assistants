"""Demonstrates the Keras Functional API with multiple inputs, shared weights, and a skip path.

Builds one numerical branch and one categorical branch (embedding), applies the same Dense
block to both (shared layer), concatenates, adds a skip connection from a projection of the
numerical input, and trains on synthetic labels with `compile` / `fit`. Prints a layer-wise
summary of the graph.
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

    rng = np.random.default_rng(7)
    tf.random.set_seed(7)

    n = 600
    num_dim = 20
    n_cat = 24
    n_classes = 3

    num_x = rng.standard_normal((n, num_dim)).astype(np.float32)
    cat_ids = rng.integers(0, n_cat, size=(n, 1), dtype=np.int32)
    hidden = num_x[:, :8].sum(axis=1, keepdims=True) + (cat_ids.astype(np.float32) % 5)
    y = np.argmax(
        np.concatenate(
            [hidden, -hidden, 0.1 * rng.standard_normal((n, 1))],
            axis=1,
        ),
        axis=1,
    )

    split = int(0.85 * n)
    train = slice(0, split)
    val = slice(split, None)

    num_in = keras.Input(shape=(num_dim,), name="numerical")
    cat_in = keras.Input(shape=(1,), dtype="int32", name="categorical_id")

    shared_block = layers.Dense(32, activation="relu", name="shared_dense")

    cat_emb = layers.Flatten()(
        layers.Embedding(n_cat, 8, name="cat_embedding")(cat_in)
    )

    h_num = shared_block(num_in)
    h_cat = shared_block(cat_emb)
    merged = layers.Concatenate(name="merge_branches")([h_num, h_cat])
    hidden = layers.Dense(32, activation="relu", name="combined")(merged)
    skip = layers.Dense(32, activation="linear", name="num_skip_proj")(num_in)
    with_skip = layers.Add(name="add_skip")([hidden, skip])
    out = layers.Dense(n_classes, activation="softmax", name="predictions")(with_skip)

    model = keras.Model(
        inputs=[num_in, cat_in],
        outputs=out,
        name="multi_input_skip_functional",
    )

    model.compile(
        optimizer=keras.optimizers.Adam(1e-3),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )

    print("Functional model: multi-input, shared Dense, skip connection")
    print("-" * 60)
    model.summary(line_length=100)
    print("-" * 60)

    history = model.fit(
        [num_x[train], cat_ids[train]],
        y[train],
        validation_data=([num_x[val], cat_ids[val]], y[val]),
        epochs=15,
        batch_size=32,
        verbose=0,
    )

    print()
    print("Sample of training history (final epoch)")
    print(f"  loss: {history.history['loss'][-1]:.4f}")
    print(f"  val_loss: {history.history['val_loss'][-1]:.4f}")
    print(f"  accuracy: {history.history['accuracy'][-1]:.4f}")
    print(f"  val_accuracy: {history.history['val_accuracy'][-1]:.4f}")


if __name__ == "__main__":
    main()
