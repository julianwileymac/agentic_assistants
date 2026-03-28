# requires: dvc
"""DVC experiments: `dvc exp run`, metrics.json, params changes, diff and compare.

Prints CLI-oriented workflows; optional `dvc` import confirms the package is present.
"""

from __future__ import annotations


def _print_metrics_json_example() -> None:
    print(
        """
# Example metrics.json (referenced as metrics in dvc.yaml)
# --------------------------------------------------------
{
  "accuracy": 0.91,
  "f1": 0.88,
  "loss": 0.12
}
"""
    )


def _print_params_tweak() -> None:
    print(
        """
# Temporarily change params for an experiment (options)
# -------------------------------------------------------
# A) Edit params.yaml (train.*) then:
#      $ dvc exp run
#
# B) One-off override without editing files:
#      $ dvc exp run -S train.epochs=20 -S train.learning_rate=0.0005
#
# C) Queue multiple runs:
#      $ dvc exp run --queue -S train.batch_size=32
#      $ dvc exp run --queue -S train.batch_size=64
#      $ dvc exp run --run-all
"""
    )


def _print_diff_compare() -> None:
    print(
        """
Experiment diff and comparison (CLI strings)
--------------------------------------------
# Show what changed vs baseline (params, metrics, commits):
#   $ dvc exp diff

# Compare two experiment names or hashes:
#   $ dvc exp diff exp-abc123 exp-def456

# List experiments with metrics columns (tabular):
#   $ dvc exp show --no-pager

# Show a specific metric across experiments:
#   $ dvc metrics show --json

# Apply a successful experiment back to the workspace / branch:
#   $ dvc exp apply <exp-name-or-rev>

Flow summary
------------
1. Pipeline stages in dvc.yaml write metrics.json (cache: false is common).
2. `dvc exp run` creates an isolated Git commit (experiment ref) with params + metrics.
3. Compare runs with `dvc exp diff` / `dvc exp show` before promoting via `dvc exp apply`.
"""
    )


def main() -> None:
    print("DVC experiment tracking: exp run, metrics, params, diff\n")
    print("=== Example metrics.json ===")
    _print_metrics_json_example()
    print("=== params.yaml + dvc exp run patterns ===")
    _print_params_tweak()
    _print_diff_compare()

    try:
        import dvc  # noqa: F401

        print(
            "Package `dvc` is importable; experiment orchestration is still "
            "primarily via the `dvc exp` CLI shown above."
        )
    except ImportError:
        print("Install: pip install dvc")


if __name__ == "__main__":
    main()
