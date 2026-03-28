# requires: dvc
"""DVC data tracking: `dvc add`, remotes (S3/GCS), push/pull, .dvc files, and .gitignore.

Conceptual / documentation example with printed CLI strings and sample .dvc content.
"""

from __future__ import annotations


def _print_dvc_file_example() -> None:
    print(
        """
# Example data/dataset.csv.dvc - pointer tracked by Git; bulk data lives in cache/remote
# --------------------------------------------------------------------------------------
outs:
- md5: a1b2c3d4e5f6789012345678901234ab
  size: 10485760
  path: dataset.csv
"""
    )


def _print_gitignore_snippets() -> None:
    print(
        """
# .gitignore - keep large artifacts and local cache out of Git
# -------------------------------------------------------------
/data/*.csv
/data/*.parquet
/models/*.pkl
/dvc-cache/

# DVC local cache (default ~/.cache/dvc or ./.dvc/cache depending on config)
# If you symlink cache into the repo, ignore it:
/.dvc/cache/
"""
    )


def _print_remote_config_examples() -> None:
    print(
        """
# Remote storage: configure once, then push/pull tracked data
# -----------------------------------------------------------

# S3 - CLI (strings):
#   $ dvc remote add -d myremote s3://my-bucket/dvc-store
#   $ dvc remote modify myremote region us-east-1
#   $ dvc push
#   $ dvc pull

# GCS - CLI (strings):
#   $ dvc remote add -d gcsremote gs://my-bucket/dvc-store
#   $ dvc push
#   $ dvc pull

# ~/.config/dvc/config (conceptual) might contain:
#   ['remote "myremote"']
#   url = s3://my-bucket/dvc-store
#   region = us-east-1
"""
    )


def _print_workflow() -> None:
    print(
        """
Typical `dvc add` workflow
--------------------------
1. Place raw data under Git-ignored paths (see .gitignore above).
2. Run:  dvc add data/dataset.csv
   This creates data/dataset.csv.dvc and moves content into DVC cache.
3. Git-add the .dvc file only:  git add data/dataset.csv.dvc .gitignore
4. `dvc push` uploads cache objects to the default remote (S3/GCS/SSH/etc.).
5. Teammates `git pull` then `dvc pull` to materialize the same bytes via md5.

Python API (when installed): `import dvc.api` for open/get_url/read-only access
to tracked data by path or rev without manually syncing whole projects.
"""
    )


def main() -> None:
    print("DVC data tracking: add, remotes, .dvc pointers, gitignore\n")
    print("=== Example .dvc sidecar ===")
    _print_dvc_file_example()
    print("=== .gitignore integration ===")
    _print_gitignore_snippets()
    print("=== Remote config (S3 / GCS) ===")
    _print_remote_config_examples()
    _print_workflow()

    try:
        import dvc.api  # noqa: F401

        print(
            "Optional: `dvc.api.open()`, `dvc.api.read()`, `dvc.api.get_url()` "
            "for loading tracked files from specific Git commits."
        )
    except ImportError:
        print("Install: pip install dvc  (optional for Python API examples above)")


if __name__ == "__main__":
    main()
