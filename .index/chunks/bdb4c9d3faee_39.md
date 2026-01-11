# Chunk: bdb4c9d3faee_39

- source: `.venv-lab/Lib/site-packages/pip/_vendor/pkg_resources/__init__.py`
- lines: 3107-3188
- chunk: 40/47

```
ol = False):
        """Ensure distribution is importable on `path` (default=sys.path)"""
        if path is None:
            path = sys.path
        self.insert_on(path, replace=replace)
        if path is sys.path and self.location is not None:
            fixup_namespace_packages(self.location)
            for pkg in self._get_metadata('namespace_packages.txt'):
                if pkg in sys.modules:
                    declare_namespace(pkg)

    def egg_name(self):
        """Return what this distribution's standard .egg filename should be"""
        filename = "%s-%s-py%s" % (
            to_filename(self.project_name),
            to_filename(self.version),
            self.py_version or PY_MAJOR,
        )

        if self.platform:
            filename += '-' + self.platform
        return filename

    def __repr__(self):
        if self.location:
            return "%s (%s)" % (self, self.location)
        else:
            return str(self)

    def __str__(self):
        try:
            version = getattr(self, 'version', None)
        except ValueError:
            version = None
        version = version or "[unknown version]"
        return "%s %s" % (self.project_name, version)

    def __getattr__(self, attr):
        """Delegate all unrecognized public attributes to .metadata provider"""
        if attr.startswith('_'):
            raise AttributeError(attr)
        return getattr(self._provider, attr)

    def __dir__(self):
        return list(
            set(super().__dir__())
            | set(attr for attr in self._provider.__dir__() if not attr.startswith('_'))
        )

    @classmethod
    def from_filename(
        cls,
        filename: StrPath,
        metadata: _MetadataType = None,
        **kw: int,  # We could set `precedence` explicitly, but keeping this as `**kw` for full backwards and subclassing compatibility
    ):
        return cls.from_location(
            _normalize_cached(filename), os.path.basename(filename), metadata, **kw
        )

    def as_requirement(self):
        """Return a ``Requirement`` that matches this distribution exactly"""
        if isinstance(self.parsed_version, _packaging_version.Version):
            spec = "%s==%s" % (self.project_name, self.parsed_version)
        else:
            spec = "%s===%s" % (self.project_name, self.parsed_version)

        return Requirement.parse(spec)

    def load_entry_point(self, group: str, name: str) -> _ResolvedEntryPoint:
        """Return the `name` entry point of `group` or raise ImportError"""
        ep = self.get_entry_info(group, name)
        if ep is None:
            raise ImportError("Entry point %r not found" % ((group, name),))
        return ep.load()

    @overload
    def get_entry_map(self, group: None = None) -> dict[str, dict[str, EntryPoint]]: ...
    @overload
    def get_entry_map(self, group: str) -> dict[str, EntryPoint]: ...
    def get_entry_map(self, group: str | None = None):
```
