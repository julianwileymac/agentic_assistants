# Chunk: 8ade7dbb48a6_8

- source: `.venv-lab/Lib/site-packages/IPython/core/magic.py`
- lines: 596-664
- chunk: 9/11

```
# they can only record the names of the methods they are supposed to
        # grab.  Only now, that the instance exists, can we create the proper
        # mapping to bound methods.  So we read the info off the original names
        # table and replace each method name by the actual bound method.
        # But we mustn't clobber the *class* mapping, in case of multiple instances.
        class_magics = self.magics
        self.magics = {}
        for mtype in magic_kinds:
            tab = self.magics[mtype] = {}
            cls_tab = class_magics[mtype]
            for magic_name, meth_name in cls_tab.items():
                if isinstance(meth_name, str):
                    # it's a method name, grab it
                    tab[magic_name] = getattr(self, meth_name)
                else:
                    # it's the real thing
                    tab[magic_name] = meth_name
        # Configurable **needs** to be initiated at the end or the config
        # magics get screwed up.
        super(Magics, self).__init__(**kwargs)

    def arg_err(self, func):
        """Print docstring if incorrect arguments were passed"""
        print("Error in arguments:")
        print(oinspect.getdoc(func))

    def format_latex(self, strng):
        """Format a string for latex inclusion."""

        # Characters that need to be escaped for latex:
        escape_re = re.compile(r"(%|_|\$|#|&)", re.MULTILINE)
        # Magic command names as headers:
        cmd_name_re = re.compile(r"^(%s.*?):" % ESC_MAGIC, re.MULTILINE)
        # Magic commands
        cmd_re = re.compile(r"(?P<cmd>%s.+?\b)(?!\}\}:)" % ESC_MAGIC, re.MULTILINE)
        # Paragraph continue
        par_re = re.compile(r"\\$", re.MULTILINE)

        # The "\n" symbol
        newline_re = re.compile(r"\\n")

        # Now build the string for output:
        # strng = cmd_name_re.sub(r'\n\\texttt{\\textsl{\\large \1}}:',strng)
        strng = cmd_name_re.sub(r"\n\\bigskip\n\\texttt{\\textbf{ \1}}:", strng)
        strng = cmd_re.sub(r"\\texttt{\g<cmd>}", strng)
        strng = par_re.sub(r"\\\\", strng)
        strng = escape_re.sub(r"\\\1", strng)
        strng = newline_re.sub(r"\\textbackslash{}n", strng)
        return strng

    def parse_options(self, arg_str, opt_str, *long_opts, **kw):
        """Parse options passed to an argument string.

        The interface is similar to that of :func:`getopt.getopt`, but it
        returns a :class:`~IPython.utils.struct.Struct` with the options as keys
        and the stripped argument string still as a string.

        arg_str is quoted as a true sys.argv vector by using shlex.split.
        This allows us to easily expand variables, glob files, quote
        arguments, etc.

        Parameters
        ----------
        arg_str : str
            The arguments to parse.
        opt_str : str
            The options specification.
        mode : str, default 'string'
```
