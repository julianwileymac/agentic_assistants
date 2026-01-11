# Chunk: bdb4c9d3faee_9

- source: `.venv-lab/Lib/site-packages/pip/_vendor/pkg_resources/__init__.py`
- lines: 771-847
- chunk: 10/47

```
ool = False,
    ):
        """Add `dist` to working set, associated with `entry`

        If `entry` is unspecified, it defaults to the ``.location`` of `dist`.
        On exit from this routine, `entry` is added to the end of the working
        set's ``.entries`` (if it wasn't already present).

        `dist` is only added to the working set if it's for a project that
        doesn't already have a distribution in the set, unless `replace=True`.
        If it's added, any callbacks registered with the ``subscribe()`` method
        will be called.
        """
        if insert:
            dist.insert_on(self.entries, entry, replace=replace)

        if entry is None:
            entry = dist.location
        keys = self.entry_keys.setdefault(entry, [])
        keys2 = self.entry_keys.setdefault(dist.location, [])
        if not replace and dist.key in self.by_key:
            # ignore hidden distros
            return

        self.by_key[dist.key] = dist
        normalized_name = _packaging_utils.canonicalize_name(dist.key)
        self.normalized_to_canonical_keys[normalized_name] = dist.key
        if dist.key not in keys:
            keys.append(dist.key)
        if dist.key not in keys2:
            keys2.append(dist.key)
        self._added_new(dist)

    @overload
    def resolve(
        self,
        requirements: Iterable[Requirement],
        env: Environment | None,
        installer: _InstallerTypeT[_DistributionT],
        replace_conflicting: bool = False,
        extras: tuple[str, ...] | None = None,
    ) -> list[_DistributionT]: ...
    @overload
    def resolve(
        self,
        requirements: Iterable[Requirement],
        env: Environment | None = None,
        *,
        installer: _InstallerTypeT[_DistributionT],
        replace_conflicting: bool = False,
        extras: tuple[str, ...] | None = None,
    ) -> list[_DistributionT]: ...
    @overload
    def resolve(
        self,
        requirements: Iterable[Requirement],
        env: Environment | None = None,
        installer: _InstallerType | None = None,
        replace_conflicting: bool = False,
        extras: tuple[str, ...] | None = None,
    ) -> list[Distribution]: ...
    def resolve(
        self,
        requirements: Iterable[Requirement],
        env: Environment | None = None,
        installer: _InstallerType | None | _InstallerTypeT[_DistributionT] = None,
        replace_conflicting: bool = False,
        extras: tuple[str, ...] | None = None,
    ) -> list[Distribution] | list[_DistributionT]:
        """List all distributions needed to (recursively) meet `requirements`

        `requirements` must be a sequence of ``Requirement`` objects.  `env`,
        if supplied, should be an ``Environment`` instance.  If
        not supplied, it defaults to all distributions available within any
        entry or distribution in the working set.  `installer`, if supplied,
        will be invoked with each requirement that cannot be met by an
```
