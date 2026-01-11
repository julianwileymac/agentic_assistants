# Chunk: adb34eb6a0ca_1

- source: `.venv-lab/Lib/site-packages/IPython/utils/sysinfo.py`
- lines: 91-121
- chunk: 2/2

```
tform=sys.platform,
        platform=platform.platform(),
        os_name=os.name,
        default_encoding=encoding.DEFAULT_ENCODING,
        )

def get_sys_info() -> dict:
    """Return useful information about IPython and the system, as a dict."""
    path = Path(__file__, "..").resolve().parent
    return pkg_info(str(path))

def sys_info() -> str:
    """Return useful information about IPython and the system, as a string.

    Examples
    --------
    ::
    
        In [2]: print(sys_info())
        {'commit_hash': '144fdae',      # random
         'commit_source': 'repository',
         'ipython_path': '/home/fperez/usr/lib/python2.6/site-packages/IPython',
         'ipython_version': '0.11.dev',
         'os_name': 'posix',
         'platform': 'Linux-2.6.35-22-generic-i686-with-Ubuntu-10.10-maverick',
         'sys_executable': '/usr/bin/python',
         'sys_platform': 'linux2',
         'sys_version': '2.6.6 (r266:84292, Sep 15 2010, 15:52:39) \\n[GCC 4.4.5]'}
    """
    return pprint.pformat(get_sys_info())
```
