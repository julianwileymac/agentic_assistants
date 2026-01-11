# Chunk: aa1ac86ee9e0_0

- source: `.venv-lab/Lib/site-packages/ipywidgets/widgets/interaction.py`
- lines: 1-88
- chunk: 1/8

```
# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

"""Interact with functions using widgets."""

from collections.abc import Iterable, Mapping
from enum import EnumMeta as EnumType
from inspect import signature, Parameter
from inspect import getcallargs
from inspect import getfullargspec as check_argspec
import sys

from IPython import get_ipython
from . import (Widget, ValueWidget, Text,
    FloatSlider, FloatText, IntSlider, IntText, Checkbox,
    Dropdown, VBox, Button, DOMWidget, Output)
from IPython.display import display, clear_output
from traitlets import HasTraits, Any, Unicode, observe
from numbers import Real, Integral
from warnings import warn



empty = Parameter.empty


def show_inline_matplotlib_plots():
    """Show matplotlib plots immediately if using the inline backend.

    With ipywidgets 6.0, matplotlib plots don't work well with interact when
    using the inline backend that comes with ipykernel. Basically, the inline
    backend only shows the plot after the entire cell executes, which does not
    play well with drawing plots inside of an interact function. See
    https://github.com/jupyter-widgets/ipywidgets/issues/1181/ and
    https://github.com/ipython/ipython/issues/10376 for more details. This
    function displays any matplotlib plots if the backend is the inline backend.
    """
    if 'matplotlib' not in sys.modules:
        # matplotlib hasn't been imported, nothing to do.
        return

    try:
        import matplotlib as mpl
        from matplotlib_inline.backend_inline import flush_figures
    except ImportError:
        return

    if (mpl.get_backend() == 'module://ipykernel.pylab.backend_inline' or
        mpl.get_backend() == 'module://matplotlib_inline.backend_inline'):
        flush_figures()


def interactive_output(f, controls):
    """Connect widget controls to a function.

    This function does not generate a user interface for the widgets (unlike `interact`).
    This enables customisation of the widget user interface layout.
    The user interface layout must be defined and displayed manually.
    """

    out = Output()
    def observer(change):
        kwargs = {k:v.value for k,v in controls.items()}
        show_inline_matplotlib_plots()
        with out:
            clear_output(wait=True)
            f(**kwargs)
            show_inline_matplotlib_plots()
    for k,w in controls.items():
        w.observe(observer, 'value')
    show_inline_matplotlib_plots()
    observer(None)
    return out


def _matches(o, pattern):
    """Match a pattern of types in a sequence."""
    if not len(o) == len(pattern):
        return False
    comps = zip(o,pattern)
    return all(isinstance(obj,kind) for obj,kind in comps)


def _get_min_max_value(min, max, value=None, step=None):
    """Return min, max, value given input values with possible None."""
    # Either min and max need to be given, or value needs to be given
    if value is None:
```
