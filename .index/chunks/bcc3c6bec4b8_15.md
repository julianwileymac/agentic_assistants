# Chunk: bcc3c6bec4b8_15

- source: `.venv-lab/Lib/site-packages/pip/_vendor/distlib/util.py`
- lines: 1196-1277
- chunk: 16/25

```
             result.append(component)

        for node in graph:
            if node not in lowlinks:
                strongconnect(node)

        return result

    @property
    def dot(self):
        result = ['digraph G {']
        for succ in self._preds:
            preds = self._preds[succ]
            for pred in preds:
                result.append('  %s -> %s;' % (pred, succ))
        for node in self._nodes:
            result.append('  %s;' % node)
        result.append('}')
        return '\n'.join(result)


#
# Unarchiving functionality for zip, tar, tgz, tbz, whl
#

ARCHIVE_EXTENSIONS = ('.tar.gz', '.tar.bz2', '.tar', '.zip', '.tgz', '.tbz', '.whl')


def unarchive(archive_filename, dest_dir, format=None, check=True):

    def check_path(path):
        if not isinstance(path, text_type):
            path = path.decode('utf-8')
        p = os.path.abspath(os.path.join(dest_dir, path))
        if not p.startswith(dest_dir) or p[plen] != os.sep:
            raise ValueError('path outside destination: %r' % p)

    dest_dir = os.path.abspath(dest_dir)
    plen = len(dest_dir)
    archive = None
    if format is None:
        if archive_filename.endswith(('.zip', '.whl')):
            format = 'zip'
        elif archive_filename.endswith(('.tar.gz', '.tgz')):
            format = 'tgz'
            mode = 'r:gz'
        elif archive_filename.endswith(('.tar.bz2', '.tbz')):
            format = 'tbz'
            mode = 'r:bz2'
        elif archive_filename.endswith('.tar'):
            format = 'tar'
            mode = 'r'
        else:  # pragma: no cover
            raise ValueError('Unknown format for %r' % archive_filename)
    try:
        if format == 'zip':
            archive = ZipFile(archive_filename, 'r')
            if check:
                names = archive.namelist()
                for name in names:
                    check_path(name)
        else:
            archive = tarfile.open(archive_filename, mode)
            if check:
                names = archive.getnames()
                for name in names:
                    check_path(name)
        if format != 'zip' and sys.version_info[0] < 3:
            # See Python issue 17153. If the dest path contains Unicode,
            # tarfile extraction fails on Python 2.x if a member path name
            # contains non-ASCII characters - it leads to an implicit
            # bytes -> unicode conversion using ASCII to decode.
            for tarinfo in archive.getmembers():
                if not isinstance(tarinfo.name, text_type):
                    tarinfo.name = tarinfo.name.decode('utf-8')

        # Limit extraction of dangerous items, if this Python
        # allows it easily. If not, just trust the input.
        # See: https://docs.python.org/3/library/tarfile.html#extraction-filters
        def extraction_filter(member, path):
            """Run tarfile.tar_filter, but raise the expected ValueError"""
```
