# Chunk: bcc3c6bec4b8_11

- source: `.venv-lab/Lib/site-packages/pip/_vendor/distlib/util.py`
- lines: 866-966
- chunk: 12/25

```
e.escape(project_name) + r'\b', filename)
        if m:
            n = m.end()
            result = filename[:n], filename[n + 1:], pyver
    if result is None:
        m = PROJECT_NAME_AND_VERSION.match(filename)
        if m:
            result = m.group(1), m.group(3), pyver
    return result


# Allow spaces in name because of legacy dists like "Twisted Core"
NAME_VERSION_RE = re.compile(r'(?P<name>[\w .-]+)\s*'
                             r'\(\s*(?P<ver>[^\s)]+)\)$')


def parse_name_and_version(p):
    """
    A utility method used to get name and version from a string.

    From e.g. a Provides-Dist value.

    :param p: A value in a form 'foo (1.0)'
    :return: The name and version as a tuple.
    """
    m = NAME_VERSION_RE.match(p)
    if not m:
        raise DistlibException('Ill-formed name/version string: \'%s\'' % p)
    d = m.groupdict()
    return d['name'].strip().lower(), d['ver']


def get_extras(requested, available):
    result = set()
    requested = set(requested or [])
    available = set(available or [])
    if '*' in requested:
        requested.remove('*')
        result |= available
    for r in requested:
        if r == '-':
            result.add(r)
        elif r.startswith('-'):
            unwanted = r[1:]
            if unwanted not in available:
                logger.warning('undeclared extra: %s' % unwanted)
            if unwanted in result:
                result.remove(unwanted)
        else:
            if r not in available:
                logger.warning('undeclared extra: %s' % r)
            result.add(r)
    return result


#
# Extended metadata functionality
#


def _get_external_data(url):
    result = {}
    try:
        # urlopen might fail if it runs into redirections,
        # because of Python issue #13696. Fixed in locators
        # using a custom redirect handler.
        resp = urlopen(url)
        headers = resp.info()
        ct = headers.get('Content-Type')
        if not ct.startswith('application/json'):
            logger.debug('Unexpected response for JSON request: %s', ct)
        else:
            reader = codecs.getreader('utf-8')(resp)
            # data = reader.read().decode('utf-8')
            # result = json.loads(data)
            result = json.load(reader)
    except Exception as e:
        logger.exception('Failed to get external data for %s: %s', url, e)
    return result


_external_data_base_url = 'https://www.red-dove.com/pypi/projects/'


def get_project_data(name):
    url = '%s/%s/project.json' % (name[0].upper(), name)
    url = urljoin(_external_data_base_url, url)
    result = _get_external_data(url)
    return result


def get_package_data(name, version):
    url = '%s/%s/package-%s.json' % (name[0].upper(), name, version)
    url = urljoin(_external_data_base_url, url)
    return _get_external_data(url)


class Cache(object):
    """
    A class implementing a cache for resources that need to live in the file system
```
