# Chunk: 8eb2c67fee2e_7

- source: `.venv-lab/Lib/site-packages/setuptools/dist.py`
- lines: 462-528
- chunk: 8/17

```
s explicitly given by the user
            files = self._expand_patterns(patterns, enforce_match=True)

        self.metadata.license_files = list(unique_everseen(files))

    @classmethod
    def _expand_patterns(
        cls, patterns: list[str], enforce_match: bool = True
    ) -> Iterator[str]:
        """
        >>> getfixture('sample_project_cwd')
        >>> list(Distribution._expand_patterns(['LICENSE.txt']))
        ['LICENSE.txt']
        >>> list(Distribution._expand_patterns(['pyproject.toml', 'LIC*']))
        ['pyproject.toml', 'LICENSE.txt']
        >>> list(Distribution._expand_patterns(['src/**/*.dat']))
        ['src/sample/package_data.dat']
        """
        return (
            path.replace(os.sep, "/")
            for pattern in patterns
            for path in sorted(cls._find_pattern(pattern, enforce_match))
            if not path.endswith('~') and os.path.isfile(path)
        )

    @staticmethod
    def _find_pattern(pattern: str, enforce_match: bool = True) -> list[str]:
        r"""
        >>> getfixture('sample_project_cwd')
        >>> Distribution._find_pattern("LICENSE.txt")
        ['LICENSE.txt']
        >>> Distribution._find_pattern("/LICENSE.MIT")
        Traceback (most recent call last):
        ...
        setuptools.errors.InvalidConfigError: Pattern '/LICENSE.MIT' should be relative...
        >>> Distribution._find_pattern("../LICENSE.MIT")
        Traceback (most recent call last):
        ...
        setuptools.warnings.SetuptoolsDeprecationWarning: ...Pattern '../LICENSE.MIT' cannot contain '..'...
        >>> Distribution._find_pattern("LICEN{CSE*")
        Traceback (most recent call last):
        ...
        setuptools.warnings.SetuptoolsDeprecationWarning: ...Pattern 'LICEN{CSE*' contains invalid characters...
        """
        pypa_guides = "specifications/glob-patterns/"
        if ".." in pattern:
            SetuptoolsDeprecationWarning.emit(
                f"Pattern {pattern!r} cannot contain '..'",
                """
                Please ensure the files specified are contained by the root
                of the Python package (normally marked by `pyproject.toml`).
                """,
                see_url=f"https://packaging.python.org/en/latest/{pypa_guides}",
                due_date=(2026, 3, 20),  # Introduced in 2025-03-20
                # Replace with InvalidConfigError after deprecation
            )
        if pattern.startswith((os.sep, "/")) or ":\\" in pattern:
            raise InvalidConfigError(
                f"Pattern {pattern!r} should be relative and must not start with '/'"
            )
        if re.match(r'^[\w\-\.\/\*\?\[\]]+$', pattern) is None:
            SetuptoolsDeprecationWarning.emit(
                "Please provide a valid glob pattern.",
                "Pattern {pattern!r} contains invalid characters.",
                pattern=pattern,
                see_url=f"https://packaging.python.org/en/latest/{pypa_guides}",
```
