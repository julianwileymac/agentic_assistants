# requires: bentoml
"""Server-side micro-batching, concurrency, and resource hints for BentoML services.

Documents `@bentoml.api` batching kwargs and `@bentoml.service` resource blocks.
"""

from __future__ import annotations


def _print_service_resource_block() -> None:
    print(
        """
# @bentoml.service - cluster/resource hints (example)
# --------------------------------------------------
# @bentoml.service(
#     resources={"cpu": "2", "memory": "4Gi"},
#     traffic={"timeout": 60},
# )
# class MyService:
#     ...
"""
    )


def _print_api_batching_options() -> None:
    print(
        """
# @bentoml.api - adaptive micro-batching (conceptual kwargs)
# ----------------------------------------------------------
# batchable=True          # allow the server to merge concurrent requests
# max_batch_size=32       # upper bound on merged batch dimension
# max_latency_ms=10       # wait up to N ms to fill a batch before flushing
# batch_dim=0             # which axis is the batch dimension (or tuple for in/out)

# Example skeleton:
#
#   @bentoml.api(
#       batchable=True,
#       max_batch_size=64,
#       max_latency_ms=5,
#       input_spec=NumpyNdarray(),
#       output_spec=NumpyNdarray(),
#   )
#   def predict(self, inputs: np.ndarray) -> np.ndarray:
#       return self.model_runner.predict.run(inputs)
"""
    )


def _print_runner_gpu_notes() -> None:
    print(
        """
Runners and GPU allocation
--------------------------
- Framework runners (e.g. `bentoml.pytorch.get(...).to_runner()`) honor device
  placement configured in the library / model export; set `CUDA_VISIBLE_DEVICES`
  in the deployment environment for single-GPU pinning.
- `@bentoml.service(resources={"gpu": "1", ...})` declares scheduling needs on
  Kubernetes-style clusters (exact keys depend on your BentoCloud / Yatai version).
- Scale-out: increase replica count; batching reduces per-request overhead on each GPU.

Validate options for your installed version:
  $ python -c "import bentoml, inspect; print(inspect.signature(bentoml.api))"
"""
    )


def main() -> None:
    print("BentoML adaptive batching and resource configuration\n")
    _print_service_resource_block()
    _print_api_batching_options()
    _print_runner_gpu_notes()

    try:
        import inspect

        import bentoml

        print("\nInstalled bentoml.api signature:")
        print(inspect.signature(bentoml.api))
    except ImportError:
        print("\nInstall: pip install bentoml")
    except (TypeError, ValueError) as exc:
        print("\nCould not introspect bentoml.api:", exc)


if __name__ == "__main__":
    main()
