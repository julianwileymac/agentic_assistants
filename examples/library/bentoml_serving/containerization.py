# requires: bentoml
"""BentoML containerization: bentofile.yaml, `bentoml build`, Docker/OCI export.

Prints reference YAML and CLI strings; importing `bentoml` verifies the package.
"""

from __future__ import annotations


def _print_bentofile_yaml() -> None:
    print(
        """
# bentofile.yaml - build manifest for `bentoml build`
# ---------------------------------------------------
# service: module:attribute for the @bentoml.service class
service: "service:MyService"
labels:
  owner: ml-platform
  project: scoring-api
include:
  - "*.py"
  - "configs/"
python:
  packages:
    - scikit-learn
    - numpy
docker:
  distro: debian
  python_version: "3.11"
  # system_packages:
  #   - libgomp1
"""
    )


def _print_build_and_export_commands() -> None:
    print(
        """
CLI workflow (strings)
----------------------
# Build a Bento archive from the current directory (expects bentofile.yaml):
#   $ bentoml build

# List local Bentos:
#   $ bentoml list

# Containerize with the default backend (Docker):
#   $ bentoml containerize scoring_service:latest

# Write a Dockerfile only (inspect / customize before build):
#   $ bentoml containerize scoring_service:latest --backend docker --output docker/

# Push to a registry after tagging the image produced by containerize:
#   $ docker tag scoring_service:latest myregistry.io/ml/scoring_service:v1
#   $ docker push myregistry.io/ml/scoring_service:v1
"""
    )


def main() -> None:
    print("BentoML bentofile.yaml + build + container export\n")
    print("=== Example bentofile.yaml ===")
    _print_bentofile_yaml()
    _print_build_and_export_commands()

    try:
        import bentoml  # noqa: F401

        print(
            "Python: `bentoml.bentos.build_bentofile()` can build from a bentofile "
            "when you need programmatic builds (see BentoML reference docs)."
        )
    except ImportError:
        print("Install: pip install bentoml")


if __name__ == "__main__":
    main()
