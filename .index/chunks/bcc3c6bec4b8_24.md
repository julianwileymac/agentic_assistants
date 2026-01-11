# Chunk: bcc3c6bec4b8_24

- source: `.venv-lab/Lib/site-packages/pip/_vendor/distlib/util.py`
- lines: 1914-1985
- chunk: 25/25

```
rn 'win-arm64'
        return sys.platform

    # Set for cross builds explicitly
    if "_PYTHON_HOST_PLATFORM" in os.environ:
        return os.environ["_PYTHON_HOST_PLATFORM"]

    if os.name != 'posix' or not hasattr(os, 'uname'):
        # XXX what about the architecture? NT is Intel or Alpha,
        # Mac OS is M68k or PPC, etc.
        return sys.platform

    # Try to distinguish various flavours of Unix

    (osname, host, release, version, machine) = os.uname()

    # Convert the OS name to lowercase, remove '/' characters, and translate
    # spaces (for "Power Macintosh")
    osname = osname.lower().replace('/', '')
    machine = machine.replace(' ', '_').replace('/', '-')

    if osname[:5] == 'linux':
        # At least on Linux/Intel, 'machine' is the processor --
        # i386, etc.
        # XXX what about Alpha, SPARC, etc?
        return "%s-%s" % (osname, machine)

    elif osname[:5] == 'sunos':
        if release[0] >= '5':  # SunOS 5 == Solaris 2
            osname = 'solaris'
            release = '%d.%s' % (int(release[0]) - 3, release[2:])
            # We can't use 'platform.architecture()[0]' because a
            # bootstrap problem. We use a dict to get an error
            # if some suspicious happens.
            bitness = {2147483647: '32bit', 9223372036854775807: '64bit'}
            machine += '.%s' % bitness[sys.maxsize]
        # fall through to standard osname-release-machine representation
    elif osname[:3] == 'aix':
        from _aix_support import aix_platform
        return aix_platform()
    elif osname[:6] == 'cygwin':
        osname = 'cygwin'
        rel_re = re.compile(r'[\d.]+', re.ASCII)
        m = rel_re.match(release)
        if m:
            release = m.group()
    elif osname[:6] == 'darwin':
        import _osx_support
        try:
            from distutils import sysconfig
        except ImportError:
            import sysconfig
        osname, release, machine = _osx_support.get_platform_osx(sysconfig.get_config_vars(), osname, release, machine)

    return '%s-%s-%s' % (osname, release, machine)


_TARGET_TO_PLAT = {
    'x86': 'win32',
    'x64': 'win-amd64',
    'arm': 'win-arm32',
}


def get_platform():
    if os.name != 'nt':
        return get_host_platform()
    cross_compilation_target = os.environ.get('VSCMD_ARG_TGT_ARCH')
    if cross_compilation_target not in _TARGET_TO_PLAT:
        return get_host_platform()
    return _TARGET_TO_PLAT[cross_compilation_target]
```
