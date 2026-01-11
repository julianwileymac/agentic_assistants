# Chunk: bdb4c9d3faee_21

- source: `.venv-lab/Lib/site-packages/pip/_vendor/pkg_resources/__init__.py`
- lines: 1624-1707
- chunk: 22/47

```
ng' module.
    """
    try:
        marker = _packaging_markers.Marker(text)
        return marker.evaluate()
    except _packaging_markers.InvalidMarker as e:
        raise SyntaxError(e) from e


class NullProvider:
    """Try to implement resources and metadata for arbitrary PEP 302 loaders"""

    egg_name: str | None = None
    egg_info: str | None = None
    loader: _LoaderProtocol | None = None

    def __init__(self, module: _ModuleLike):
        self.loader = getattr(module, '__loader__', None)
        self.module_path = os.path.dirname(getattr(module, '__file__', ''))

    def get_resource_filename(self, manager: ResourceManager, resource_name: str):
        return self._fn(self.module_path, resource_name)

    def get_resource_stream(self, manager: ResourceManager, resource_name: str):
        return io.BytesIO(self.get_resource_string(manager, resource_name))

    def get_resource_string(
        self, manager: ResourceManager, resource_name: str
    ) -> bytes:
        return self._get(self._fn(self.module_path, resource_name))

    def has_resource(self, resource_name: str):
        return self._has(self._fn(self.module_path, resource_name))

    def _get_metadata_path(self, name):
        return self._fn(self.egg_info, name)

    def has_metadata(self, name: str) -> bool:
        if not self.egg_info:
            return False

        path = self._get_metadata_path(name)
        return self._has(path)

    def get_metadata(self, name: str):
        if not self.egg_info:
            return ""
        path = self._get_metadata_path(name)
        value = self._get(path)
        try:
            return value.decode('utf-8')
        except UnicodeDecodeError as exc:
            # Include the path in the error message to simplify
            # troubleshooting, and without changing the exception type.
            exc.reason += ' in {} file at path: {}'.format(name, path)
            raise

    def get_metadata_lines(self, name: str) -> Iterator[str]:
        return yield_lines(self.get_metadata(name))

    def resource_isdir(self, resource_name: str):
        return self._isdir(self._fn(self.module_path, resource_name))

    def metadata_isdir(self, name: str) -> bool:
        return bool(self.egg_info and self._isdir(self._fn(self.egg_info, name)))

    def resource_listdir(self, resource_name: str):
        return self._listdir(self._fn(self.module_path, resource_name))

    def metadata_listdir(self, name: str) -> list[str]:
        if self.egg_info:
            return self._listdir(self._fn(self.egg_info, name))
        return []

    def run_script(self, script_name: str, namespace: dict[str, Any]):
        script = 'scripts/' + script_name
        if not self.has_metadata(script):
            raise ResolutionError(
                "Script {script!r} not found in metadata at {self.egg_info!r}".format(
                    **locals()
                ),
            )
```
