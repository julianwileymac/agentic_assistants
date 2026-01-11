# Chunk: bcc3c6bec4b8_3

- source: `.venv-lab/Lib/site-packages/pip/_vendor/distlib/util.py`
- lines: 224-300
- chunk: 4/25

```
          if not versions:
                        versions = None
                return versions, ver_remaining

            if remaining[0] != '(':
                versions, remaining = get_versions(remaining)
            else:
                i = remaining.find(')', 1)
                if i < 0:
                    raise SyntaxError('unterminated parenthesis: %s' % remaining)
                s = remaining[1:i]
                remaining = remaining[i + 1:].lstrip()
                # As a special diversion from PEP 508, allow a version number
                # a.b.c in parentheses as a synonym for ~= a.b.c (because this
                # is allowed in earlier PEPs)
                if COMPARE_OP.match(s):
                    versions, _ = get_versions(s)
                else:
                    m = VERSION_IDENTIFIER.match(s)
                    if not m:
                        raise SyntaxError('invalid constraint: %s' % s)
                    v = m.groups()[0]
                    s = s[m.end():].lstrip()
                    if s:
                        raise SyntaxError('invalid constraint: %s' % s)
                    versions = [('~=', v)]

    if remaining:
        if remaining[0] != ';':
            raise SyntaxError('invalid requirement: %s' % remaining)
        remaining = remaining[1:].lstrip()

        mark_expr, remaining = parse_marker(remaining)

    if remaining and remaining[0] != '#':
        raise SyntaxError('unexpected trailing data: %s' % remaining)

    if not versions:
        rs = distname
    else:
        rs = '%s %s' % (distname, ', '.join(['%s %s' % con for con in versions]))
    return Container(name=distname, extras=extras, constraints=versions, marker=mark_expr, url=uri, requirement=rs)


def get_resources_dests(resources_root, rules):
    """Find destinations for resources files"""

    def get_rel_path(root, path):
        # normalizes and returns a lstripped-/-separated path
        root = root.replace(os.path.sep, '/')
        path = path.replace(os.path.sep, '/')
        assert path.startswith(root)
        return path[len(root):].lstrip('/')

    destinations = {}
    for base, suffix, dest in rules:
        prefix = os.path.join(resources_root, base)
        for abs_base in iglob(prefix):
            abs_glob = os.path.join(abs_base, suffix)
            for abs_path in iglob(abs_glob):
                resource_file = get_rel_path(resources_root, abs_path)
                if dest is None:  # remove the entry if it was here
                    destinations.pop(resource_file, None)
                else:
                    rel_path = get_rel_path(abs_base, abs_path)
                    rel_dest = dest.replace(os.path.sep, '/').rstrip('/')
                    destinations[resource_file] = rel_dest + '/' + rel_path
    return destinations


def in_venv():
    if hasattr(sys, 'real_prefix'):
        # virtualenv venvs
        result = True
    else:
        # PEP 405 venvs
```
