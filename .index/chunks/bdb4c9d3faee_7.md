# Chunk: bdb4c9d3faee_7

- source: `.venv-lab/Lib/site-packages/pip/_vendor/pkg_resources/__init__.py`
- lines: 619-707
- chunk: 8/47

```
ed resource a directory?  (like ``os.path.isdir()``)"""

    def resource_listdir(self, resource_name: str) -> list[str]:
        """List of resource names in the directory (like ``os.listdir()``)"""


class WorkingSet:
    """A collection of active distributions on sys.path (or a similar list)"""

    def __init__(self, entries: Iterable[str] | None = None):
        """Create working set from list of path entries (default=sys.path)"""
        self.entries: list[str] = []
        self.entry_keys = {}
        self.by_key = {}
        self.normalized_to_canonical_keys = {}
        self.callbacks = []

        if entries is None:
            entries = sys.path

        for entry in entries:
            self.add_entry(entry)

    @classmethod
    def _build_master(cls):
        """
        Prepare the master working set.
        """
        ws = cls()
        try:
            from __main__ import __requires__
        except ImportError:
            # The main program does not list any requirements
            return ws

        # ensure the requirements are met
        try:
            ws.require(__requires__)
        except VersionConflict:
            return cls._build_from_requirements(__requires__)

        return ws

    @classmethod
    def _build_from_requirements(cls, req_spec):
        """
        Build a working set from a requirement spec. Rewrites sys.path.
        """
        # try it without defaults already on sys.path
        # by starting with an empty path
        ws = cls([])
        reqs = parse_requirements(req_spec)
        dists = ws.resolve(reqs, Environment())
        for dist in dists:
            ws.add(dist)

        # add any missing entries from sys.path
        for entry in sys.path:
            if entry not in ws.entries:
                ws.add_entry(entry)

        # then copy back to sys.path
        sys.path[:] = ws.entries
        return ws

    def add_entry(self, entry: str):
        """Add a path item to ``.entries``, finding any distributions on it

        ``find_distributions(entry, True)`` is used to find distributions
        corresponding to the path entry, and they are added.  `entry` is
        always appended to ``.entries``, even if it is already present.
        (This is because ``sys.path`` can contain the same value more than
        once, and the ``.entries`` of the ``sys.path`` WorkingSet should always
        equal ``sys.path``.)
        """
        self.entry_keys.setdefault(entry, [])
        self.entries.append(entry)
        for dist in find_distributions(entry, True):
            self.add(dist, entry, False)

    def __contains__(self, dist: Distribution) -> bool:
        """True if `dist` is the active distribution for its project"""
        return self.by_key.get(dist.key) == dist

    def find(self, req: Requirement) -> Distribution | None:
        """Find a distribution matching requirement `req`

        If there is an active distribution for the requested project, this
```
