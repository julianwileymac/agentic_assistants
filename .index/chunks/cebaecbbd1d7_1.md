# Chunk: cebaecbbd1d7_1

- source: `.venv-lab/Lib/site-packages/setuptools/_distutils/command/build_ext.py`
- lines: 72-158
- chunk: 2/13

```
 extensions into the source "
            "directory alongside your pure Python modules",
        ),
        (
            'include-dirs=',
            'I',
            "list of directories to search for header files" + sep_by,
        ),
        ('define=', 'D', "C preprocessor macros to define"),
        ('undef=', 'U', "C preprocessor macros to undefine"),
        ('libraries=', 'l', "external C libraries to link with"),
        (
            'library-dirs=',
            'L',
            "directories to search for external C libraries" + sep_by,
        ),
        ('rpath=', 'R', "directories to search for shared C libraries at runtime"),
        ('link-objects=', 'O', "extra explicit link objects to include in the link"),
        ('debug', 'g', "compile/link with debugging information"),
        ('force', 'f', "forcibly build everything (ignore file timestamps)"),
        ('compiler=', 'c', "specify the compiler type"),
        ('parallel=', 'j', "number of parallel build jobs"),
        ('swig-cpp', None, "make SWIG create C++ files (default is C)"),
        ('swig-opts=', None, "list of SWIG command line options"),
        ('swig=', None, "path to the SWIG executable"),
        ('user', None, "add user include, library and rpath"),
    ]

    boolean_options: ClassVar[list[str]] = [
        'inplace',
        'debug',
        'force',
        'swig-cpp',
        'user',
    ]

    help_options: ClassVar[list[tuple[str, str | None, str, Callable[[], object]]]] = [
        ('help-compiler', None, "list available compilers", show_compilers),
    ]

    def initialize_options(self):
        self.extensions = None
        self.build_lib = None
        self.plat_name = None
        self.build_temp = None
        self.inplace = False
        self.package = None

        self.include_dirs = None
        self.define = None
        self.undef = None
        self.libraries = None
        self.library_dirs = None
        self.rpath = None
        self.link_objects = None
        self.debug = None
        self.force = None
        self.compiler = None
        self.swig = None
        self.swig_cpp = None
        self.swig_opts = None
        self.user = None
        self.parallel = None

    @staticmethod
    def _python_lib_dir(sysconfig):
        """
        Resolve Python's library directory for building extensions
        that rely on a shared Python library.

        See python/cpython#44264 and python/cpython#48686
        """
        if not sysconfig.get_config_var('Py_ENABLE_SHARED'):
            return

        if sysconfig.python_build:
            yield '.'
            return

        if sys.platform == 'zos':
            # On z/OS, a user is not required to install Python to
            # a predetermined path, but can use Python portably
            installed_dir = sysconfig.get_config_var('base')
            lib_dir = sysconfig.get_config_var('platlibdir')
            yield os.path.join(installed_dir, lib_dir)
        else:
```
