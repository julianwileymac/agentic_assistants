# Chunk: d7cafaf991d7_6

- source: `.venv-lab/Lib/site-packages/jedi/inference/base_value.py`
- lines: 489-559
- chunk: 7/7

```
ute_with_values(self, *args, **kwargs):
        return ValueSet.from_sets(c.execute_with_values(*args, **kwargs) for c in self._set)

    def goto(self, *args, **kwargs):
        return reduce(add, [c.goto(*args, **kwargs) for c in self._set], [])

    def py__getattribute__(self, *args, **kwargs):
        return ValueSet.from_sets(c.py__getattribute__(*args, **kwargs) for c in self._set)

    def get_item(self, *args, **kwargs):
        return ValueSet.from_sets(_getitem(c, *args, **kwargs) for c in self._set)

    def try_merge(self, function_name):
        value_set = self.__class__([])
        for c in self._set:
            try:
                method = getattr(c, function_name)
            except AttributeError:
                pass
            else:
                value_set |= method()
        return value_set

    def gather_annotation_classes(self):
        return ValueSet.from_sets([c.gather_annotation_classes() for c in self._set])

    def get_signatures(self):
        return [sig for c in self._set for sig in c.get_signatures()]

    def get_type_hint(self, add_class_info=True):
        t = [v.get_type_hint(add_class_info=add_class_info) for v in self._set]
        type_hints = sorted(filter(None, t))
        if len(type_hints) == 1:
            return type_hints[0]

        optional = 'None' in type_hints
        if optional:
            type_hints.remove('None')

        if len(type_hints) == 0:
            return None
        elif len(type_hints) == 1:
            s = type_hints[0]
        else:
            s = 'Union[%s]' % ', '.join(type_hints)
        if optional:
            s = 'Optional[%s]' % s
        return s

    def infer_type_vars(self, value_set):
        # Circular
        from jedi.inference.gradual.annotation import merge_type_var_dicts

        type_var_dict = {}
        for value in self._set:
            merge_type_var_dicts(
                type_var_dict,
                value.infer_type_vars(value_set),
            )
        return type_var_dict


NO_VALUES = ValueSet([])


def iterator_to_value_set(func):
    def wrapper(*args, **kwargs):
        return ValueSet(func(*args, **kwargs))

    return wrapper
```
