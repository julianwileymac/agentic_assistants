# Chunk: bcc3c6bec4b8_10

- source: `.venv-lab/Lib/site-packages/pip/_vendor/distlib/util.py`
- lines: 772-877
- chunk: 11/25

```
th.expanduser('~')
    # we use 'isdir' instead of 'exists', because we want to
    # fail if there's a file with that name
    if os.path.isdir(result):
        usable = os.access(result, os.W_OK)
        if not usable:
            logger.warning('Directory exists but is not writable: %s', result)
    else:
        try:
            os.makedirs(result)
            usable = True
        except OSError:
            logger.warning('Unable to create %s', result, exc_info=True)
            usable = False
    if not usable:
        result = tempfile.mkdtemp()
        logger.warning('Default location unusable, using %s', result)
    return os.path.join(result, suffix)


def path_to_cache_dir(path, use_abspath=True):
    """
    Convert an absolute path to a directory name for use in a cache.

    The algorithm used is:

    #. On Windows, any ``':'`` in the drive is replaced with ``'---'``.
    #. Any occurrence of ``os.sep`` is replaced with ``'--'``.
    #. ``'.cache'`` is appended.
    """
    d, p = os.path.splitdrive(os.path.abspath(path) if use_abspath else path)
    if d:
        d = d.replace(':', '---')
    p = p.replace(os.sep, '--')
    return d + p + '.cache'


def ensure_slash(s):
    if not s.endswith('/'):
        return s + '/'
    return s


def parse_credentials(netloc):
    username = password = None
    if '@' in netloc:
        prefix, netloc = netloc.rsplit('@', 1)
        if ':' not in prefix:
            username = prefix
        else:
            username, password = prefix.split(':', 1)
    if username:
        username = unquote(username)
    if password:
        password = unquote(password)
    return username, password, netloc


def get_process_umask():
    result = os.umask(0o22)
    os.umask(result)
    return result


def is_string_sequence(seq):
    result = True
    i = None
    for i, s in enumerate(seq):
        if not isinstance(s, string_types):
            result = False
            break
    assert i is not None
    return result


PROJECT_NAME_AND_VERSION = re.compile('([a-z0-9_]+([.-][a-z_][a-z0-9_]*)*)-'
                                      '([a-z0-9_.+-]+)', re.I)
PYTHON_VERSION = re.compile(r'-py(\d\.?\d?)')


def split_filename(filename, project_name=None):
    """
    Extract name, version, python version from a filename (no extension)

    Return name, version, pyver or None
    """
    result = None
    pyver = None
    filename = unquote(filename).replace(' ', '-')
    m = PYTHON_VERSION.search(filename)
    if m:
        pyver = m.group(1)
        filename = filename[:m.start()]
    if project_name and len(filename) > len(project_name) + 1:
        m = re.match(re.escape(project_name) + r'\b', filename)
        if m:
            n = m.end()
            result = filename[:n], filename[n + 1:], pyver
    if result is None:
        m = PROJECT_NAME_AND_VERSION.match(filename)
        if m:
            result = m.group(1), m.group(3), pyver
    return result
```
