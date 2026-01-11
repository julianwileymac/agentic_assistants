# Chunk: 3f4c1edbb8e6_4

- source: `.venv-lab/Lib/site-packages/pip/_vendor/packaging/markers.py`
- lines: 327-363
- chunk: 5/5

```
 all other situations).

        The environment is determined from the current Python process.
        """
        current_environment = cast(
            "dict[str, str | AbstractSet[str]]", default_environment()
        )
        if context == "lock_file":
            current_environment.update(
                extras=frozenset(), dependency_groups=frozenset()
            )
        elif context == "metadata":
            current_environment["extra"] = ""
        if environment is not None:
            current_environment.update(environment)
            # The API used to allow setting extra to None. We need to handle this
            # case for backwards compatibility.
            if "extra" in current_environment and current_environment["extra"] is None:
                current_environment["extra"] = ""

        return _evaluate_markers(
            self._markers, _repair_python_full_version(current_environment)
        )


def _repair_python_full_version(
    env: dict[str, str | AbstractSet[str]],
) -> dict[str, str | AbstractSet[str]]:
    """
    Work around platform.python_version() returning something that is not PEP 440
    compliant for non-tagged Python builds.
    """
    python_full_version = cast(str, env["python_full_version"])
    if python_full_version.endswith("+"):
        env["python_full_version"] = f"{python_full_version}local"
    return env
```
