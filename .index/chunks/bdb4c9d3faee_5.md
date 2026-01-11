# Chunk: bdb4c9d3faee_5

- source: `.venv-lab/Lib/site-packages/pip/_vendor/pkg_resources/__init__.py`
- lines: 477-558
- chunk: 6/47

```
+)\.(\d+)-(.*)")
# XXX backward compat
get_platform = get_build_platform


def compatible_platforms(provided: str | None, required: str | None):
    """Can code for the `provided` platform run on the `required` platform?

    Returns true if either platform is ``None``, or the platforms are equal.

    XXX Needs compatibility checks for Linux and other unixy OSes.
    """
    if provided is None or required is None or provided == required:
        # easy case
        return True

    # macOS special cases
    reqMac = macosVersionString.match(required)
    if reqMac:
        provMac = macosVersionString.match(provided)

        # is this a Mac package?
        if not provMac:
            # this is backwards compatibility for packages built before
            # setuptools 0.6. All packages built after this point will
            # use the new macOS designation.
            provDarwin = darwinVersionString.match(provided)
            if provDarwin:
                dversion = int(provDarwin.group(1))
                macosversion = "%s.%s" % (reqMac.group(1), reqMac.group(2))
                if (
                    dversion == 7
                    and macosversion >= "10.3"
                    or dversion == 8
                    and macosversion >= "10.4"
                ):
                    return True
            # egg isn't macOS or legacy darwin
            return False

        # are they the same major version and machine type?
        if provMac.group(1) != reqMac.group(1) or provMac.group(3) != reqMac.group(3):
            return False

        # is the required OS major update >= the provided one?
        if int(provMac.group(2)) > int(reqMac.group(2)):
            return False

        return True

    # XXX Linux and other platforms' special cases should go here
    return False


@overload
def get_distribution(dist: _DistributionT) -> _DistributionT: ...
@overload
def get_distribution(dist: _PkgReqType) -> Distribution: ...
def get_distribution(dist: Distribution | _PkgReqType) -> Distribution:
    """Return a current distribution object for a Requirement or string"""
    if isinstance(dist, str):
        dist = Requirement.parse(dist)
    if isinstance(dist, Requirement):
        # Bad type narrowing, dist has to be a Requirement here, so get_provider has to return Distribution
        dist = get_provider(dist)  # type: ignore[assignment]
    if not isinstance(dist, Distribution):
        raise TypeError("Expected str, Requirement, or Distribution", dist)
    return dist


def load_entry_point(dist: _EPDistType, group: str, name: str) -> _ResolvedEntryPoint:
    """Return `name` entry point of `group` for `dist` or raise ImportError"""
    return get_distribution(dist).load_entry_point(group, name)


@overload
def get_entry_map(
    dist: _EPDistType, group: None = None
) -> dict[str, dict[str, EntryPoint]]: ...
@overload
def get_entry_map(dist: _EPDistType, group: str) -> dict[str, EntryPoint]: ...
```
