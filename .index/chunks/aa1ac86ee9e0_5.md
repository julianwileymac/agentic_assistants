# Chunk: aa1ac86ee9e0_5

- source: `.venv-lab/Lib/site-packages/ipywidgets/widgets/interaction.py`
- lines: 351-441
- chunk: 6/8

```
None

    @staticmethod
    def widget_from_annotation(t):
        """Make widgets from type annotation and optional default value."""
        if t is str:
            return Text()
        elif t is bool:
            return Checkbox()
        elif t in {int, Integral}:
            return IntText()
        elif t in {float, Real}:
            return FloatText()
        elif isinstance(t, EnumType):
            return Dropdown(options={option.name: option for option in t})
        else:
            return None

    @staticmethod
    def widget_from_tuple(o):
        """Make widgets from a tuple abbreviation."""
        if _matches(o, (Real, Real)):
            min, max, value = _get_min_max_value(o[0], o[1])
            if all(isinstance(_, Integral) for _ in o):
                cls = IntSlider
            else:
                cls = FloatSlider
            return cls(value=value, min=min, max=max)
        elif _matches(o, (Real, Real, Real)):
            step = o[2]
            if step <= 0:
                raise ValueError("step must be >= 0, not %r" % step)
            min, max, value = _get_min_max_value(o[0], o[1], step=step)
            if all(isinstance(_, Integral) for _ in o):
                cls = IntSlider
            else:
                cls = FloatSlider
            return cls(value=value, min=min, max=max, step=step)

    @staticmethod
    def widget_from_iterable(o):
        """Make widgets from an iterable. This should not be done for
        a string or tuple."""
        # Dropdown expects a dict or list, so we convert an arbitrary
        # iterable to either of those.
        if isinstance(o, (list, dict)):
            return Dropdown(options=o)
        elif isinstance(o, Mapping):
            return Dropdown(options=list(o.items()))
        else:
            return Dropdown(options=list(o))

    # Return a factory for interactive functions
    @classmethod
    def factory(cls):
        options = dict(manual=False, auto_display=True, manual_name="Run Interact")
        return _InteractFactory(cls, options)


class _InteractFactory:
    """
    Factory for instances of :class:`interactive`.

    This class is needed to support options like::

        >>> @interact.options(manual=True)
        ... def greeting(text="World"):
        ...     print("Hello {}".format(text))

    Parameters
    ----------
    cls : class
        The subclass of :class:`interactive` to construct.
    options : dict
        A dict of options used to construct the interactive
        function. By default, this is returned by
        ``cls.default_options()``.
    kwargs : dict
        A dict of **kwargs to use for widgets.
    """
    def __init__(self, cls, options, kwargs={}):
        self.cls = cls
        self.opts = options
        self.kwargs = kwargs

    def widget(self, f):
        """
        Return an interactive function widget for the given function.

        The widget is only constructed, not displayed nor attached to
```
