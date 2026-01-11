# Chunk: 17eb42dab0ca_1

- source: `.venv-lab/Lib/site-packages/notebook_shim/traits.py`
- lines: 76-146
- chunk: 2/2

```
  """return extra paths + the default locations"""
        return self.extra_template_paths

    extra_nbextensions_path = List(Unicode(), config=True,
                                   help=_i18n(
                                       """extra paths to look for Javascript notebook extensions""")
                                   )

    @property
    def nbextensions_path(self):
        """The path to look for Javascript notebook extensions"""
        path = self.extra_nbextensions_path + jupyter_path('nbextensions')
        # FIXME: remove IPython nbextensions path after a migration period
        try:
            from IPython.paths import get_ipython_dir
        except ImportError:
            pass
        else:
            path.append(os.path.join(get_ipython_dir(), 'nbextensions'))
        return path

    mathjax_url = Unicode("", config=True,
                          help="""A custom url for MathJax.js.
        Should be in the form of a case-sensitive url to MathJax,
        for example:  /static/components/MathJax/MathJax.js
        """
                          )

    @property
    def static_url_prefix(self):
        """Get the static url prefix for serving static files."""
        return super(NotebookAppTraits, self).static_url_prefix

    @default('mathjax_url')
    def _default_mathjax_url(self):
        if not self.enable_mathjax:
            return u''
        static_url_prefix = self.static_url_prefix
        return url_path_join(static_url_prefix, 'components', 'MathJax', 'MathJax.js')

    @observe('mathjax_url')
    def _update_mathjax_url(self, change):
        new = change['new']
        if new and not self.enable_mathjax:
            # enable_mathjax=False overrides mathjax_url
            self.mathjax_url = u''
        else:
            self.log.info(_i18n("Using MathJax: %s"), new)

    mathjax_config = Unicode("TeX-AMS-MML_HTMLorMML-full,Safe", config=True,
                             help=_i18n(
                                 """The MathJax.js configuration file that is to be used.""")
                             )

    @observe('mathjax_config')
    def _update_mathjax_config(self, change):
        self.log.info(
            _i18n("Using MathJax configuration file: %s"), change['new'])

    quit_button = Bool(True, config=True,
                       help="""If True, display a button in the dashboard to quit
        (shutdown the notebook server)."""
                       )

    nbserver_extensions = Dict({}, config=True,
                               help=(_i18n("Dict of Python modules to load as notebook server extensions."
                                           "Entry values can be used to enable and disable the loading of"
                                           "the extensions. The extensions will be loaded in alphabetical "
                                           "order."))
                               )
```
