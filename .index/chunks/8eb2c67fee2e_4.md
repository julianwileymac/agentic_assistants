# Chunk: 8eb2c67fee2e_4

- source: `.venv-lab/Lib/site-packages/setuptools/dist.py`
- lines: 283-354
- chunk: 5/17

```
exclude()' methods can be thought of as in-place add and subtract
    commands that add or remove packages, modules, extensions, and so on from
    the distribution.
    """

    _DISTUTILS_UNSUPPORTED_METADATA = {
        'long_description_content_type': lambda: None,
        'project_urls': dict,
        'provides_extras': dict,  # behaves like an ordered set
        'license_expression': lambda: None,
        'license_file': lambda: None,
        'license_files': lambda: None,
        'install_requires': list,
        'extras_require': dict,
    }

    # Used by build_py, editable_wheel and install_lib commands for legacy namespaces
    namespace_packages: list[str]  #: :meta private: DEPRECATED

    # Any: Dynamic assignment results in Incompatible types in assignment
    def __init__(self, attrs: MutableMapping[str, Any] | None = None) -> None:
        have_package_data = hasattr(self, "package_data")
        if not have_package_data:
            self.package_data: dict[str, list[str]] = {}
        attrs = attrs or {}
        self.dist_files: list[tuple[str, str, str]] = []
        self.include_package_data: bool | None = None
        self.exclude_package_data: dict[str, list[str]] | None = None
        # Filter-out setuptools' specific options.
        self.src_root: str | None = attrs.pop("src_root", None)
        self.dependency_links: list[str] = attrs.pop('dependency_links', [])
        self.setup_requires: list[str] = attrs.pop('setup_requires', [])
        for ep in metadata.entry_points(group='distutils.setup_keywords'):
            vars(self).setdefault(ep.name, None)

        metadata_only = set(self._DISTUTILS_UNSUPPORTED_METADATA)
        metadata_only -= {"install_requires", "extras_require"}
        dist_attrs = {k: v for k, v in attrs.items() if k not in metadata_only}
        _Distribution.__init__(self, dist_attrs)

        # Private API (setuptools-use only, not restricted to Distribution)
        # Stores files that are referenced by the configuration and need to be in the
        # sdist (e.g. `version = file: VERSION.txt`)
        self._referenced_files = set[str]()

        self.set_defaults = ConfigDiscovery(self)

        self._set_metadata_defaults(attrs)

        self.metadata.version = self._normalize_version(self.metadata.version)
        self._finalize_requires()

    def _validate_metadata(self):
        required = {"name"}
        provided = {
            key
            for key in vars(self.metadata)
            if getattr(self.metadata, key, None) is not None
        }
        missing = required - provided

        if missing:
            msg = f"Required package metadata is missing: {missing}"
            raise DistutilsSetupError(msg)

    def _set_metadata_defaults(self, attrs):
        """
        Fill-in missing metadata fields not supported by distutils.
        Some fields may have been set by other tools (e.g. pbr).
        Those fields (vars(self.metadata)) take precedence to
        supplied attrs.
```
