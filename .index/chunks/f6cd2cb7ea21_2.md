# Chunk: f6cd2cb7ea21_2

- source: `.venv-lab/Lib/site-packages/jedi/api/project.py`
- lines: 144-229
- chunk: 3/7

```
ap potential pathlib.Path entries
            sys_path = list(map(str, sys_path))
        self._sys_path = sys_path
        self._smart_sys_path = smart_sys_path
        self._load_unsafe_extensions = load_unsafe_extensions
        self._django = False
        # Remap potential pathlib.Path entries
        self.added_sys_path = list(map(str, added_sys_path))
        """The sys path that is going to be added at the end of the """

    @property
    def path(self):
        """
        The base path for this project.
        """
        return self._path

    @property
    def sys_path(self):
        """
        The sys path provided to this project. This can be None and in that
        case will be auto generated.
        """
        return self._sys_path

    @property
    def smart_sys_path(self):
        """
        If the sys path is going to be calculated in a smart way, where
        additional paths are added.
        """
        return self._smart_sys_path

    @property
    def load_unsafe_extensions(self):
        """
        Wheter the project loads unsafe extensions.
        """
        return self._load_unsafe_extensions

    @inference_state_as_method_param_cache()
    def _get_base_sys_path(self, inference_state):
        # The sys path has not been set explicitly.
        sys_path = list(inference_state.environment.get_sys_path())
        try:
            sys_path.remove('')
        except ValueError:
            pass
        return sys_path

    @inference_state_as_method_param_cache()
    def _get_sys_path(self, inference_state, add_parent_paths=True, add_init_paths=False):
        """
        Keep this method private for all users of jedi. However internally this
        one is used like a public method.
        """
        suffixed = list(self.added_sys_path)
        prefixed = []

        if self._sys_path is None:
            sys_path = list(self._get_base_sys_path(inference_state))
        else:
            sys_path = list(self._sys_path)

        if self._smart_sys_path:
            prefixed.append(str(self._path))

            if inference_state.script_path is not None:
                suffixed += map(str, discover_buildout_paths(
                    inference_state,
                    inference_state.script_path
                ))

                if add_parent_paths:
                    # Collect directories in upward search by:
                    #   1. Skipping directories with __init__.py
                    #   2. Stopping immediately when above self._path
                    traversed = []
                    for parent_path in inference_state.script_path.parents:
                        if parent_path == self._path \
                                or self._path not in parent_path.parents:
                            break
                        if not add_init_paths \
                                and parent_path.joinpath("__init__.py").is_file():
                            continue
```
