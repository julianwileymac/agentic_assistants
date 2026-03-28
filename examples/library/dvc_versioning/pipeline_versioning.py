# requires: dvc
"""Conceptual DVC pipeline versioning: dvc.yaml stages, params.yaml, and `dvc repro`.

DVC is primarily CLI-driven; this script prints representative YAML and workflow
commands. Optional imports show where Python APIs exist (e.g. opening a Repo).
"""

from __future__ import annotations


def _print_example_dvc_yaml() -> None:
    print(
        """
# Example dvc.yaml - pipeline stages and dependencies (data + params)
# -------------------------------------------------------------------
stages:
  prepare:
    cmd: python src/prepare.py data/raw data/prepared
    deps:
      - src/prepare.py
      - data/raw
    outs:
      - data/prepared

  train:
    cmd: python src/train.py data/prepared models/model.pkl
    deps:
      - src/train.py
      - data/prepared
      - params.yaml
    params:
      - train
    outs:
      - models/model.pkl
    metrics:
      - metrics.json:
          cache: false

  evaluate:
    cmd: python src/evaluate.py models/model.pkl data/prepared metrics.json
    deps:
      - src/evaluate.py
      - models/model.pkl
      - data/prepared
    metrics:
      - metrics.json:
          cache: false
"""
    )


def _print_example_params_yaml() -> None:
    print(
        """
# Example params.yaml - keyed sections referenced by dvc.yaml `params:`
# -----------------------------------------------------------------------
prepare:
  sample_frac: 0.25
  random_seed: 42

train:
  epochs: 10
  learning_rate: 0.001
  batch_size: 64
"""
    )


def _print_versioning_flow() -> None:
    print(
        """
Versioning flow (conceptual)
---------------------------
1. Git tracks dvc.yaml, params.yaml, and *.dvc pointer files - not large data blobs.
2. `dvc repro` runs stages whose deps or params changed (like Make for ML).
3. Changing params.yaml (e.g. train.learning_rate) invalidates downstream stages;
   DVC reruns train -> evaluate and updates metrics.json in the workspace.
4. Commit the updated dvc.lock (and metrics) to pin exact stage command hashes and
   data versions used for that experiment.

Typical CLI commands (strings you would run in the project root):
"""
    )
    for cmd in (
        "dvc init",
        "dvc repro",
        "dvc dag",
        "dvc status",
        "git add dvc.yaml dvc.lock params.yaml",
        "git commit -m 'Update pipeline params'",
    ):
        print(f"  $ {cmd}")


def main() -> None:
    print("DVC pipeline versioning (dvc.yaml + params.yaml + dvc repro)\n")
    print("=== Example dvc.yaml ===")
    _print_example_dvc_yaml()
    print("=== Example params.yaml ===")
    _print_example_params_yaml()
    _print_versioning_flow()

    try:
        from dvc.repo import Repo  # noqa: F401

        print(
            "\nPython API (optional): `from dvc.repo import Repo` - "
            "open a project with Repo('.') to program `repro`, `status`, etc."
        )
    except ImportError:
        print(
            "\nInstall DVC to use the Python API: pip install dvc\n"
            "The YAML and CLI workflow above is valid without importing dvc."
        )


if __name__ == "__main__":
    main()
