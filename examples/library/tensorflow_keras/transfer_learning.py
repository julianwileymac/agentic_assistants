"""Demonstrates transfer-learning-style setup with MobileNetV2 and a small classification head.

Loads `MobileNetV2` without the top, freezes the base for feature extraction, attaches a
global pooling layer and dense head, and reports trainable versus non-trainable parameter
counts. Runs one optimizer step on synthetic image batches (no dataset download).

By default the base uses randomly initialized weights (`weights=None`) so the script stays
fully offline; set `weights='imagenet'` for real pretrained features (may download once).
"""

# requires: tensorflow

from __future__ import annotations

import numpy as np


def main() -> None:
    try:
        import tensorflow as tf
        from tensorflow import keras
        from tensorflow.keras import layers
        from tensorflow.keras.applications import MobileNetV2
    except ImportError:
        print(
            "This example requires TensorFlow. Install with:\n"
            "  pip install tensorflow"
        )
        return

    tf.random.set_seed(2024)
    rng = np.random.default_rng(2024)

    img_h, img_w = 96, 96
    n_classes = 5
    batch_size = 4

    base = MobileNetV2(
        include_top=False,
        weights=None,
        input_shape=(img_h, img_w, 3),
        pooling=None,
    )
    base.trainable = False

    inputs = keras.Input(shape=(img_h, img_w, 3))
    x = base(inputs, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dropout(0.2)(x)
    outputs = layers.Dense(n_classes, activation="softmax")(x)
    model = keras.Model(inputs, outputs, name="mobilenet_transfer_head")

    model.compile(
        optimizer=keras.optimizers.Adam(1e-3),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )

    trainable = sum(
        tf.keras.backend.count_params(v) for v in model.trainable_variables
    )
    non_trainable = sum(
        tf.keras.backend.count_params(v) for v in model.non_trainable_variables
    )

    print("MobileNetV2 (include_top=False) + frozen base + classification head")
    print(f"Trainable parameters (head only):     {trainable:,}")
    print(f"Non-trainable parameters (frozen base): {non_trainable:,}")
    print(f"Total: {trainable + non_trainable:,}")
    print()

    x_batch = rng.random((batch_size, img_h, img_w, 3)).astype(np.float32)
    y_batch = rng.integers(0, n_classes, size=(batch_size,), dtype=np.int32)

    loss_fn = keras.losses.SparseCategoricalCrossentropy()
    opt = keras.optimizers.Adam(1e-3)

    with tf.GradientTape() as tape:
        preds = model(x_batch, training=True)
        step_loss = loss_fn(y_batch, preds)

    grads = tape.gradient(step_loss, model.trainable_variables)
    opt.apply_gradients(zip(grads, model.trainable_variables))

    preds_after = model(x_batch, training=False)
    loss_after = float(loss_fn(y_batch, preds_after).numpy())
    print("Single training step on synthetic batch")
    print(f"  batch shape: {x_batch.shape}, labels: {y_batch.tolist()}")
    print(f"  loss after one step: {loss_after:.4f}")
    print(f"  mean pred confidence (max class): {float(tf.reduce_mean(tf.reduce_max(preds_after, axis=1)).numpy()):.4f}")


if __name__ == "__main__":
    main()
