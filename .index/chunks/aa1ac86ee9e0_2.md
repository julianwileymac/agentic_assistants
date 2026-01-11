# Chunk: aa1ac86ee9e0_2

- source: `.venv-lab/Lib/site-packages/ipywidgets/widgets/interaction.py`
- lines: 152-222
- chunk: 3/8

```

        ``"manual"`` (defaults to ``False``), ``"manual_name"`` (defaults
        to ``"Run Interact"``) and ``"auto_display"`` (defaults to ``False``).
    **kwargs : various, optional
        An interactive widget is created for each keyword argument that is a
        valid widget abbreviation.

    Note that the first two parameters intentionally start with a double
    underscore to avoid being mixed up with keyword arguments passed by
    ``**kwargs``.
    """
    def __init__(self, __interact_f, __options={}, **kwargs):
        VBox.__init__(self, _dom_classes=['widget-interact'])
        self.result = None
        self.args = []
        self.kwargs = {}

        self.f = f = __interact_f
        self.clear_output = kwargs.pop('clear_output', True)
        self.manual = __options.get("manual", False)
        self.manual_name = __options.get("manual_name", "Run Interact")
        self.auto_display = __options.get("auto_display", False)

        new_kwargs = self.find_abbreviations(kwargs)
        # Before we proceed, let's make sure that the user has passed a set of args+kwargs
        # that will lead to a valid call of the function. This protects against unspecified
        # and doubly-specified arguments.
        try:
            check_argspec(f)
        except TypeError:
            # if we can't inspect, we can't validate
            pass
        else:
            getcallargs(f, **{n:v for n,v,_ in new_kwargs})
        # Now build the widgets from the abbreviations.
        self.kwargs_widgets = self.widgets_from_abbreviations(new_kwargs)

        # This has to be done as an assignment, not using self.children.append,
        # so that traitlets notices the update. We skip any objects (such as fixed) that
        # are not DOMWidgets.
        c = [w for w in self.kwargs_widgets if isinstance(w, DOMWidget)]

        # If we are only to run the function on demand, add a button to request this.
        if self.manual:
            self.manual_button = Button(description=self.manual_name)
            c.append(self.manual_button)

        self.out = Output()
        c.append(self.out)
        self.children = c

        # Wire up the widgets
        # If we are doing manual running, the callback is only triggered by the button
        # Otherwise, it is triggered for every trait change received
        # On-demand running also suppresses running the function with the initial parameters
        if self.manual:
            self.manual_button.on_click(self.update)

            # Also register input handlers on text areas, so the user can hit return to
            # invoke execution.
            for w in self.kwargs_widgets:
                if isinstance(w, Text):
                    w.continuous_update = False
                    w.observe(self.update, names='value')
        else:
            for widget in self.kwargs_widgets:
                widget.observe(self.update, names='value')
            self.update()

    # Callback function
```
