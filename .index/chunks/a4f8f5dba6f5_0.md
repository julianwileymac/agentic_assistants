# Chunk: a4f8f5dba6f5_0

- source: `.venv-lab/Lib/site-packages/ipywidgets/widgets/widget_media.py`
- lines: 1-105
- chunk: 1/3

```
# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

import mimetypes

from .widget_core import CoreWidget
from .domwidget import DOMWidget
from .valuewidget import ValueWidget
from .widget import register
from traitlets import Unicode, CUnicode, Bool
from .trait_types import CByteMemoryView


@register
class _Media(DOMWidget, ValueWidget, CoreWidget):
    """Base class for Image, Audio and Video widgets.

    The `value` of this widget accepts a byte string.  The byte string is the
    raw data that you want the browser to display.

    If you pass `"url"` to the `"format"` trait, `value` will be interpreted
    as a URL as bytes encoded in UTF-8.
    """

    # Define the custom state properties to sync with the front-end
    value = CByteMemoryView(help="The media data as a memory view of bytes.").tag(sync=True)

    @classmethod
    def _from_file(cls, tag, filename, **kwargs):
        """
        Create an :class:`Media` from a local file.

        Parameters
        ----------
        filename: str
            The location of a file to read into the value from disk.

        **kwargs:
            The keyword arguments for `Media`

        Returns an `Media` with the value set from the filename.
        """
        value = cls._load_file_value(filename)

        if 'format' not in kwargs:
            format = cls._guess_format(tag, filename)
            if format is not None:
                kwargs['format'] = format

        return cls(value=value, **kwargs)

    @classmethod
    def from_url(cls, url, **kwargs):
        """
        Create an :class:`Media` from a URL.

        :code:`Media.from_url(url)` is equivalent to:

        .. code-block: python

            med = Media(value=url, format='url')

        But both unicode and bytes arguments are allowed for ``url``.

        Parameters
        ----------
        url: [str, bytes]
            The location of a URL to load.
        """
        if isinstance(url, str):
            # If str, it needs to be encoded to bytes
            url = url.encode('utf-8')

        return cls(value=url, format='url', **kwargs)

    def set_value_from_file(self, filename):
        """
        Convenience method for reading a file into `value`.

        Parameters
        ----------
        filename: str
            The location of a file to read into value from disk.
        """
        value = self._load_file_value(filename)

        self.value = value

    @classmethod
    def _load_file_value(cls, filename):
        if getattr(filename, 'read', None) is not None:
            return filename.read()
        else:
            with open(filename, 'rb') as f:
                return f.read()

    @classmethod
    def _guess_format(cls, tag, filename):
        # file objects may have a .name parameter
        name = getattr(filename, 'name', None)
        name = name or filename

        try:
            mtype, _ = mimetypes.guess_type(name)
```
