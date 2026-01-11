# Chunk: f0bcaff45f4a_1

- source: `.venv-lab/Lib/site-packages/jedi/api/refactoring/__init__.py`
- lines: 79-166
- chunk: 2/4

```
  return '<%s: %s>' % (self.__class__.__name__, self._from_path)


class Refactoring:
    def __init__(self, inference_state, file_to_node_changes, renames=()):
        self._inference_state = inference_state
        self._renames = renames
        self._file_to_node_changes = file_to_node_changes

    def get_changed_files(self) -> Dict[Path, ChangedFile]:
        def calculate_to_path(p):
            if p is None:
                return p
            p = str(p)
            for from_, to in renames:
                if p.startswith(str(from_)):
                    p = str(to) + p[len(str(from_)):]
            return Path(p)

        renames = self.get_renames()
        return {
            path: ChangedFile(
                self._inference_state,
                from_path=path,
                to_path=calculate_to_path(path),
                module_node=next(iter(map_)).get_root_node(),
                node_to_str_map=map_
            )
            # We need to use `or`, because the path can be None
            for path, map_ in sorted(
                self._file_to_node_changes.items(),
                key=lambda x: x[0] or Path("")
            )
        }

    def get_renames(self) -> Iterable[Tuple[Path, Path]]:
        """
        Files can be renamed in a refactoring.
        """
        return sorted(self._renames)

    def get_diff(self):
        text = ''
        project_path = self._inference_state.project.path
        for from_, to in self.get_renames():
            text += 'rename from %s\nrename to %s\n' \
                % (_try_relative_to(from_, project_path), _try_relative_to(to, project_path))

        return text + ''.join(f.get_diff() for f in self.get_changed_files().values())

    def apply(self):
        """
        Applies the whole refactoring to the files, which includes renames.
        """
        for f in self.get_changed_files().values():
            f.apply()

        for old, new in self.get_renames():
            old.rename(new)


def _calculate_rename(path, new_name):
    dir_ = path.parent
    if path.name in ('__init__.py', '__init__.pyi'):
        return dir_, dir_.parent.joinpath(new_name)
    return path, dir_.joinpath(new_name + path.suffix)


def rename(inference_state, definitions, new_name):
    file_renames = set()
    file_tree_name_map = {}

    if not definitions:
        raise RefactoringError("There is no name under the cursor")

    for d in definitions:
        # This private access is ok in a way. It's not public to
        # protect Jedi users from seeing it.
        tree_name = d._name.tree_name
        if d.type == 'module' and tree_name is None and d.module_path is not None:
            p = Path(d.module_path)
            file_renames.add(_calculate_rename(p, new_name))
        elif isinstance(d._name, ImplicitNSName):
            for p in d._name._value.py__path__():
                file_renames.add(_calculate_rename(Path(p), new_name))
        else:
            if tree_name is not None:
```
