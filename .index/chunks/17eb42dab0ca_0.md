# Chunk: 17eb42dab0ca_0

- source: `.venv-lab/Lib/site-packages/notebook_shim/traits.py`
- lines: 1-82
- chunk: 1/2

```
import os
from traitlets import (
    HasTraits, Dict, Unicode, List, Bool,
    observe, default
)
from jupyter_core.paths import jupyter_path
from jupyter_server.transutils import _i18n
from jupyter_server.utils import url_path_join


class NotebookAppTraits(HasTraits):

    ignore_minified_js = Bool(False,
                              config=True,
                              help=_i18n(
                                  'Deprecated: Use minified JS file or not, mainly use during dev to avoid JS recompilation'),
                              )

    jinja_environment_options = Dict(config=True,
                                     help=_i18n("Supply extra arguments that will be passed to Jinja environment."))

    jinja_template_vars = Dict(
        config=True,
        help=_i18n(
            "Extra variables to supply to jinja templates when rendering."),
    )

    enable_mathjax = Bool(True, config=True,
                          help="""Whether to enable MathJax for typesetting math/TeX

        MathJax is the javascript library Jupyter uses to render math/LaTeX. It is
        very large, so you may want to disable it if you have a slow internet
        connection, or for offline use of the notebook.

        When disabled, equations etc. will appear as their untransformed TeX source.
        """
                          )

    @observe('enable_mathjax')
    def _update_enable_mathjax(self, change):
        """set mathjax url to empty if mathjax is disabled"""
        if not change['new']:
            self.mathjax_url = u''

    extra_static_paths = List(Unicode(), config=True,
                              help="""Extra paths to search for serving static files.

        This allows adding javascript/css to be available from the notebook server machine,
        or overriding individual files in the IPython"""
                              )

    @property
    def static_file_path(self):
        """return extra paths + the default location"""
        return self.extra_static_paths

    static_custom_path = List(Unicode(),
                              help=_i18n(
                                  """Path to search for custom.js, css""")
                              )

    @default('static_custom_path')
    def _default_static_custom_path(self):
        return [
            os.path.join(self.config_dir, 'custom')
        ]

    extra_template_paths = List(Unicode(), config=True,
                                help=_i18n("""Extra paths to search for serving jinja templates.

        Can be used to override templates from notebook.templates.""")
                                )

    @property
    def template_file_path(self):
        """return extra paths + the default locations"""
        return self.extra_template_paths

    extra_nbextensions_path = List(Unicode(), config=True,
                                   help=_i18n(
                                       """extra paths to look for Javascript notebook extensions""")
```
