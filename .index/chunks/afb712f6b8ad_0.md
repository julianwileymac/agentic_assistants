# Chunk: afb712f6b8ad_0

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydev_ipython/matplotlibtools.py`
- lines: 1-93
- chunk: 1/3

```
import sys
from _pydev_bundle import pydev_log

backends = {
    "tk": "TkAgg",
    "gtk": "GTKAgg",
    "wx": "WXAgg",
    "qt": "QtAgg",  # Auto-choose qt4/5
    "qt4": "Qt4Agg",
    "qt5": "Qt5Agg",
    "qt6": "Qt6Agg",
    "osx": "MacOSX",
}

lowercase_convert = {
    "tkagg": "TkAgg",
    "gtkagg": "GTKAgg",
    "wxagg": "WXAgg",
    "qtagg": "QtAgg",
    "qt4agg": "Qt4Agg",
    "qt5agg": "Qt5Agg",
    "qt6agg": "Qt6Agg",
    "macosx": "MacOSX",
    "gtk": "GTK",
    "gtkcairo": "GTKCairo",
    "wx": "WX",
    "cocoaagg": "CocoaAgg",
}

# We also need a reverse backends2guis mapping that will properly choose which
# GUI support to activate based on the desired matplotlib backend.  For the
# most part it's just a reverse of the above dict, but we also need to add a
# few others that map to the same GUI manually:
backend2gui = dict(zip(backends.values(), backends.keys()))
# In the reverse mapping, there are a few extra valid matplotlib backends that
# map to the same GUI support
backend2gui["GTK"] = backend2gui["GTKCairo"] = "gtk"
backend2gui["WX"] = "wx"
backend2gui["CocoaAgg"] = "osx"


def do_enable_gui(guiname):
    from _pydev_bundle.pydev_versioncheck import versionok_for_gui

    if versionok_for_gui():
        try:
            from pydev_ipython.inputhook import enable_gui

            enable_gui(guiname)
        except:
            sys.stderr.write("Failed to enable GUI event loop integration for '%s'\n" % guiname)
            pydev_log.exception()
    elif guiname not in ["none", "", None]:
        # Only print a warning if the guiname was going to do something
        sys.stderr.write("Debug console: Python version does not support GUI event loop integration for '%s'\n" % guiname)
    # Return value does not matter, so return back what was sent
    return guiname


def find_gui_and_backend():
    """Return the gui and mpl backend."""
    matplotlib = sys.modules["matplotlib"]
    # WARNING: this assumes matplotlib 1.1 or newer!!
    backend = matplotlib.rcParams["backend"]

    # Translate to the real case as in 3.9 the case was forced to lowercase
    # but our internal mapping is in the original case.
    realcase_backend = lowercase_convert.get(backend, backend)

    # In this case, we need to find what the appropriate gui selection call
    # should be for IPython, so we can activate inputhook accordingly
    gui = backend2gui.get(realcase_backend, None)
    return gui, backend


def _get_major_version(module):
    return int(module.__version__.split('.')[0])


def _get_minor_version(module):
    return int(module.__version__.split('.')[1])


def is_interactive_backend(backend):
    """Check if backend is interactive"""
    matplotlib = sys.modules["matplotlib"]
    new_api_version = (3, 9)
    installed_version = (
        _get_major_version(matplotlib),
        _get_minor_version(matplotlib)
    )

```
