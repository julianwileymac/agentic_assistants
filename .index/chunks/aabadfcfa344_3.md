# Chunk: aabadfcfa344_3

- source: `.venv-lab/Lib/site-packages/setuptools/_distutils/command/config.py`
- lines: 214-312
- chunk: 4/5

```
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
        lang="c",
    ):
        """Try to compile and link a source file, built from 'body' and
        'headers', to executable form.  Return true on success, false
        otherwise.
        """
        self._check_compiler()
        try:
            self._link(body, headers, include_dirs, libraries, library_dirs, lang)
            ok = True
        except (CompileError, LinkError):
            ok = False

        log.info(ok and "success!" or "failure.")
        self._clean()
        return ok

    def try_run(
        self,
        body,
        headers=None,
        include_dirs=None,
        libraries=None,
        library_dirs=None,
        lang="c",
    ):
        """Try to compile, link to an executable, and run a program
        built from 'body' and 'headers'.  Return true on success, false
        otherwise.
        """
        self._check_compiler()
        try:
            src, obj, exe = self._link(
                body, headers, include_dirs, libraries, library_dirs, lang
            )
            self.spawn([exe])
            ok = True
        except (CompileError, LinkError, DistutilsExecError):
            ok = False

        log.info(ok and "success!" or "failure.")
        self._clean()
        return ok

    # -- High-level methods --------------------------------------------
    # (these are the ones that are actually likely to be useful
    # when implementing a real-world config command!)

    def check_func(
        self,
        func,
        headers=None,
        include_dirs=None,
        libraries=None,
        library_dirs=None,
        decl=False,
        call=False,
    ):
        """Determine if function 'func' is available by constructing a
        source file that refers to 'func', and compiles and links it.
        If everything succeeds, returns true; otherwise returns false.

        The constructed source file starts out by including the header
        files listed in 'headers'.  If 'decl' is true, it then declares
        'func' (as "int func()"); you probably shouldn't supply 'headers'
        and set 'decl' true in the same call, or you might get errors about
        a conflicting declarations for 'func'.  Finally, the constructed
        'main()' function either references 'func' or (if 'call' is true)
        calls it.  'libraries' and 'library_dirs' are used when
        linking.
        """
        self._check_compiler()
        body = []
        if decl:
            body.append(f"int {func} ();")
        body.append("int main () {")
        if call:
            body.append(f"  {func}();")
        else:
            body.append(f"  {func};")
        body.append("}")
        body = "\n".join(body) + "\n"
```
