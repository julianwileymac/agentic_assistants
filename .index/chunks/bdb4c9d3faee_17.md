# Chunk: bdb4c9d3faee_17

- source: `.venv-lab/Lib/site-packages/pip/_vendor/pkg_resources/__init__.py`
- lines: 1346-1421
- chunk: 18/47

```
tion_path: str | None = None

    def __init__(self):
        self.cached_files = {}

    def resource_exists(self, package_or_requirement: _PkgReqType, resource_name: str):
        """Does the named resource exist?"""
        return get_provider(package_or_requirement).has_resource(resource_name)

    def resource_isdir(self, package_or_requirement: _PkgReqType, resource_name: str):
        """Is the named resource an existing directory?"""
        return get_provider(package_or_requirement).resource_isdir(resource_name)

    def resource_filename(
        self, package_or_requirement: _PkgReqType, resource_name: str
    ):
        """Return a true filesystem path for specified resource"""
        return get_provider(package_or_requirement).get_resource_filename(
            self, resource_name
        )

    def resource_stream(self, package_or_requirement: _PkgReqType, resource_name: str):
        """Return a readable file-like object for specified resource"""
        return get_provider(package_or_requirement).get_resource_stream(
            self, resource_name
        )

    def resource_string(
        self, package_or_requirement: _PkgReqType, resource_name: str
    ) -> bytes:
        """Return specified resource as :obj:`bytes`"""
        return get_provider(package_or_requirement).get_resource_string(
            self, resource_name
        )

    def resource_listdir(self, package_or_requirement: _PkgReqType, resource_name: str):
        """List the contents of the named resource directory"""
        return get_provider(package_or_requirement).resource_listdir(resource_name)

    def extraction_error(self) -> NoReturn:
        """Give an error message for problems extracting file(s)"""

        old_exc = sys.exc_info()[1]
        cache_path = self.extraction_path or get_default_cache()

        tmpl = textwrap.dedent(
            """
            Can't extract file(s) to egg cache

            The following error occurred while trying to extract file(s)
            to the Python egg cache:

              {old_exc}

            The Python egg cache directory is currently set to:

              {cache_path}

            Perhaps your account does not have write access to this directory?
            You can change the cache directory by setting the PYTHON_EGG_CACHE
            environment variable to point to an accessible directory.
            """
        ).lstrip()
        err = ExtractionError(tmpl.format(**locals()))
        err.manager = self
        err.cache_path = cache_path
        err.original_error = old_exc
        raise err

    def get_cache_path(self, archive_name: str, names: Iterable[StrPath] = ()):
        """Return absolute location in cache for `archive_name` and `names`

        The parent directory of the resulting path will be created if it does
        not already exist.  `archive_name` should be the base filename of the
        enclosing egg (which may not be the name of the enclosing zipfile!),
```
