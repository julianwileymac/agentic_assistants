# Chunk: bdb4c9d3faee_16

- source: `.venv-lab/Lib/site-packages/pip/_vendor/pkg_resources/__init__.py`
- lines: 1266-1355
- chunk: 17/47

```
requirement: Requirement,
        installer: Callable[[Requirement], None] | None = None,
    ) -> None: ...
    @overload
    def obtain(
        self,
        requirement: Requirement,
        installer: _InstallerType | None = None,
    ) -> Distribution | None: ...
    def obtain(
        self,
        requirement: Requirement,
        installer: Callable[[Requirement], None]
        | _InstallerType
        | None
        | _InstallerTypeT[_DistributionT] = None,
    ) -> Distribution | None:
        """Obtain a distribution matching `requirement` (e.g. via download)

        Obtain a distro that matches requirement (e.g. via download).  In the
        base ``Environment`` class, this routine just returns
        ``installer(requirement)``, unless `installer` is None, in which case
        None is returned instead.  This method is a hook that allows subclasses
        to attempt other ways of obtaining a distribution before falling back
        to the `installer` argument."""
        return installer(requirement) if installer else None

    def __iter__(self) -> Iterator[str]:
        """Yield the unique project names of the available distributions"""
        for key in self._distmap.keys():
            if self[key]:
                yield key

    def __iadd__(self, other: Distribution | Environment):
        """In-place addition of a distribution or environment"""
        if isinstance(other, Distribution):
            self.add(other)
        elif isinstance(other, Environment):
            for project in other:
                for dist in other[project]:
                    self.add(dist)
        else:
            raise TypeError("Can't add %r to environment" % (other,))
        return self

    def __add__(self, other: Distribution | Environment):
        """Add an environment or distribution to an environment"""
        new = self.__class__([], platform=None, python=None)
        for env in self, other:
            new += env
        return new


# XXX backward compatibility
AvailableDistributions = Environment


class ExtractionError(RuntimeError):
    """An error occurred extracting a resource

    The following attributes are available from instances of this exception:

    manager
        The resource manager that raised this exception

    cache_path
        The base directory for resource extraction

    original_error
        The exception instance that caused extraction to fail
    """

    manager: ResourceManager
    cache_path: str
    original_error: BaseException | None


class ResourceManager:
    """Manage resource extraction and packages"""

    extraction_path: str | None = None

    def __init__(self):
        self.cached_files = {}

    def resource_exists(self, package_or_requirement: _PkgReqType, resource_name: str):
        """Does the named resource exist?"""
        return get_provider(package_or_requirement).has_resource(resource_name)
```
