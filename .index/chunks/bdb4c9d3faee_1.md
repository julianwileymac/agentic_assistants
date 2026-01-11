# Chunk: bdb4c9d3faee_1

- source: `.venv-lab/Lib/site-packages/pip/_vendor/pkg_resources/__init__.py`
- lines: 106-204
- chunk: 2/47

```
ove deprecation warning from vendored pkg_resources.
# Setting PYTHONWARNINGS=error to verify builds produce no warnings
# causes immediate exceptions.
# See https://github.com/pypa/pip/issues/12243


_T = TypeVar("_T")
_DistributionT = TypeVar("_DistributionT", bound="Distribution")
# Type aliases
_NestedStr = Union[str, Iterable[Union[str, Iterable["_NestedStr"]]]]
_InstallerTypeT = Callable[["Requirement"], "_DistributionT"]
_InstallerType = Callable[["Requirement"], Union["Distribution", None]]
_PkgReqType = Union[str, "Requirement"]
_EPDistType = Union["Distribution", _PkgReqType]
_MetadataType = Union["IResourceProvider", None]
_ResolvedEntryPoint = Any  # Can be any attribute in the module
_ResourceStream = Any  # TODO / Incomplete: A readable file-like object
# Any object works, but let's indicate we expect something like a module (optionally has __loader__ or __file__)
_ModuleLike = Union[object, types.ModuleType]
# Any: Should be _ModuleLike but we end up with issues where _ModuleLike doesn't have _ZipLoaderModule's __loader__
_ProviderFactoryType = Callable[[Any], "IResourceProvider"]
_DistFinderType = Callable[[_T, str, bool], Iterable["Distribution"]]
_NSHandlerType = Callable[[_T, str, str, types.ModuleType], Union[str, None]]
_AdapterT = TypeVar(
    "_AdapterT", _DistFinderType[Any], _ProviderFactoryType, _NSHandlerType[Any]
)


# Use _typeshed.importlib.LoaderProtocol once available https://github.com/python/typeshed/pull/11890
class _LoaderProtocol(Protocol):
    def load_module(self, fullname: str, /) -> types.ModuleType: ...


class _ZipLoaderModule(Protocol):
    __loader__: zipimport.zipimporter


_PEP440_FALLBACK = re.compile(r"^v?(?P<safe>(?:[0-9]+!)?[0-9]+(?:\.[0-9]+)*)", re.I)


class PEP440Warning(RuntimeWarning):
    """
    Used when there is an issue with a version or specifier not complying with
    PEP 440.
    """


parse_version = _packaging_version.Version


_state_vars: dict[str, str] = {}


def _declare_state(vartype: str, varname: str, initial_value: _T) -> _T:
    _state_vars[varname] = vartype
    return initial_value


def __getstate__() -> dict[str, Any]:
    state = {}
    g = globals()
    for k, v in _state_vars.items():
        state[k] = g['_sget_' + v](g[k])
    return state


def __setstate__(state: dict[str, Any]) -> dict[str, Any]:
    g = globals()
    for k, v in state.items():
        g['_sset_' + _state_vars[k]](k, g[k], v)
    return state


def _sget_dict(val):
    return val.copy()


def _sset_dict(key, ob, state):
    ob.clear()
    ob.update(state)


def _sget_object(val):
    return val.__getstate__()


def _sset_object(key, ob, state):
    ob.__setstate__(state)


_sget_none = _sset_none = lambda *args: None


def get_supported_platform():
    """Return this platform's maximum compatible version.

    distutils.util.get_platform() normally reports the minimum version
    of macOS that would be required to *use* extensions produced by
```
