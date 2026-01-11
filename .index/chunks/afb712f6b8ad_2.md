# Chunk: afb712f6b8ad_2

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydev_ipython/matplotlibtools.py`
- lines: 157-195
- chunk: 3/3

```
 a 'called' attribute. wrapper.called is initialized to False.

    The wrapper.called attribute is set to False right before each call to the
    wrapped function, so if the call fails it remains False.  After the call
    completes, wrapper.called is set to True and the output is returned.

    Testing for truth in wrapper.called allows you to determine if a call to
    func() was attempted and succeeded."""

    # don't wrap twice
    if hasattr(func, "called"):
        return func

    def wrapper(*args, **kw):
        wrapper.called = False
        out = func(*args, **kw)
        wrapper.called = True
        return out

    wrapper.called = False
    wrapper.__doc__ = func.__doc__
    return wrapper


def activate_pylab():
    pylab = sys.modules["pylab"]
    pylab.show._needmain = False
    # We need to detect at runtime whether show() is called by the user.
    # For this, we wrap it into a decorator which adds a 'called' flag.
    pylab.draw_if_interactive = flag_calls(pylab.draw_if_interactive)


def activate_pyplot():
    pyplot = sys.modules["matplotlib.pyplot"]
    pyplot.show._needmain = False
    # We need to detect at runtime whether show() is called by the user.
    # For this, we wrap it into a decorator which adds a 'called' flag.
    pyplot.draw_if_interactive = flag_calls(pyplot.draw_if_interactive)
```
