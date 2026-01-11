# Chunk: aa1ac86ee9e0_4

- source: `.venv-lab/Lib/site-packages/ipywidgets/widgets/interaction.py`
- lines: 282-362
- chunk: 5/8

```
 []
        for name, abbrev, default in seq:
            if isinstance(abbrev, Widget) and (not isinstance(abbrev, ValueWidget)):
                raise TypeError("{!r} is not a ValueWidget".format(abbrev))
            widget = self.widget_from_abbrev(abbrev, default)
            if widget is None:
                raise ValueError("{!r} cannot be transformed to a widget".format(abbrev))
            if not hasattr(widget, "description") or not widget.description:
                widget.description = name
            widget._kwarg = name
            result.append(widget)
        return result

    @classmethod
    def widget_from_abbrev(cls, abbrev, default=empty):
        """Build a ValueWidget instance given an abbreviation or Widget."""
        if isinstance(abbrev, ValueWidget) or isinstance(abbrev, fixed):
            return abbrev

        if isinstance(abbrev, tuple):
            widget = cls.widget_from_tuple(abbrev)
            if default is not empty:
                try:
                    widget.value = default
                except Exception:
                    # ignore failure to set default
                    pass
            return widget
        
        # Try type annotation
        if isinstance(abbrev, type):
            widget = cls.widget_from_annotation(abbrev)
            if widget is not None:
                return widget

        # Try single value
        widget = cls.widget_from_single_value(abbrev)
        if widget is not None:
            return widget

        # Something iterable (list, dict, generator, ...). Note that str and
        # tuple should be handled before, that is why we check this case last.
        if isinstance(abbrev, Iterable):
            widget = cls.widget_from_iterable(abbrev)
            if default is not empty:
                try:
                    widget.value = default
                except Exception:
                    # ignore failure to set default
                    pass
            return widget

        # No idea...
        return None

    @staticmethod
    def widget_from_single_value(o):
        """Make widgets from single values, which can be used as parameter defaults."""
        if isinstance(o, str):
            return Text(value=str(o))
        elif isinstance(o, bool):
            return Checkbox(value=o)
        elif isinstance(o, Integral):
            min, max, value = _get_min_max_value(None, None, o)
            return IntSlider(value=o, min=min, max=max)
        elif isinstance(o, Real):
            min, max, value = _get_min_max_value(None, None, o)
            return FloatSlider(value=o, min=min, max=max)
        else:
            return None

    @staticmethod
    def widget_from_annotation(t):
        """Make widgets from type annotation and optional default value."""
        if t is str:
            return Text()
        elif t is bool:
            return Checkbox()
        elif t in {int, Integral}:
            return IntText()
```
