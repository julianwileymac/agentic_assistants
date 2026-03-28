# requires: bentoml numpy pydantic
"""BentoML API endpoints: `@bentoml.api` with ndarray I/O, JSON via Pydantic, batching notes.

Demonstrates IO descriptors (`NumpyNdarray`, `JSON`) and batch-friendly request shapes.
"""

from __future__ import annotations

try:
    import numpy as np
    import bentoml
    from bentoml.io import JSON, NumpyNdarray
    from pydantic import BaseModel, Field
except ImportError:
    _DEPS_OK = False
    np = None  # type: ignore[assignment]
    bentoml = None  # type: ignore[assignment]
else:
    _DEPS_OK = True


if _DEPS_OK:

    class PredictRequest(BaseModel):
        feature_rows: list[list[float]] = Field(
            ...,
            description="Batch of samples; outer list = batch, inner = feature vector",
        )

    class PredictResponse(BaseModel):
        scores: list[float]

    @bentoml.service(name="io_demo_service")
    class IODemoService:
        @bentoml.api(input_spec=NumpyNdarray(), output_spec=NumpyNdarray())
        def infer_array(self, batch: np.ndarray) -> np.ndarray:
            """Row-wise identity-style demo; replace with model.predict(batch)."""
            return batch.astype(np.float64)

        @bentoml.api(input_spec=JSON(), output_spec=JSON())
        def infer_json(self, payload: PredictRequest) -> PredictResponse:
            arr = np.asarray(payload.feature_rows, dtype=np.float64)
            out = arr.sum(axis=-1)
            return PredictResponse(scores=out.tolist())

else:

    class IODemoService:  # type: ignore[no-redef]
        pass


def main() -> None:
    if not _DEPS_OK:
        print("Missing dependency (need bentoml, numpy, pydantic).")
        print("Install with: pip install bentoml numpy pydantic")
        return

    print("Service defined:", IODemoService)
    print(
        "\nBatch inference pattern:\n"
        "  - Numpy: stack rows as shape (batch, features) and POST once.\n"
        "  - JSON: send {\"feature_rows\": [[...], [...]]} for variable batch size.\n"
        "  - For very large batches, prefer ndarray endpoint + binary serialization."
    )
    print("Run: bentoml serve ...api_endpoints:IODemoService")


if __name__ == "__main__":
    main()
