# Chunk: aa1ac86ee9e0_7

- source: `.venv-lab/Lib/site-packages/ipywidgets/widgets/interaction.py`
- lines: 508-585
- chunk: 8/8

```
ract as a decorator with named parameters
            @interact(num=5)
            def square(num=2):
                print("{} squared is {}".format(num, num*num))
        """
        # If kwargs are given, replace self by a new
        # _InteractFactory with the updated kwargs
        if kwargs:
            kw = dict(self.kwargs)
            kw.update(kwargs)
            self = type(self)(self.cls, self.opts, kw)

        f = __interact_f
        if f is None:
            # This branch handles the case 3
            # @interact(a=30, b=40)
            # def f(*args, **kwargs):
            #     ...
            #
            # Simply return the new factory
            return self

        # positional arg support in: https://gist.github.com/8851331
        # Handle the cases 1 and 2
        # 1. interact(f, **kwargs)
        # 2. @interact
        #    def f(*args, **kwargs):
        #        ...
        w = self.widget(f)
        try:
            f.widget = w
        except AttributeError:
            # some things (instancemethods) can't have attributes attached,
            # so wrap in a lambda
            f = lambda *args, **kwargs: __interact_f(*args, **kwargs)
            f.widget = w
        show_inline_matplotlib_plots()
        display(w)
        return f

    def options(self, **kwds):
        """
        Change options for interactive functions.

        Returns
        -------
        A new :class:`_InteractFactory` which will apply the
        options when called.
        """
        opts = dict(self.opts)
        for k in kwds:
            try:
                # Ensure that the key exists because we want to change
                # existing options, not add new ones.
                _ = opts[k]
            except KeyError:
                raise ValueError("invalid option {!r}".format(k))
            opts[k] = kwds[k]
        return type(self)(self.cls, opts, self.kwargs)


interact = interactive.factory()
interact_manual = interact.options(manual=True, manual_name="Run Interact")


class fixed(HasTraits):
    """A pseudo-widget whose value is fixed and never synced to the client."""
    value = Any(help="Any Python object")
    description = Unicode('', help="Any Python object")
    def __init__(self, value, **kwargs):
        super().__init__(value=value, **kwargs)
    def get_interact_value(self):
        """Return the value for this widget which should be passed to
        interactive functions. Custom widgets can change this method
        to process the raw value ``self.value``.
        """
        return self.value
```
