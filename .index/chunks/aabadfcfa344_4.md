# Chunk: aabadfcfa344_4

- source: `.venv-lab/Lib/site-packages/setuptools/_distutils/command/config.py`
- lines: 300-359
- chunk: 5/5

```
_compiler()
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

        return self.try_link(body, headers, include_dirs, libraries, library_dirs)

    def check_lib(
        self,
        library,
        library_dirs=None,
        headers=None,
        include_dirs=None,
        other_libraries: Sequence[str] = [],
    ):
        """Determine if 'library' is available to be linked against,
        without actually checking that any particular symbols are provided
        by it.  'headers' will be used in constructing the source file to
        be compiled, but the only effect of this is to check if all the
        header files listed are available.  Any libraries listed in
        'other_libraries' will be included in the link, in case 'library'
        has symbols that depend on other libraries.
        """
        self._check_compiler()
        return self.try_link(
            "int main (void) { }",
            headers,
            include_dirs,
            [library] + list(other_libraries),
            library_dirs,
        )

    def check_header(self, header, include_dirs=None, library_dirs=None, lang="c"):
        """Determine if the system header file named by 'header_file'
        exists and can be found by the preprocessor; return true if so,
        false otherwise.
        """
        return self.try_cpp(
            body="/* No body */", headers=[header], include_dirs=include_dirs
        )


def dump_file(filename, head=None):
    """Dumps a file content into log.info.

    If head is not None, will be dumped before the file content.
    """
    if head is None:
        log.info('%s', filename)
    else:
        log.info(head)
    log.info(pathlib.Path(filename).read_text(encoding='utf-8'))
```
