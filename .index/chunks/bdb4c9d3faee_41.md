# Chunk: bdb4c9d3faee_41

- source: `.venv-lab/Lib/site-packages/pip/_vendor/pkg_resources/__init__.py`
- lines: 3250-3335
- chunk: 42/47

```
.insert(p, loc)
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

        # p is the spot where we found or inserted loc; now remove duplicates
        while True:
            try:
                np = npath.index(nloc, p + 1)
            except ValueError:
                break
            else:
                del npath[np], path[np]
                # ha!
                p = np

        return

    def check_version_conflict(self):
        if self.key == 'setuptools':
            # ignore the inevitable setuptools self-conflicts  :(
            return

        nsp = dict.fromkeys(self._get_metadata('namespace_packages.txt'))
        loc = normalize_path(self.location)
        for modname in self._get_metadata('top_level.txt'):
            if (
                modname not in sys.modules
                or modname in nsp
                or modname in _namespace_packages
            ):
                continue
            if modname in ('pkg_resources', 'setuptools', 'site'):
                continue
            fn = getattr(sys.modules[modname], '__file__', None)
            if fn and (
                normalize_path(fn).startswith(loc) or fn.startswith(self.location)
            ):
                continue
            issue_warning(
                "Module %s was already imported from %s, but %s is being added"
                " to sys.path" % (modname, fn, self.location),
            )

    def has_version(self):
        try:
            self.version
        except ValueError:
            issue_warning("Unbuilt egg for " + repr(self))
            return False
        except SystemError:
            # TODO: remove this except clause when python/cpython#103632 is fixed.
            return False
        return True

    def clone(self, **kw: str | int | IResourceProvider | None):
        """Copy this distribution, substituting in any changed keyword args"""
        names = 'project_name version py_version platform location precedence'
        for attr in names.split():
            kw.setdefault(attr, getattr(self, attr, None))
        kw.setdefault('metadata', self._provider)
        # Unsafely unpacking. But keeping **kw for backwards and subclassing compatibility
        return self.__class__(**kw)  # type:ignore[arg-type]

    @property
    def extras(self):
        return [dep for dep in self._dep_map if dep]


class EggInfoDistribution(Distribution):
    def _reload_version(self):
        """
        Packages installed by distutils (e.g. numpy or scipy),
        which uses an old safe_version, and so
        their version numbers can get mangled when
        converted to filenames (e.g., 1.11.0.dev0+2329eae to
        1.11.0.dev0_2329eae). These distributions will not be
        parsed properly
```
