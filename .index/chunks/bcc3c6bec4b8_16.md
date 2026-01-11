# Chunk: bcc3c6bec4b8_16

- source: `.venv-lab/Lib/site-packages/pip/_vendor/distlib/util.py`
- lines: 1272-1380
- chunk: 17/25

```
tion of dangerous items, if this Python
        # allows it easily. If not, just trust the input.
        # See: https://docs.python.org/3/library/tarfile.html#extraction-filters
        def extraction_filter(member, path):
            """Run tarfile.tar_filter, but raise the expected ValueError"""
            # This is only called if the current Python has tarfile filters
            try:
                return tarfile.tar_filter(member, path)
            except tarfile.FilterError as exc:
                raise ValueError(str(exc))

        archive.extraction_filter = extraction_filter

        archive.extractall(dest_dir)

    finally:
        if archive:
            archive.close()


def zip_dir(directory):
    """zip a directory tree into a BytesIO object"""
    result = io.BytesIO()
    dlen = len(directory)
    with ZipFile(result, "w") as zf:
        for root, dirs, files in os.walk(directory):
            for name in files:
                full = os.path.join(root, name)
                rel = root[dlen:]
                dest = os.path.join(rel, name)
                zf.write(full, dest)
    return result


#
# Simple progress bar
#

UNITS = ('', 'K', 'M', 'G', 'T', 'P')


class Progress(object):
    unknown = 'UNKNOWN'

    def __init__(self, minval=0, maxval=100):
        assert maxval is None or maxval >= minval
        self.min = self.cur = minval
        self.max = maxval
        self.started = None
        self.elapsed = 0
        self.done = False

    def update(self, curval):
        assert self.min <= curval
        assert self.max is None or curval <= self.max
        self.cur = curval
        now = time.time()
        if self.started is None:
            self.started = now
        else:
            self.elapsed = now - self.started

    def increment(self, incr):
        assert incr >= 0
        self.update(self.cur + incr)

    def start(self):
        self.update(self.min)
        return self

    def stop(self):
        if self.max is not None:
            self.update(self.max)
        self.done = True

    @property
    def maximum(self):
        return self.unknown if self.max is None else self.max

    @property
    def percentage(self):
        if self.done:
            result = '100 %'
        elif self.max is None:
            result = ' ?? %'
        else:
            v = 100.0 * (self.cur - self.min) / (self.max - self.min)
            result = '%3d %%' % v
        return result

    def format_duration(self, duration):
        if (duration <= 0) and self.max is None or self.cur == self.min:
            result = '??:??:??'
        # elif duration < 1:
        #     result = '--:--:--'
        else:
            result = time.strftime('%H:%M:%S', time.gmtime(duration))
        return result

    @property
    def ETA(self):
        if self.done:
            prefix = 'Done'
            t = self.elapsed
            # import pdb; pdb.set_trace()
        else:
            prefix = 'ETA '
            if self.max is None:
```
