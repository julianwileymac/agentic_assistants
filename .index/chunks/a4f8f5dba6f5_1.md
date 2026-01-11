# Chunk: a4f8f5dba6f5_1

- source: `.venv-lab/Lib/site-packages/ipywidgets/widgets/widget_media.py`
- lines: 94-180
- chunk: 2/3

```
, 'rb') as f:
                return f.read()

    @classmethod
    def _guess_format(cls, tag, filename):
        # file objects may have a .name parameter
        name = getattr(filename, 'name', None)
        name = name or filename

        try:
            mtype, _ = mimetypes.guess_type(name)
            if not mtype.startswith('{}/'.format(tag)):
                return None

            return mtype[len('{}/'.format(tag)):]
        except Exception:
            return None

    def _get_repr(self, cls):
        # Truncate the value in the repr, since it will
        # typically be very, very large.
        class_name = self.__class__.__name__

        # Return value first like a ValueWidget
        signature = []

        sig_value = 'value={!r}'.format(self.value[:40].tobytes())
        if self.value.nbytes > 40:
            sig_value = sig_value[:-1]+"..."+sig_value[-1]
        signature.append(sig_value)

        for key in super(cls, self)._repr_keys():
            if key == 'value':
                continue
            value = str(getattr(self, key))
            signature.append('{}={!r}'.format(key, value))
        signature = ', '.join(signature)
        return '{}({})'.format(class_name, signature)


@register
class Image(_Media):
    """Displays an image as a widget.

    The `value` of this widget accepts a byte string.  The byte string is the
    raw image data that you want the browser to display.  You can explicitly
    define the format of the byte string using the `format` trait (which
    defaults to "png").

    If you pass `"url"` to the `"format"` trait, `value` will be interpreted
    as a URL as bytes encoded in UTF-8.
    """
    _view_name = Unicode('ImageView').tag(sync=True)
    _model_name = Unicode('ImageModel').tag(sync=True)

    # Define the custom state properties to sync with the front-end
    format = Unicode('png', help="The format of the image.").tag(sync=True)
    width = CUnicode(help="Width of the image in pixels. Use layout.width "
                          "for styling the widget.").tag(sync=True)
    height = CUnicode(help="Height of the image in pixels. Use layout.height "
                           "for styling the widget.").tag(sync=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def from_file(cls, filename, **kwargs):
        return cls._from_file('image', filename, **kwargs)

    def __repr__(self):
        return self._get_repr(Image)


@register
class Video(_Media):
    """Displays a video as a widget.

    The `value` of this widget accepts a byte string.  The byte string is the
    raw video data that you want the browser to display.  You can explicitly
    define the format of the byte string using the `format` trait (which
    defaults to "mp4").

    If you pass `"url"` to the `"format"` trait, `value` will be interpreted
    as a URL as bytes encoded in UTF-8.
    """
    _view_name = Unicode('VideoView').tag(sync=True)
```
