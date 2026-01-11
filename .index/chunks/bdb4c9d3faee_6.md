# Chunk: bdb4c9d3faee_6

- source: `.venv-lab/Lib/site-packages/pip/_vendor/pkg_resources/__init__.py`
- lines: 548-628
- chunk: 7/47

```
`dist` or raise ImportError"""
    return get_distribution(dist).load_entry_point(group, name)


@overload
def get_entry_map(
    dist: _EPDistType, group: None = None
) -> dict[str, dict[str, EntryPoint]]: ...
@overload
def get_entry_map(dist: _EPDistType, group: str) -> dict[str, EntryPoint]: ...
def get_entry_map(dist: _EPDistType, group: str | None = None):
    """Return the entry point map for `group`, or the full entry map"""
    return get_distribution(dist).get_entry_map(group)


def get_entry_info(dist: _EPDistType, group: str, name: str):
    """Return the EntryPoint object for `group`+`name`, or ``None``"""
    return get_distribution(dist).get_entry_info(group, name)


class IMetadataProvider(Protocol):
    def has_metadata(self, name: str) -> bool:
        """Does the package's distribution contain the named metadata?"""

    def get_metadata(self, name: str) -> str:
        """The named metadata resource as a string"""

    def get_metadata_lines(self, name: str) -> Iterator[str]:
        """Yield named metadata resource as list of non-blank non-comment lines

        Leading and trailing whitespace is stripped from each line, and lines
        with ``#`` as the first non-blank character are omitted."""

    def metadata_isdir(self, name: str) -> bool:
        """Is the named metadata a directory?  (like ``os.path.isdir()``)"""

    def metadata_listdir(self, name: str) -> list[str]:
        """List of metadata names in the directory (like ``os.listdir()``)"""

    def run_script(self, script_name: str, namespace: dict[str, Any]) -> None:
        """Execute the named script in the supplied namespace dictionary"""


class IResourceProvider(IMetadataProvider, Protocol):
    """An object that provides access to package resources"""

    def get_resource_filename(
        self, manager: ResourceManager, resource_name: str
    ) -> str:
        """Return a true filesystem path for `resource_name`

        `manager` must be a ``ResourceManager``"""

    def get_resource_stream(
        self, manager: ResourceManager, resource_name: str
    ) -> _ResourceStream:
        """Return a readable file-like object for `resource_name`

        `manager` must be a ``ResourceManager``"""

    def get_resource_string(
        self, manager: ResourceManager, resource_name: str
    ) -> bytes:
        """Return the contents of `resource_name` as :obj:`bytes`

        `manager` must be a ``ResourceManager``"""

    def has_resource(self, resource_name: str) -> bool:
        """Does the package contain the named resource?"""

    def resource_isdir(self, resource_name: str) -> bool:
        """Is the named resource a directory?  (like ``os.path.isdir()``)"""

    def resource_listdir(self, resource_name: str) -> list[str]:
        """List of resource names in the directory (like ``os.listdir()``)"""


class WorkingSet:
    """A collection of active distributions on sys.path (or a similar list)"""
```
