# Chunk: 8eb2c67fee2e_5

- source: `.venv-lab/Lib/site-packages/setuptools/dist.py`
- lines: 346-418
- chunk: 6/17

```
stutilsSetupError(msg)

    def _set_metadata_defaults(self, attrs):
        """
        Fill-in missing metadata fields not supported by distutils.
        Some fields may have been set by other tools (e.g. pbr).
        Those fields (vars(self.metadata)) take precedence to
        supplied attrs.
        """
        for option, default in self._DISTUTILS_UNSUPPORTED_METADATA.items():
            vars(self.metadata).setdefault(option, attrs.get(option, default()))

    @staticmethod
    def _normalize_version(version):
        from . import sic

        if isinstance(version, numbers.Number):
            # Some people apparently take "version number" too literally :)
            version = str(version)
        elif isinstance(version, sic) or version is None:
            return version

        normalized = str(Version(version))
        if version != normalized:
            InformationOnly.emit(f"Normalizing '{version}' to '{normalized}'")
            return normalized
        return version

    def _finalize_requires(self):
        """
        Set `metadata.python_requires` and fix environment markers
        in `install_requires` and `extras_require`.
        """
        if getattr(self, 'python_requires', None):
            self.metadata.python_requires = self.python_requires

        self._normalize_requires()
        self.metadata.install_requires = self.install_requires
        self.metadata.extras_require = self.extras_require

        if self.extras_require:
            for extra in self.extras_require.keys():
                # Setuptools allows a weird "<name>:<env markers> syntax for extras
                extra = extra.split(':')[0]
                if extra:
                    self.metadata.provides_extras.setdefault(extra)

    def _normalize_requires(self):
        """Make sure requirement-related attributes exist and are normalized"""
        install_requires = getattr(self, "install_requires", None) or []
        extras_require = getattr(self, "extras_require", None) or {}

        # Preserve the "static"-ness of values parsed from config files
        list_ = _static.List if _static.is_static(install_requires) else list
        self.install_requires = list_(map(str, _reqs.parse(install_requires)))

        dict_ = _static.Dict if _static.is_static(extras_require) else dict
        self.extras_require = dict_(
            (k, list(map(str, _reqs.parse(v or [])))) for k, v in extras_require.items()
        )

    def _finalize_license_expression(self) -> None:
        """
        Normalize license and license_expression.
        >>> dist = Distribution({"license_expression": _static.Str("mit aNd  gpl-3.0-OR-later")})
        >>> _static.is_static(dist.metadata.license_expression)
        True
        >>> dist._finalize_license_expression()
        >>> _static.is_static(dist.metadata.license_expression)  # preserve "static-ness"
        True
        >>> print(dist.metadata.license_expression)
        MIT AND GPL-3.0-or-later
```
