# Chunk: aabadfcfa344_2

- source: `.venv-lab/Lib/site-packages/setuptools/_distutils/command/config.py`
- lines: 149-229
- chunk: 3/5

```
enames):
        if not filenames:
            filenames = self.temp_files
            self.temp_files = []
        log.info("removing: %s", ' '.join(filenames))
        for filename in filenames:
            try:
                os.remove(filename)
            except OSError:
                pass

    # XXX these ignore the dry-run flag: what to do, what to do? even if
    # you want a dry-run build, you still need some sort of configuration
    # info.  My inclination is to make it up to the real config command to
    # consult 'dry_run', and assume a default (minimal) configuration if
    # true.  The problem with trying to do it here is that you'd have to
    # return either true or false from all the 'try' methods, neither of
    # which is correct.

    # XXX need access to the header search path and maybe default macros.

    def try_cpp(self, body=None, headers=None, include_dirs=None, lang="c"):
        """Construct a source file from 'body' (a string containing lines
        of C/C++ code) and 'headers' (a list of header files to include)
        and run it through the preprocessor.  Return true if the
        preprocessor succeeded, false if there were any errors.
        ('body' probably isn't of much use, but what the heck.)
        """
        self._check_compiler()
        ok = True
        try:
            self._preprocess(body, headers, include_dirs, lang)
        except CompileError:
            ok = False

        self._clean()
        return ok

    def search_cpp(self, pattern, body=None, headers=None, include_dirs=None, lang="c"):
        """Construct a source file (just like 'try_cpp()'), run it through
        the preprocessor, and return true if any line of the output matches
        'pattern'.  'pattern' should either be a compiled regex object or a
        string containing a regex.  If both 'body' and 'headers' are None,
        preprocesses an empty file -- which can be useful to determine the
        symbols the preprocessor and compiler set by default.
        """
        self._check_compiler()
        src, out = self._preprocess(body, headers, include_dirs, lang)

        if isinstance(pattern, str):
            pattern = re.compile(pattern)

        with open(out, encoding='utf-8') as file:
            match = any(pattern.search(line) for line in file)

        self._clean()
        return match

    def try_compile(self, body, headers=None, include_dirs=None, lang="c"):
        """Try to compile a source file built from 'body' and 'headers'.
        Return true on success, false otherwise.
        """
        self._check_compiler()
        try:
            self._compile(body, headers, include_dirs, lang)
            ok = True
        except CompileError:
            ok = False

        log.info(ok and "success!" or "failure.")
        self._clean()
        return ok

    def try_link(
        self,
        body,
        headers=None,
        include_dirs=None,
        libraries=None,
        library_dirs=None,
```
