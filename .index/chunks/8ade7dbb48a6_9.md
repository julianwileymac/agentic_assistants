# Chunk: 8ade7dbb48a6_9

- source: `.venv-lab/Lib/site-packages/IPython/core/magic.py`
- lines: 653-724
- chunk: 10/11

```
hlex.split.
        This allows us to easily expand variables, glob files, quote
        arguments, etc.

        Parameters
        ----------
        arg_str : str
            The arguments to parse.
        opt_str : str
            The options specification.
        mode : str, default 'string'
            If given as 'list', the argument string is returned as a list (split
            on whitespace) instead of a string.
        list_all : bool, default False
            Put all option values in lists. Normally only options
            appearing more than once are put in a list.
        posix : bool, default True
            Whether to split the input line in POSIX mode or not, as per the
            conventions outlined in the :mod:`shlex` module from the standard
            library.
        """

        # inject default options at the beginning of the input line
        caller = sys._getframe(1).f_code.co_name
        arg_str = "%s %s" % (self.options_table.get(caller, ""), arg_str)

        mode = kw.get("mode", "string")
        if mode not in ["string", "list"]:
            raise ValueError("incorrect mode given: %s" % mode)
        # Get options
        list_all = kw.get("list_all", 0)
        posix = kw.get("posix", os.name == "posix")
        strict = kw.get("strict", True)

        preserve_non_opts = kw.get("preserve_non_opts", False)
        remainder_arg_str = arg_str

        # Check if we have more than one argument to warrant extra processing:
        odict: dict[str, t.Any] = {}  # Dictionary with options
        args = arg_str.split()
        if len(args) >= 1:
            # If the list of inputs only has 0 or 1 thing in it, there's no
            # need to look for options
            argv = arg_split(arg_str, posix, strict)
            # Do regular option processing
            try:
                opts, args = getopt(argv, opt_str, long_opts)
            except GetoptError as e:
                raise UsageError(
                    '%s (allowed: "%s"%s)'
                    % (e.msg, opt_str, " ".join(("",) + long_opts) if long_opts else "")
                ) from e
            for o, a in opts:
                if mode == "string" and preserve_non_opts:
                    # remove option-parts from the original args-string and preserve remaining-part.
                    # This relies on the arg_split(...) and getopt(...)'s impl spec, that the parsed options are
                    # returned in the original order.
                    remainder_arg_str = remainder_arg_str.replace(o, "", 1).replace(
                        a, "", 1
                    )
                if o.startswith("--"):
                    o = o[2:]
                else:
                    o = o[1:]
                try:
                    odict[o].append(a)
                except AttributeError:
                    odict[o] = [odict[o], a]
                except KeyError:
                    if list_all:
                        odict[o] = [a]
```
