# Chunk: f6cd2cb7ea21_6

- source: `.venv-lab/Lib/site-packages/jedi/api/project.py`
- lines: 428-449
- chunk: 7/7

```
ct._django = True
            return project

        if probable_path is None and _is_potential_project(dir):
            probable_path = dir

    if probable_path is not None:
        return Project(probable_path)

    if first_no_init_file is not None:
        return Project(first_no_init_file)

    curdir = path if path.is_dir() else path.parent
    return Project(curdir)


def _remove_imports(names):
    return [
        n for n in names
        if n.tree_name is None or n.api_type not in ('module', 'namespace')
    ]
```
