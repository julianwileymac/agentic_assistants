# Chunk: 8eb2c67fee2e_6

- source: `.venv-lab/Lib/site-packages/setuptools/dist.py`
- lines: 411-471
- chunk: 7/17

```
static.is_static(dist.metadata.license_expression)
        True
        >>> dist._finalize_license_expression()
        >>> _static.is_static(dist.metadata.license_expression)  # preserve "static-ness"
        True
        >>> print(dist.metadata.license_expression)
        MIT AND GPL-3.0-or-later
        """
        classifiers = self.metadata.get_classifiers()
        license_classifiers = [cl for cl in classifiers if cl.startswith("License :: ")]

        license_expr = self.metadata.license_expression
        if license_expr:
            str_ = _static.Str if _static.is_static(license_expr) else str
            normalized = str_(_canonicalize_license_expression(license_expr))
            if license_expr != normalized:
                InformationOnly.emit(f"Normalizing '{license_expr}' to '{normalized}'")
                self.metadata.license_expression = normalized
            if license_classifiers:
                raise InvalidConfigError(
                    "License classifiers have been superseded by license expressions "
                    "(see https://peps.python.org/pep-0639/). Please remove:\n\n"
                    + "\n".join(license_classifiers),
                )
        elif license_classifiers:
            pypa_guides = "guides/writing-pyproject-toml/#license"
            SetuptoolsDeprecationWarning.emit(
                "License classifiers are deprecated.",
                "Please consider removing the following classifiers in favor of a "
                "SPDX license expression:\n\n" + "\n".join(license_classifiers),
                see_url=f"https://packaging.python.org/en/latest/{pypa_guides}",
                # Warning introduced on 2025-02-17
                # TODO: Should we add a due date? It may affect old/unmaintained
                #       packages in the ecosystem and cause problems...
            )

    def _finalize_license_files(self) -> None:
        """Compute names of all license files which should be included."""
        license_files: list[str] | None = self.metadata.license_files
        patterns = license_files or []

        license_file: str | None = self.metadata.license_file
        if license_file and license_file not in patterns:
            patterns.append(license_file)

        if license_files is None and license_file is None:
            # Default patterns match the ones wheel uses
            # See https://wheel.readthedocs.io/en/stable/user_guide.html
            # -> 'Including license files in the generated wheel file'
            patterns = ['LICEN[CS]E*', 'COPYING*', 'NOTICE*', 'AUTHORS*']
            files = self._expand_patterns(patterns, enforce_match=False)
        else:  # Patterns explicitly given by the user
            files = self._expand_patterns(patterns, enforce_match=True)

        self.metadata.license_files = list(unique_everseen(files))

    @classmethod
    def _expand_patterns(
        cls, patterns: list[str], enforce_match: bool = True
    ) -> Iterator[str]:
```
