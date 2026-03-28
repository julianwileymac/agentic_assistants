"""Demonstrates saving a Keras model as SavedModel, optional TFLite conversion, and reload inference.

Trains a tiny MLP briefly on synthetic data, exports with the TensorFlow SavedModel format,
converts a flat-buffer TFLite model for the same graph (conceptual deployment path), reloads
both representations, and prints max absolute differences versus the in-memory Keras model.
"""

# requires: tensorflow

from __future__ import annotations

import tempfile
from pathlib import Path

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

    tf.random.set_seed(1)
    rng = np.random.default_rng(1)

    n, dim, n_classes = 200, 6, 3
    x = rng.standard_normal((n, dim)).astype(np.float32)
    y = np.argmax(
        x @ rng.standard_normal((dim, n_classes)) + 0.1 * rng.standard_normal((n, n_classes)),
        axis=1,
    )

    model = keras.Sequential(
        [
            layers.Input(shape=(dim,)),
            layers.Dense(16, activation="relu"),
            layers.Dense(n_classes, activation="softmax"),
        ],
        name="export_demo_mlp",
    )
    model.compile(
        optimizer="adam",
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    model.fit(x, y, epochs=8, batch_size=32, verbose=0)

    sample = rng.standard_normal((4, dim)).astype(np.float32)
    keras_probs = model.predict(sample, verbose=0)

    with tempfile.TemporaryDirectory() as tmp:
        saved_path = Path(tmp) / "saved_model"
        # SavedModel directory: legacy `save_format="tf"` or Keras 3 `model.export`.
        try:
            model.save(str(saved_path), save_format="tf")
        except (TypeError, ValueError, OSError):
            model.export(str(saved_path))

        loaded_sm = keras.models.load_model(str(saved_path))
        sm_out = loaded_sm.predict(sample, verbose=0)

        converter = tf.lite.TFLiteConverter.from_saved_model(str(saved_path))
        tflite_bytes = converter.convert()
        tflite_path = Path(tmp) / "model.tflite"
        tflite_path.write_bytes(tflite_bytes)

        interp = tf.lite.Interpreter(model_content=tflite_bytes)
        interp.allocate_tensors()
        in_det = interp.get_input_details()[0]
        out_det = interp.get_output_details()[0]
        interp.set_tensor(in_det["index"], sample.astype(in_det["dtype"]))
        interp.invoke()
        lite_out = interp.get_tensor(out_det["index"])

    diff_sm = float(np.max(np.abs(keras_probs - sm_out)))
    diff_lite = float(np.max(np.abs(keras_probs - lite_out)))

    print("Export / reload demo (synthetic classification MLP)")
    print(f"SavedModel directory (temp) -> {saved_path}")
    print(f"TFLite: flatbuffer size = {len(tflite_bytes):,} bytes")
    print()
    print("Inference comparison on 4 random samples (max abs diff vs in-memory Keras):")
    print(f"  Keras vs load_model(SavedModel): {diff_sm:.2e}")
    print(f"  Keras vs TFLite interpreter:   {diff_lite:.2e}")
    print()
    print("First sample softmax (Keras):", np.round(keras_probs[0], 4))
    print("First sample softmax (TFLite):", np.round(lite_out[0], 4))


if __name__ == "__main__":
    main()
