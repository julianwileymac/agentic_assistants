# Chunk: d7cafaf991d7_3

- source: `.venv-lab/Lib/site-packages/jedi/inference/base_value.py`
- lines: 232-322
- chunk: 4/7

```
       return default

    def execute_operation(self, other, operator):
        debug.warning("%s not possible between %s and %s", operator, self, other)
        return NO_VALUES

    def py__call__(self, arguments):
        debug.warning("no execution possible %s", self)
        return NO_VALUES

    def py__stop_iteration_returns(self):
        debug.warning("Not possible to return the stop iterations of %s", self)
        return NO_VALUES

    def py__getattribute__alternatives(self, name_or_str):
        """
        For now a way to add values in cases like __getattr__.
        """
        return NO_VALUES

    def py__get__(self, instance, class_value):
        debug.warning("No __get__ defined on %s", self)
        return ValueSet([self])

    def py__get__on_class(self, calling_instance, instance, class_value):
        return NotImplemented

    def get_qualified_names(self):
        # Returns Optional[Tuple[str, ...]]
        return None

    def is_stub(self):
        # The root value knows if it's a stub or not.
        return self.parent_context.is_stub()

    def _as_context(self):
        raise HasNoContext

    @property
    def name(self):
        raise NotImplementedError

    def get_type_hint(self, add_class_info=True):
        return None

    def infer_type_vars(self, value_set):
        """
        When the current instance represents a type annotation, this method
        tries to find information about undefined type vars and returns a dict
        from type var name to value set.

        This is for example important to understand what `iter([1])` returns.
        According to typeshed, `iter` returns an `Iterator[_T]`:

            def iter(iterable: Iterable[_T]) -> Iterator[_T]: ...

        This functions would generate `int` for `_T` in this case, because it
        unpacks the `Iterable`.

        Parameters
        ----------

        `self`: represents the annotation of the current parameter to infer the
            value for. In the above example, this would initially be the
            `Iterable[_T]` of the `iterable` parameter and then, when recursing,
            just the `_T` generic parameter.

        `value_set`: represents the actual argument passed to the parameter
            we're inferred for, or (for recursive calls) their types. In the
            above example this would first be the representation of the list
            `[1]` and then, when recursing, just of `1`.
        """
        return {}


def iterate_values(values, contextualized_node=None, is_async=False):
    """
    Calls `iterate`, on all values but ignores the ordering and just returns
    all values that the iterate functions yield.
    """
    return ValueSet.from_sets(
        lazy_value.infer()
        for lazy_value in values.iterate(contextualized_node, is_async=is_async)
    )


class _ValueWrapperBase(HelperValueMixin):
    @safe_property
    def name(self):
        from jedi.inference.names import ValueName
```
