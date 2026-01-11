# Chunk: d917abc63eda_2

- source: `.venv-lab/Lib/site-packages/attrs-25.4.0.dist-info/METADATA`
- lines: 141-198
- chunk: 3/4

```
_number = field(default=42)
    list_of_numbers = field(factory=list)
```


## Data Classes

On the tin, *attrs* might remind you of `dataclasses` (and indeed, `dataclasses` [are a descendant](https://hynek.me/articles/import-attrs/) of *attrs*).
In practice it does a lot more and is more flexible.
For instance, it allows you to define [special handling of NumPy arrays for equality checks](https://www.attrs.org/en/stable/comparison.html#customization), allows more ways to [plug into the initialization process](https://www.attrs.org/en/stable/init.html#hooking-yourself-into-initialization), has a replacement for `__init_subclass__`, and allows for stepping through the generated methods using a debugger.

For more details, please refer to our [comparison page](https://www.attrs.org/en/stable/why.html#data-classes), but generally speaking, we are more likely to commit crimes against nature to make things work that one would expect to work, but that are quite complicated in practice.


## Project Information

- [**Changelog**](https://www.attrs.org/en/stable/changelog.html)
- [**Documentation**](https://www.attrs.org/)
- [**PyPI**](https://pypi.org/project/attrs/)
- [**Source Code**](https://github.com/python-attrs/attrs)
- [**Contributing**](https://github.com/python-attrs/attrs/blob/main/.github/CONTRIBUTING.md)
- [**Third-party Extensions**](https://github.com/python-attrs/attrs/wiki/Extensions-to-attrs)
- **Get Help**: use the `python-attrs` tag on [Stack Overflow](https://stackoverflow.com/questions/tagged/python-attrs)


### *attrs* for Enterprise

Available as part of the [Tidelift Subscription](https://tidelift.com/?utm_source=lifter&utm_medium=referral&utm_campaign=hynek).

The maintainers of *attrs* and thousands of other packages are working with Tidelift to deliver commercial support and maintenance for the open source packages you use to build your applications.
Save time, reduce risk, and improve code health, while paying the maintainers of the exact packages you use.

## Release Information

### Backwards-incompatible Changes

- Class-level `kw_only=True` behavior is now consistent with `dataclasses`.

  Previously, a class that sets `kw_only=True` makes all attributes keyword-only, including those from base classes.
  If an attribute sets `kw_only=False`, that setting is ignored, and it is still made keyword-only.

  Now, only the attributes defined in that class that doesn't explicitly set `kw_only=False` are made keyword-only.

  This shouldn't be a problem for most users, unless you have a pattern like this:

  ```python
  @attrs.define(kw_only=True)
  class Base:
      a: int
      b: int = attrs.field(default=1, kw_only=False)

  @attrs.define
  class Subclass(Base):
      c: int
  ```

  Here, we have a `kw_only=True` *attrs* class (`Base`) with an attribute that sets `kw_only=False` and has a default (`Base.b`), and then create a subclass (`Subclass`) with required arguments (`Subclass.c`).
```
