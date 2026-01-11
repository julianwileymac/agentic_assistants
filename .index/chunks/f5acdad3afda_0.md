# Chunk: f5acdad3afda_0

- source: `.venv-lab/Lib/site-packages/ipywidgets/widgets/widget_output.py`
- lines: 1-92
- chunk: 1/3

```
# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

"""Output class.

Represents a widget that can be used to display output within the widget area.
"""

import sys
from functools import wraps

from .domwidget import DOMWidget
from .trait_types import TypedTuple
from .widget import register
from .._version import __jupyter_widgets_output_version__

from traitlets import Unicode, Dict
from IPython.core.interactiveshell import InteractiveShell
from IPython.display import clear_output
from IPython import get_ipython
import traceback

@register
class Output(DOMWidget):
    """Widget used as a context manager to display output.

    This widget can capture and display stdout, stderr, and rich output.  To use
    it, create an instance of it and display it.

    You can then use the widget as a context manager: any output produced while in the
    context will be captured and displayed in the widget instead of the standard output
    area.

    You can also use the .capture() method to decorate a function or a method. Any output
    produced by the function will then go to the output widget. This is useful for
    debugging widget callbacks, for example.

    Example::
        import ipywidgets as widgets
        from IPython.display import display
        out = widgets.Output()
        display(out)

        print('prints to output area')

        with out:
            print('prints to output widget')

        @out.capture()
        def func():
            print('prints to output widget')
    """
    _view_name = Unicode('OutputView').tag(sync=True)
    _model_name = Unicode('OutputModel').tag(sync=True)
    _view_module = Unicode('@jupyter-widgets/output').tag(sync=True)
    _model_module = Unicode('@jupyter-widgets/output').tag(sync=True)
    _view_module_version = Unicode(__jupyter_widgets_output_version__).tag(sync=True)
    _model_module_version = Unicode(__jupyter_widgets_output_version__).tag(sync=True)

    msg_id = Unicode('', help="Parent message id of messages to capture").tag(sync=True)
    outputs = TypedTuple(trait=Dict(), help="The output messages synced from the frontend.").tag(sync=True)

    __counter = 0

    def clear_output(self, *pargs, **kwargs):
        """
        Clear the content of the output widget.

        Parameters
        ----------

        wait: bool
            If True, wait to clear the output until new output is
            available to replace it. Default: False
        """
        with self:
            clear_output(*pargs, **kwargs)

    # PY3: Force passing clear_output and clear_kwargs as kwargs
    def capture(self, clear_output=False, *clear_args, **clear_kwargs):
        """
        Decorator to capture the stdout and stderr of a function.

        Parameters
        ----------

        clear_output: bool
            If True, clear the content of the output widget at every
            new function call. Default: False

        wait: bool
```
