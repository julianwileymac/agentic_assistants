# Chunk: d917abc63eda_3

- source: `.venv-lab/Lib/site-packages/attrs-25.4.0.dist-info/METADATA`
- lines: 190-236
- chunk: 4/4

```
ld(default=1, kw_only=False)

  @attrs.define
  class Subclass(Base):
      c: int
  ```

  Here, we have a `kw_only=True` *attrs* class (`Base`) with an attribute that sets `kw_only=False` and has a default (`Base.b`), and then create a subclass (`Subclass`) with required arguments (`Subclass.c`).
  Previously this would work, since it would make `Base.b` keyword-only, but now this fails since `Base.b` is positional, and we have a required positional argument (`Subclass.c`) following another argument with defaults.
  [#1457](https://github.com/python-attrs/attrs/issues/1457)


### Changes

- Values passed to the `__init__()` method of `attrs` classes are now correctly passed to `__attrs_pre_init__()` instead of their default values (in cases where *kw_only* was not specified).
  [#1427](https://github.com/python-attrs/attrs/issues/1427)
- Added support for Python 3.14 and [PEP 749](https://peps.python.org/pep-0749/).
  [#1446](https://github.com/python-attrs/attrs/issues/1446),
  [#1451](https://github.com/python-attrs/attrs/issues/1451)
- `attrs.validators.deep_mapping()` now allows to leave out either *key_validator* xor *value_validator*.
  [#1448](https://github.com/python-attrs/attrs/issues/1448)
- `attrs.validators.deep_iterator()` and `attrs.validators.deep_mapping()` now accept lists and tuples for all validators and wrap them into a `attrs.validators.and_()`.
  [#1449](https://github.com/python-attrs/attrs/issues/1449)
- Added a new **experimental** way to inspect classes:

  `attrs.inspect(cls)` returns the _effective_ class-wide parameters that were used by *attrs* to construct the class.

  The returned class is the same data structure that *attrs* uses internally to decide how to construct the final class.
  [#1454](https://github.com/python-attrs/attrs/issues/1454)
- Fixed annotations for `attrs.field(converter=...)`.
  Previously, a `tuple` of converters was only accepted if it had exactly one element.
  [#1461](https://github.com/python-attrs/attrs/issues/1461)
- The performance of `attrs.asdict()` has been improved by 45–260%.
  [#1463](https://github.com/python-attrs/attrs/issues/1463)
- The performance of `attrs.astuple()` has been improved by 49–270%.
  [#1469](https://github.com/python-attrs/attrs/issues/1469)
- The type annotation for `attrs.validators.or_()` now allows for different types of validators.

  This was only an issue on Pyright.
  [#1474](https://github.com/python-attrs/attrs/issues/1474)



---

[Full changelog →](https://www.attrs.org/en/stable/changelog.html)
```
