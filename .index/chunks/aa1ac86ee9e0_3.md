# Chunk: aa1ac86ee9e0_3

- source: `.venv-lab/Lib/site-packages/ipywidgets/widgets/interaction.py`
- lines: 213-288
- chunk: 4/8

```
f isinstance(w, Text):
                    w.continuous_update = False
                    w.observe(self.update, names='value')
        else:
            for widget in self.kwargs_widgets:
                widget.observe(self.update, names='value')
            self.update()

    # Callback function
    def update(self, *args):
        """
        Call the interact function and update the output widget with
        the result of the function call.

        Parameters
        ----------
        *args : ignored
            Required for this method to be used as traitlets callback.
        """
        self.kwargs = {}
        if self.manual:
            self.manual_button.disabled = True
        try:
            show_inline_matplotlib_plots()
            with self.out:
                if self.clear_output:
                    clear_output(wait=True)
                for widget in self.kwargs_widgets:
                    value = widget.get_interact_value()
                    self.kwargs[widget._kwarg] = value
                self.result = self.f(**self.kwargs)
                show_inline_matplotlib_plots()
                if self.auto_display and self.result is not None:
                    display(self.result)
        except Exception as e:
            ip = get_ipython()
            if ip is None:
                self.log.warning("Exception in interact callback: %s", e, exc_info=True)
            else:
                ip.showtraceback()
        finally:
            if self.manual:
                self.manual_button.disabled = False

    # Find abbreviations
    def signature(self):
        return signature(self.f)

    def find_abbreviations(self, kwargs):
        """Find the abbreviations for the given function and kwargs.
        Return (name, abbrev, default) tuples.
        """
        new_kwargs = []
        try:
            sig = self.signature()
        except (ValueError, TypeError):
            # can't inspect, no info from function; only use kwargs
            return [ (key, value, value) for key, value in kwargs.items() ]

        for param in sig.parameters.values():
            for name, value, default in _yield_abbreviations_for_parameter(param, kwargs):
                if value is empty:
                    raise ValueError('cannot find widget or abbreviation for argument: {!r}'.format(name))
                new_kwargs.append((name, value, default))
        return new_kwargs

    # Abbreviations to widgets
    def widgets_from_abbreviations(self, seq):
        """Given a sequence of (name, abbrev, default) tuples, return a sequence of Widgets."""
        result = []
        for name, abbrev, default in seq:
            if isinstance(abbrev, Widget) and (not isinstance(abbrev, ValueWidget)):
                raise TypeError("{!r} is not a ValueWidget".format(abbrev))
            widget = self.widget_from_abbrev(abbrev, default)
            if widget is None:
```
