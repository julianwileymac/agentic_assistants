# Chunk: bcc3c6bec4b8_20

- source: `.venv-lab/Lib/site-packages/pip/_vendor/distlib/util.py`
- lines: 1588-1695
- chunk: 21/25

```
            else:
                tcls = Transport
            kwargs['transport'] = t = tcls(timeout, use_datetime=use_datetime)
            self.transport = t
        xmlrpclib.ServerProxy.__init__(self, uri, **kwargs)


#
# CSV functionality. This is provided because on 2.x, the csv module can't
# handle Unicode. However, we need to deal with Unicode in e.g. RECORD files.
#


def _csv_open(fn, mode, **kwargs):
    if sys.version_info[0] < 3:
        mode += 'b'
    else:
        kwargs['newline'] = ''
        # Python 3 determines encoding from locale. Force 'utf-8'
        # file encoding to match other forced utf-8 encoding
        kwargs['encoding'] = 'utf-8'
    return open(fn, mode, **kwargs)


class CSVBase(object):
    defaults = {
        'delimiter': str(','),  # The strs are used because we need native
        'quotechar': str('"'),  # str in the csv API (2.x won't take
        'lineterminator': str('\n')  # Unicode)
    }

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        self.stream.close()


class CSVReader(CSVBase):

    def __init__(self, **kwargs):
        if 'stream' in kwargs:
            stream = kwargs['stream']
            if sys.version_info[0] >= 3:
                # needs to be a text stream
                stream = codecs.getreader('utf-8')(stream)
            self.stream = stream
        else:
            self.stream = _csv_open(kwargs['path'], 'r')
        self.reader = csv.reader(self.stream, **self.defaults)

    def __iter__(self):
        return self

    def next(self):
        result = next(self.reader)
        if sys.version_info[0] < 3:
            for i, item in enumerate(result):
                if not isinstance(item, text_type):
                    result[i] = item.decode('utf-8')
        return result

    __next__ = next


class CSVWriter(CSVBase):

    def __init__(self, fn, **kwargs):
        self.stream = _csv_open(fn, 'w')
        self.writer = csv.writer(self.stream, **self.defaults)

    def writerow(self, row):
        if sys.version_info[0] < 3:
            r = []
            for item in row:
                if isinstance(item, text_type):
                    item = item.encode('utf-8')
                r.append(item)
            row = r
        self.writer.writerow(row)


#
#   Configurator functionality
#


class Configurator(BaseConfigurator):

    value_converters = dict(BaseConfigurator.value_converters)
    value_converters['inc'] = 'inc_convert'

    def __init__(self, config, base=None):
        super(Configurator, self).__init__(config)
        self.base = base or os.getcwd()

    def configure_custom(self, config):

        def convert(o):
            if isinstance(o, (list, tuple)):
                result = type(o)([convert(i) for i in o])
            elif isinstance(o, dict):
                if '()' in o:
                    result = self.configure_custom(o)
                else:
                    result = {}
                    for k in o:
```
