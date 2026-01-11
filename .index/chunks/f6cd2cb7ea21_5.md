# Chunk: f6cd2cb7ea21_5

- source: `.venv-lab/Lib/site-packages/jedi/api/project.py`
- lines: 345-440
- chunk: 6/7

```
mes,
                wanted_type=wanted_type,
                wanted_names=wanted_names,
                complete=complete,
                ignore_imports=True,
            )

        # 3. Search for modules on sys.path
        sys_path = [
            p for p in self._get_sys_path(inference_state)
            # Exclude the current folder which is handled by recursing the folders.
            if p != self._path
        ]
        names = list(iter_module_names(inference_state, empty_module_context, sys_path))
        yield from search_in_module(
            inference_state,
            empty_module_context,
            names=names,
            wanted_type=wanted_type,
            wanted_names=wanted_names,
            complete=complete,
            convert=True,
        )

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self._path)


def _is_potential_project(path):
    for name in _CONTAINS_POTENTIAL_PROJECT:
        try:
            if path.joinpath(name).exists():
                return True
        except OSError:
            continue
    return False


def _is_django_path(directory):
    """ Detects the path of the very well known Django library (if used) """
    try:
        with open(directory.joinpath('manage.py'), 'rb') as f:
            return b"DJANGO_SETTINGS_MODULE" in f.read()
    except (FileNotFoundError, IsADirectoryError, PermissionError):
        return False


def get_default_project(path=None):
    """
    If a project is not defined by the user, Jedi tries to define a project by
    itself as well as possible. Jedi traverses folders until it finds one of
    the following:

    1. A ``.jedi/config.json``
    2. One of the following files: ``setup.py``, ``.git``, ``.hg``,
       ``requirements.txt`` and ``MANIFEST.in``.
    """
    if path is None:
        path = Path.cwd()
    elif isinstance(path, str):
        path = Path(path)

    check = path.absolute()
    probable_path = None
    first_no_init_file = None
    for dir in chain([check], check.parents):
        try:
            return Project.load(dir)
        except (FileNotFoundError, IsADirectoryError, PermissionError):
            pass
        except NotADirectoryError:
            continue

        if first_no_init_file is None:
            if dir.joinpath('__init__.py').exists():
                # In the case that a __init__.py exists, it's in 99% just a
                # Python package and the project sits at least one level above.
                continue
            elif not dir.is_file():
                first_no_init_file = dir

        if _is_django_path(dir):
            project = Project(dir)
            project._django = True
            return project

        if probable_path is None and _is_potential_project(dir):
            probable_path = dir

    if probable_path is not None:
        return Project(probable_path)

    if first_no_init_file is not None:
        return Project(first_no_init_file)
```
