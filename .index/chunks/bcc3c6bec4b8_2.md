# Chunk: bcc3c6bec4b8_2

- source: `.venv-lab/Lib/site-packages/pip/_vendor/distlib/util.py`
- lines: 161-233
- chunk: 3/25

```
ated extra: %s' % remaining)
        s = remaining[1:i]
        remaining = remaining[i + 1:].lstrip()
        extras = []
        while s:
            m = IDENTIFIER.match(s)
            if not m:
                raise SyntaxError('malformed extra: %s' % s)
            extras.append(m.groups()[0])
            s = s[m.end():]
            if not s:
                break
            if s[0] != ',':
                raise SyntaxError('comma expected in extras: %s' % s)
            s = s[1:].lstrip()
        if not extras:
            extras = None
    if remaining:
        if remaining[0] == '@':
            # it's a URI
            remaining = remaining[1:].lstrip()
            m = NON_SPACE.match(remaining)
            if not m:
                raise SyntaxError('invalid URI: %s' % remaining)
            uri = m.groups()[0]
            t = urlparse(uri)
            # there are issues with Python and URL parsing, so this test
            # is a bit crude. See bpo-20271, bpo-23505. Python doesn't
            # always parse invalid URLs correctly - it should raise
            # exceptions for malformed URLs
            if not (t.scheme and t.netloc):
                raise SyntaxError('Invalid URL: %s' % uri)
            remaining = remaining[m.end():].lstrip()
        else:

            def get_versions(ver_remaining):
                """
                Return a list of operator, version tuples if any are
                specified, else None.
                """
                m = COMPARE_OP.match(ver_remaining)
                versions = None
                if m:
                    versions = []
                    while True:
                        op = m.groups()[0]
                        ver_remaining = ver_remaining[m.end():]
                        m = VERSION_IDENTIFIER.match(ver_remaining)
                        if not m:
                            raise SyntaxError('invalid version: %s' % ver_remaining)
                        v = m.groups()[0]
                        versions.append((op, v))
                        ver_remaining = ver_remaining[m.end():]
                        if not ver_remaining or ver_remaining[0] != ',':
                            break
                        ver_remaining = ver_remaining[1:].lstrip()
                        # Some packages have a trailing comma which would break things
                        # See issue #148
                        if not ver_remaining:
                            break
                        m = COMPARE_OP.match(ver_remaining)
                        if not m:
                            raise SyntaxError('invalid constraint: %s' % ver_remaining)
                    if not versions:
                        versions = None
                return versions, ver_remaining

            if remaining[0] != '(':
                versions, remaining = get_versions(remaining)
            else:
                i = remaining.find(')', 1)
                if i < 0:
```
