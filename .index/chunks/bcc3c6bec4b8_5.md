# Chunk: bcc3c6bec4b8_5

- source: `.venv-lab/Lib/site-packages/pip/_vendor/distlib/util.py`
- lines: 380-488
- chunk: 6/25

```
 stream = StringIO(data)
        read_stream(cp, stream)

    result = {}
    for key in cp.sections():
        result[key] = entries = {}
        for name, value in cp.items(key):
            s = '%s = %s' % (name, value)
            entry = get_export_entry(s)
            assert entry is not None
            # entry.dist = self
            entries[name] = entry
    return result


def write_exports(exports, stream):
    if sys.version_info[0] >= 3:
        # needs to be a text stream
        stream = codecs.getwriter('utf-8')(stream)
    cp = configparser.ConfigParser()
    for k, v in exports.items():
        # TODO check k, v for valid values
        cp.add_section(k)
        for entry in v.values():
            if entry.suffix is None:
                s = entry.prefix
            else:
                s = '%s:%s' % (entry.prefix, entry.suffix)
            if entry.flags:
                s = '%s [%s]' % (s, ', '.join(entry.flags))
            cp.set(k, entry.name, s)
    cp.write(stream)


@contextlib.contextmanager
def tempdir():
    td = tempfile.mkdtemp()
    try:
        yield td
    finally:
        shutil.rmtree(td)


@contextlib.contextmanager
def chdir(d):
    cwd = os.getcwd()
    try:
        os.chdir(d)
        yield
    finally:
        os.chdir(cwd)


@contextlib.contextmanager
def socket_timeout(seconds=15):
    cto = socket.getdefaulttimeout()
    try:
        socket.setdefaulttimeout(seconds)
        yield
    finally:
        socket.setdefaulttimeout(cto)


class cached_property(object):

    def __init__(self, func):
        self.func = func
        # for attr in ('__name__', '__module__', '__doc__'):
        #     setattr(self, attr, getattr(func, attr, None))

    def __get__(self, obj, cls=None):
        if obj is None:
            return self
        value = self.func(obj)
        object.__setattr__(obj, self.func.__name__, value)
        # obj.__dict__[self.func.__name__] = value = self.func(obj)
        return value


def convert_path(pathname):
    """Return 'pathname' as a name that will work on the native filesystem.

    The path is split on '/' and put back together again using the current
    directory separator.  Needed because filenames in the setup script are
    always supplied in Unix style, and have to be converted to the local
    convention before we can actually use them in the filesystem.  Raises
    ValueError on non-Unix-ish systems if 'pathname' either starts or
    ends with a slash.
    """
    if os.sep == '/':
        return pathname
    if not pathname:
        return pathname
    if pathname[0] == '/':
        raise ValueError("path '%s' cannot be absolute" % pathname)
    if pathname[-1] == '/':
        raise ValueError("path '%s' cannot end with '/'" % pathname)

    paths = pathname.split('/')
    while os.curdir in paths:
        paths.remove(os.curdir)
    if not paths:
        return os.curdir
    return os.path.join(*paths)


class FileOperator(object):
```
