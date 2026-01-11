# Chunk: 8eb2c67fee2e_2

- source: `.venv-lab/Lib/site-packages/setuptools/dist.py`
- lines: 153-243
- chunk: 3/17

```
marker: {marker} ({extra!r})"
        raise DistutilsSetupError(msg) from None
    list(_reqs.parse(reqs))


def _check_marker(marker):
    if not marker:
        return
    m = Marker(marker)
    m.evaluate()


def assert_bool(dist, attr, value):
    """Verify that value is True, False, 0, or 1"""
    if bool(value) != value:
        raise DistutilsSetupError(f"{attr!r} must be a boolean value (got {value!r})")


def invalid_unless_false(dist, attr, value):
    if not value:
        DistDeprecationWarning.emit(f"{attr} is ignored.")
        # TODO: should there be a `due_date` here?
        return
    raise DistutilsSetupError(f"{attr} is invalid.")


def check_requirements(dist, attr: str, value: _OrderedStrSequence) -> None:
    """Verify that install_requires is a valid requirements list"""
    try:
        list(_reqs.parse(value))
        if isinstance(value, set):
            raise TypeError("Unordered types are not allowed")
    except (TypeError, ValueError) as error:
        msg = (
            f"{attr!r} must be a string or iterable of strings "
            f"containing valid project/version requirement specifiers; {error}"
        )
        raise DistutilsSetupError(msg) from error


def check_specifier(dist, attr, value):
    """Verify that value is a valid version specifier"""
    try:
        SpecifierSet(value)
    except (InvalidSpecifier, AttributeError) as error:
        msg = f"{attr!r} must be a string containing valid version specifiers; {error}"
        raise DistutilsSetupError(msg) from error


def check_entry_points(dist, attr, value):
    """Verify that entry_points map is parseable"""
    try:
        _entry_points.load(value)
    except Exception as e:
        raise DistutilsSetupError(e) from e


def check_package_data(dist, attr, value):
    """Verify that value is a dictionary of package names to glob lists"""
    if not isinstance(value, dict):
        raise DistutilsSetupError(
            f"{attr!r} must be a dictionary mapping package names to lists of "
            "string wildcard patterns"
        )
    for k, v in value.items():
        if not isinstance(k, str):
            raise DistutilsSetupError(
                f"keys of {attr!r} dict must be strings (got {k!r})"
            )
        assert_string_list(dist, f'values of {attr!r} dict', v)


def check_packages(dist, attr, value):
    for pkgname in value:
        if not re.match(r'\w+(\.\w+)*', pkgname):
            distutils.log.warn(
                "WARNING: %r not a valid package name; please use only "
                ".-separated package names in setup.py",
                pkgname,
            )


if TYPE_CHECKING:
    # Work around a mypy issue where type[T] can't be used as a base: https://github.com/python/mypy/issues/10962
    from distutils.core import Distribution as _Distribution
else:
    _Distribution = get_unpatched(distutils.core.Distribution)


class Distribution(_Distribution):
```
