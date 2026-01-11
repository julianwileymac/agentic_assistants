# Chunk: f1fcf2cb8d52_6

- source: `.venv-lab/Lib/site-packages/jupyterlab/labapp.py`
- lines: 497-570
- chunk: 7/13

```
custom-css"] = (
        {"LabApp": {"custom_css": True}},
        "Load custom CSS in template html files. Default is False",
    )

    subcommands = {
        "build": (LabBuildApp, LabBuildApp.description.splitlines()[0]),
        "clean": (LabCleanApp, LabCleanApp.description.splitlines()[0]),
        "path": (LabPathApp, LabPathApp.description.splitlines()[0]),
        "paths": (LabPathApp, LabPathApp.description.splitlines()[0]),
        "workspace": (LabWorkspaceApp, LabWorkspaceApp.description.splitlines()[0]),
        "workspaces": (LabWorkspaceApp, LabWorkspaceApp.description.splitlines()[0]),
        "licenses": (LabLicensesApp, LabLicensesApp.description.splitlines()[0]),
    }

    default_url = Unicode("/lab", config=True, help="The default URL to redirect to from `/`")

    override_static_url = Unicode(
        config=True, help=("The override url for static lab assets, typically a CDN.")
    )

    override_theme_url = Unicode(
        config=True,
        help=("The override url for static lab theme assets, typically a CDN."),
    )

    app_dir = Unicode(None, config=True, help="The app directory to launch JupyterLab from.")

    user_settings_dir = Unicode(
        get_user_settings_dir(), config=True, help="The directory for user settings."
    )

    workspaces_dir = Unicode(get_workspaces_dir(), config=True, help="The directory for workspaces")

    core_mode = Bool(
        False,
        config=True,
        help="""Whether to start the app in core mode. In this mode, JupyterLab
        will run using the JavaScript assets that are within the installed
        JupyterLab Python package. In core mode, third party extensions are disabled.
        The `--dev-mode` flag is an alias to this to be used when the Python package
        itself is installed in development mode (`pip install -e .`).
        """,
    )

    dev_mode = Bool(
        False,
        config=True,
        help="""Whether to start the app in dev mode. Uses the unpublished local
        JavaScript packages in the `dev_mode` folder.  In this case JupyterLab will
        show a red stripe at the top of the page.  It can only be used if JupyterLab
        is installed as `pip install -e .`.
        """,
    )

    extensions_in_dev_mode = Bool(
        False,
        config=True,
        help="""Whether to load prebuilt extensions in dev mode. This may be
        useful to run and test prebuilt extensions in development installs of
        JupyterLab. APIs in a JupyterLab development install may be
        incompatible with published packages, so prebuilt extensions compiled
        against published packages may not work correctly.""",
    )

    extension_manager = Unicode(
        "pypi",
        config=True,
        help="""The extension manager factory to use. The default options are:
        "readonly" for a manager without installation capability or "pypi" for
        a manager using PyPi.org and pip to install extensions.""",
    )
```
