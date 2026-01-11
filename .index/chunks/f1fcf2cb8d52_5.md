# Chunk: f1fcf2cb8d52_5

- source: `.venv-lab/Lib/site-packages/jupyterlab/labapp.py`
- lines: 434-505
- chunk: 6/13

```
 no
      extensions are enabled. This is the default in a stable JupyterLab release if you
      have no extensions installed.
    * Dev mode (`--dev-mode`): uses the unpublished local JavaScript packages in the
      `dev_mode` folder.  In this case JupyterLab will show a red stripe at the top of
      the page.  It can only be used if JupyterLab is installed as `pip install -e .`.
    * App mode: JupyterLab allows multiple JupyterLab "applications" to be
      created by the user with different combinations of extensions. The `--app-dir` can
      be used to set a directory for different applications. The default application
      path can be found using `jupyter lab path`.
    """

    examples = """
        jupyter lab                       # start JupyterLab
        jupyter lab --dev-mode            # start JupyterLab in development mode, with no extensions
        jupyter lab --core-mode           # start JupyterLab in core mode, with no extensions
        jupyter lab --app-dir=~/myjupyterlabapp # start JupyterLab with a particular set of extensions
        jupyter lab --certfile=mycert.pem # use SSL/TLS certificate
    """

    aliases = aliases
    aliases.update(
        {
            "watch": "LabApp.watch",
        }
    )
    aliases["app-dir"] = "LabApp.app_dir"

    flags = flags
    flags["core-mode"] = (
        {"LabApp": {"core_mode": True}},
        "Start the app in core mode.",
    )
    flags["dev-mode"] = (
        {"LabApp": {"dev_mode": True}},
        "Start the app in dev mode for running from source.",
    )
    flags["skip-dev-build"] = (
        {"LabApp": {"skip_dev_build": True}},
        "Skip the initial install and JS build of the app in dev mode.",
    )
    flags["watch"] = ({"LabApp": {"watch": True}}, "Start the app in watch mode.")
    flags["splice-source"] = (
        {"LabApp": {"splice_source": True}},
        "Splice source packages into app directory.",
    )
    flags["expose-app-in-browser"] = (
        {"LabApp": {"expose_app_in_browser": True}},
        "Expose the global app instance to browser via window.jupyterapp.",
    )
    flags["extensions-in-dev-mode"] = (
        {"LabApp": {"extensions_in_dev_mode": True}},
        "Load prebuilt extensions in dev-mode.",
    )
    flags["collaborative"] = (
        {"LabApp": {"collaborative": True}},
        """To enable real-time collaboration, you must install the extension `jupyter_collaboration`.
        You can install it using pip for example:

            python -m pip install jupyter_collaboration

        This flag is now deprecated and will be removed in JupyterLab v5.""",
    )
    flags["custom-css"] = (
        {"LabApp": {"custom_css": True}},
        "Load custom CSS in template html files. Default is False",
    )

    subcommands = {
        "build": (LabBuildApp, LabBuildApp.description.splitlines()[0]),
        "clean": (LabCleanApp, LabCleanApp.description.splitlines()[0]),
```
