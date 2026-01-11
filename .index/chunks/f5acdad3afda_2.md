# Chunk: f5acdad3afda_2

- source: `.venv-lab/Lib/site-packages/ipywidgets/widgets/widget_output.py`
- lines: 151-194
- chunk: 3/3

```
unter == 0:
            self.msg_id = ''
        # suppress exceptions when in IPython, since they are shown above,
        # otherwise let someone else handle it
        return True if kernel else None

    def _flush(self):
        """Flush stdout and stderr buffers."""
        sys.stdout.flush()
        sys.stderr.flush()

    def _append_stream_output(self, text, stream_name):
        """Append a stream output."""
        self.outputs += (
            {'output_type': 'stream', 'name': stream_name, 'text': text},
        )

    def append_stdout(self, text):
        """Append text to the stdout stream."""
        self._append_stream_output(text, stream_name='stdout')

    def append_stderr(self, text):
        """Append text to the stderr stream."""
        self._append_stream_output(text, stream_name='stderr')

    def append_display_data(self, display_object):
        """Append a display object as an output.

        Parameters
        ----------
        display_object : IPython.core.display.DisplayObject
            The object to display (e.g., an instance of
            `IPython.display.Markdown` or `IPython.display.Image`).
        """
        fmt = InteractiveShell.instance().display_formatter.format
        data, metadata = fmt(display_object)
        self.outputs += (
            {
                'output_type': 'display_data',
                'data': data,
                'metadata': metadata
            },
        )
```
