# Chunk: bcc3c6bec4b8_17

- source: `.venv-lab/Lib/site-packages/pip/_vendor/distlib/util.py`
- lines: 1368-1462
- chunk: 18/25

```
ime.strftime('%H:%M:%S', time.gmtime(duration))
        return result

    @property
    def ETA(self):
        if self.done:
            prefix = 'Done'
            t = self.elapsed
            # import pdb; pdb.set_trace()
        else:
            prefix = 'ETA '
            if self.max is None:
                t = -1
            elif self.elapsed == 0 or (self.cur == self.min):
                t = 0
            else:
                # import pdb; pdb.set_trace()
                t = float(self.max - self.min)
                t /= self.cur - self.min
                t = (t - 1) * self.elapsed
        return '%s: %s' % (prefix, self.format_duration(t))

    @property
    def speed(self):
        if self.elapsed == 0:
            result = 0.0
        else:
            result = (self.cur - self.min) / self.elapsed
        for unit in UNITS:
            if result < 1000:
                break
            result /= 1000.0
        return '%d %sB/s' % (result, unit)


#
# Glob functionality
#

RICH_GLOB = re.compile(r'\{([^}]*)\}')
_CHECK_RECURSIVE_GLOB = re.compile(r'[^/\\,{]\*\*|\*\*[^/\\,}]')
_CHECK_MISMATCH_SET = re.compile(r'^[^{]*\}|\{[^}]*$')


def iglob(path_glob):
    """Extended globbing function that supports ** and {opt1,opt2,opt3}."""
    if _CHECK_RECURSIVE_GLOB.search(path_glob):
        msg = """invalid glob %r: recursive glob "**" must be used alone"""
        raise ValueError(msg % path_glob)
    if _CHECK_MISMATCH_SET.search(path_glob):
        msg = """invalid glob %r: mismatching set marker '{' or '}'"""
        raise ValueError(msg % path_glob)
    return _iglob(path_glob)


def _iglob(path_glob):
    rich_path_glob = RICH_GLOB.split(path_glob, 1)
    if len(rich_path_glob) > 1:
        assert len(rich_path_glob) == 3, rich_path_glob
        prefix, set, suffix = rich_path_glob
        for item in set.split(','):
            for path in _iglob(''.join((prefix, item, suffix))):
                yield path
    else:
        if '**' not in path_glob:
            for item in std_iglob(path_glob):
                yield item
        else:
            prefix, radical = path_glob.split('**', 1)
            if prefix == '':
                prefix = '.'
            if radical == '':
                radical = '*'
            else:
                # we support both
                radical = radical.lstrip('/')
                radical = radical.lstrip('\\')
            for path, dir, files in os.walk(prefix):
                path = os.path.normpath(path)
                for fn in _iglob(os.path.join(path, radical)):
                    yield fn


if ssl:
    from .compat import (HTTPSHandler as BaseHTTPSHandler, match_hostname, CertificateError)

    #
    # HTTPSConnection which verifies certificates/matches domains
    #

    class HTTPSConnection(httplib.HTTPSConnection):
        ca_certs = None  # set this to the path to the certs file (.pem)
        check_domain = True  # only used if ca_certs is not None
```
