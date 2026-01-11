# Chunk: aa1ac86ee9e0_6

- source: `.venv-lab/Lib/site-packages/ipywidgets/widgets/interaction.py`
- lines: 431-516
- chunk: 7/8

```
__init__(self, cls, options, kwargs={}):
        self.cls = cls
        self.opts = options
        self.kwargs = kwargs

    def widget(self, f):
        """
        Return an interactive function widget for the given function.

        The widget is only constructed, not displayed nor attached to
        the function.

        Returns
        -------
        An instance of ``self.cls`` (typically :class:`interactive`).

        Parameters
        ----------
        f : function
            The function to which the interactive widgets are tied.
        """
        return self.cls(f, self.opts, **self.kwargs)

    def __call__(self, __interact_f=None, **kwargs):
        """
        Make the given function interactive by adding and displaying
        the corresponding :class:`interactive` widget.

        Expects the first argument to be a function. Parameters to this
        function are widget abbreviations passed in as keyword arguments
        (``**kwargs``). Can be used as a decorator (see examples).

        Returns
        -------
        f : __interact_f with interactive widget attached to it.

        Parameters
        ----------
        __interact_f : function
            The function to which the interactive widgets are tied. The `**kwargs`
            should match the function signature. Passed to :func:`interactive()`
        **kwargs : various, optional
            An interactive widget is created for each keyword argument that is a
            valid widget abbreviation. Passed to :func:`interactive()`

        Examples
        --------
        Render an interactive text field that shows the greeting with the passed in
        text::

            # 1. Using interact as a function
            def greeting(text="World"):
                print("Hello {}".format(text))
            interact(greeting, text="Jupyter Widgets")

            # 2. Using interact as a decorator
            @interact
            def greeting(text="World"):
                print("Hello {}".format(text))

            # 3. Using interact as a decorator with named parameters
            @interact(text="Jupyter Widgets")
            def greeting(text="World"):
                print("Hello {}".format(text))

        Render an interactive slider widget and prints square of number::

            # 1. Using interact as a function
            def square(num=1):
                print("{} squared is {}".format(num, num*num))
            interact(square, num=5)

            # 2. Using interact as a decorator
            @interact
            def square(num=2):
                print("{} squared is {}".format(num, num*num))

            # 3. Using interact as a decorator with named parameters
            @interact(num=5)
            def square(num=2):
                print("{} squared is {}".format(num, num*num))
        """
        # If kwargs are given, replace self by a new
        # _InteractFactory with the updated kwargs
        if kwargs:
```
