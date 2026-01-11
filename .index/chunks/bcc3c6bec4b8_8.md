# Chunk: bcc3c6bec4b8_8

- source: `.venv-lab/Lib/site-packages/pip/_vendor/distlib/util.py`
- lines: 613-707
- chunk: 9/25

```
rectory tree at %s', path)
                if not self.dry_run:
                    shutil.rmtree(path)
                if self.record:
                    if path in self.dirs_created:
                        self.dirs_created.remove(path)
            else:
                if os.path.islink(path):
                    s = 'link'
                else:
                    s = 'file'
                logger.debug('Removing %s %s', s, path)
                if not self.dry_run:
                    os.remove(path)
                if self.record:
                    if path in self.files_written:
                        self.files_written.remove(path)

    def is_writable(self, path):
        result = False
        while not result:
            if os.path.exists(path):
                result = os.access(path, os.W_OK)
                break
            parent = os.path.dirname(path)
            if parent == path:
                break
            path = parent
        return result

    def commit(self):
        """
        Commit recorded changes, turn off recording, return
        changes.
        """
        assert self.record
        result = self.files_written, self.dirs_created
        self._init_record()
        return result

    def rollback(self):
        if not self.dry_run:
            for f in list(self.files_written):
                if os.path.exists(f):
                    os.remove(f)
            # dirs should all be empty now, except perhaps for
            # __pycache__ subdirs
            # reverse so that subdirs appear before their parents
            dirs = sorted(self.dirs_created, reverse=True)
            for d in dirs:
                flist = os.listdir(d)
                if flist:
                    assert flist == ['__pycache__']
                    sd = os.path.join(d, flist[0])
                    os.rmdir(sd)
                os.rmdir(d)  # should fail if non-empty
        self._init_record()


def resolve(module_name, dotted_path):
    if module_name in sys.modules:
        mod = sys.modules[module_name]
    else:
        mod = __import__(module_name)
    if dotted_path is None:
        result = mod
    else:
        parts = dotted_path.split('.')
        result = getattr(mod, parts.pop(0))
        for p in parts:
            result = getattr(result, p)
    return result


class ExportEntry(object):

    def __init__(self, name, prefix, suffix, flags):
        self.name = name
        self.prefix = prefix
        self.suffix = suffix
        self.flags = flags

    @cached_property
    def value(self):
        return resolve(self.prefix, self.suffix)

    def __repr__(self):  # pragma: no cover
        return '<ExportEntry %s = %s:%s %s>' % (self.name, self.prefix, self.suffix, self.flags)

    def __eq__(self, other):
        if not isinstance(other, ExportEntry):
            result = False
        else:
            result = (self.name == other.name and self.prefix == other.prefix and self.suffix == other.suffix and
```
