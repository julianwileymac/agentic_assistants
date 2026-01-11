# Chunk: bcc3c6bec4b8_21

- source: `.venv-lab/Lib/site-packages/pip/_vendor/distlib/util.py`
- lines: 1687-1778
- chunk: 22/25

```
 if isinstance(o, (list, tuple)):
                result = type(o)([convert(i) for i in o])
            elif isinstance(o, dict):
                if '()' in o:
                    result = self.configure_custom(o)
                else:
                    result = {}
                    for k in o:
                        result[k] = convert(o[k])
            else:
                result = self.convert(o)
            return result

        c = config.pop('()')
        if not callable(c):
            c = self.resolve(c)
        props = config.pop('.', None)
        # Check for valid identifiers
        args = config.pop('[]', ())
        if args:
            args = tuple([convert(o) for o in args])
        items = [(k, convert(config[k])) for k in config if valid_ident(k)]
        kwargs = dict(items)
        result = c(*args, **kwargs)
        if props:
            for n, v in props.items():
                setattr(result, n, convert(v))
        return result

    def __getitem__(self, key):
        result = self.config[key]
        if isinstance(result, dict) and '()' in result:
            self.config[key] = result = self.configure_custom(result)
        return result

    def inc_convert(self, value):
        """Default converter for the inc:// protocol."""
        if not os.path.isabs(value):
            value = os.path.join(self.base, value)
        with codecs.open(value, 'r', encoding='utf-8') as f:
            result = json.load(f)
        return result


class SubprocessMixin(object):
    """
    Mixin for running subprocesses and capturing their output
    """

    def __init__(self, verbose=False, progress=None):
        self.verbose = verbose
        self.progress = progress

    def reader(self, stream, context):
        """
        Read lines from a subprocess' output stream and either pass to a progress
        callable (if specified) or write progress information to sys.stderr.
        """
        progress = self.progress
        verbose = self.verbose
        while True:
            s = stream.readline()
            if not s:
                break
            if progress is not None:
                progress(s, context)
            else:
                if not verbose:
                    sys.stderr.write('.')
                else:
                    sys.stderr.write(s.decode('utf-8'))
                sys.stderr.flush()
        stream.close()

    def run_command(self, cmd, **kwargs):
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs)
        t1 = threading.Thread(target=self.reader, args=(p.stdout, 'stdout'))
        t1.start()
        t2 = threading.Thread(target=self.reader, args=(p.stderr, 'stderr'))
        t2.start()
        p.wait()
        t1.join()
        t2.join()
        if self.progress is not None:
            self.progress('done.', 'main')
        elif self.verbose:
            sys.stderr.write('done.\n')
        return p


def normalize_name(name):
```
