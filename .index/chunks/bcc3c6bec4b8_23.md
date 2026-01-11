# Chunk: bcc3c6bec4b8_23

- source: `.venv-lab/Lib/site-packages/pip/_vendor/distlib/util.py`
- lines: 1838-1923
- chunk: 24/25

```
n (self.DEFAULT_REPOSITORY, 'pypi')):
                            result['repository'] = self.DEFAULT_REPOSITORY
                        elif (result['server'] != repository and result['repository'] != repository):
                            result = {}
            elif 'server-login' in sections:
                # old format
                server = 'server-login'
                if config.has_option(server, 'repository'):
                    repository = config.get(server, 'repository')
                else:
                    repository = self.DEFAULT_REPOSITORY
                result = {
                    'username': config.get(server, 'username'),
                    'password': config.get(server, 'password'),
                    'repository': repository,
                    'server': server,
                    'realm': self.DEFAULT_REALM
                }
        return result

    def update(self, username, password):
        # import pdb; pdb.set_trace()
        config = configparser.RawConfigParser()
        fn = self.filename
        config.read(fn)
        if not config.has_section('pypi'):
            config.add_section('pypi')
        config.set('pypi', 'username', username)
        config.set('pypi', 'password', password)
        with open(fn, 'w') as f:
            config.write(f)


def _load_pypirc(index):
    """
    Read the PyPI access configuration as supported by distutils.
    """
    return PyPIRCFile(url=index.url).read()


def _store_pypirc(index):
    PyPIRCFile().update(index.username, index.password)


#
# get_platform()/get_host_platform() copied from Python 3.10.a0 source, with some minor
# tweaks
#


def get_host_platform():
    """Return a string that identifies the current platform.  This is used mainly to
    distinguish platform-specific build directories and platform-specific built
    distributions.  Typically includes the OS name and version and the
    architecture (as supplied by 'os.uname()'), although the exact information
    included depends on the OS; eg. on Linux, the kernel version isn't
    particularly important.

    Examples of returned values:
       linux-i586
       linux-alpha (?)
       solaris-2.6-sun4u

    Windows will return one of:
       win-amd64 (64bit Windows on AMD64 (aka x86_64, Intel64, EM64T, etc)
       win32 (all others - specifically, sys.platform is returned)

    For other non-POSIX platforms, currently just returns 'sys.platform'.

    """
    if os.name == 'nt':
        if 'amd64' in sys.version.lower():
            return 'win-amd64'
        if '(arm)' in sys.version.lower():
            return 'win-arm32'
        if '(arm64)' in sys.version.lower():
            return 'win-arm64'
        return sys.platform

    # Set for cross builds explicitly
    if "_PYTHON_HOST_PLATFORM" in os.environ:
        return os.environ["_PYTHON_HOST_PLATFORM"]

    if os.name != 'posix' or not hasattr(os, 'uname'):
        # XXX what about the architecture? NT is Intel or Alpha,
```
