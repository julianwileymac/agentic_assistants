# Chunk: bdb4c9d3faee_40

- source: `.venv-lab/Lib/site-packages/pip/_vendor/pkg_resources/__init__.py`
- lines: 3180-3262
- chunk: 41/47

```
 not found" % ((group, name),))
        return ep.load()

    @overload
    def get_entry_map(self, group: None = None) -> dict[str, dict[str, EntryPoint]]: ...
    @overload
    def get_entry_map(self, group: str) -> dict[str, EntryPoint]: ...
    def get_entry_map(self, group: str | None = None):
        """Return the entry point map for `group`, or the full entry map"""
        if not hasattr(self, "_ep_map"):
            self._ep_map = EntryPoint.parse_map(
                self._get_metadata('entry_points.txt'), self
            )
        if group is not None:
            return self._ep_map.get(group, {})
        return self._ep_map

    def get_entry_info(self, group: str, name: str):
        """Return the EntryPoint object for `group`+`name`, or ``None``"""
        return self.get_entry_map(group).get(name)

    # FIXME: 'Distribution.insert_on' is too complex (13)
    def insert_on(  # noqa: C901
        self,
        path: list[str],
        loc=None,
        replace: bool = False,
    ):
        """Ensure self.location is on path

        If replace=False (default):
            - If location is already in path anywhere, do nothing.
            - Else:
              - If it's an egg and its parent directory is on path,
                insert just ahead of the parent.
              - Else: add to the end of path.
        If replace=True:
            - If location is already on path anywhere (not eggs)
              or higher priority than its parent (eggs)
              do nothing.
            - Else:
              - If it's an egg and its parent directory is on path,
                insert just ahead of the parent,
                removing any lower-priority entries.
              - Else: add it to the front of path.
        """

        loc = loc or self.location
        if not loc:
            return

        nloc = _normalize_cached(loc)
        bdir = os.path.dirname(nloc)
        npath = [(p and _normalize_cached(p) or p) for p in path]

        for p, item in enumerate(npath):
            if item == nloc:
                if replace:
                    break
                else:
                    # don't modify path (even removing duplicates) if
                    # found and not replace
                    return
            elif item == bdir and self.precedence == EGG_DIST:
                # if it's an .egg, give it precedence over its directory
                # UNLESS it's already been added to sys.path and replace=False
                if (not replace) and nloc in npath[p:]:
                    return
                if path is sys.path:
                    self.check_version_conflict()
                path.insert(p, loc)
                npath.insert(p, nloc)
                break
        else:
            if path is sys.path:
                self.check_version_conflict()
            if replace:
                path.insert(0, loc)
            else:
                path.append(loc)
            return
```
