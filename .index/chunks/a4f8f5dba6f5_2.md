# Chunk: a4f8f5dba6f5_2

- source: `.venv-lab/Lib/site-packages/ipywidgets/widgets/widget_media.py`
- lines: 172-225
- chunk: 3/3

```
ay.  You can explicitly
    define the format of the byte string using the `format` trait (which
    defaults to "mp4").

    If you pass `"url"` to the `"format"` trait, `value` will be interpreted
    as a URL as bytes encoded in UTF-8.
    """
    _view_name = Unicode('VideoView').tag(sync=True)
    _model_name = Unicode('VideoModel').tag(sync=True)

    # Define the custom state properties to sync with the front-end
    format = Unicode('mp4', help="The format of the video.").tag(sync=True)
    width = CUnicode(help="Width of the video in pixels.").tag(sync=True)
    height = CUnicode(help="Height of the video in pixels.").tag(sync=True)
    autoplay = Bool(True, help="When true, the video starts when it's displayed").tag(sync=True)
    loop = Bool(True, help="When true, the video will start from the beginning after finishing").tag(sync=True)
    controls = Bool(True, help="Specifies that video controls should be displayed (such as a play/pause button etc)").tag(sync=True)

    @classmethod
    def from_file(cls, filename, **kwargs):
        return cls._from_file('video', filename, **kwargs)

    def __repr__(self):
        return self._get_repr(Video)


@register
class Audio(_Media):
    """Displays a audio as a widget.

    The `value` of this widget accepts a byte string.  The byte string is the
    raw audio data that you want the browser to display.  You can explicitly
    define the format of the byte string using the `format` trait (which
    defaults to "mp3").

    If you pass `"url"` to the `"format"` trait, `value` will be interpreted
    as a URL as bytes encoded in UTF-8.
    """
    _view_name = Unicode('AudioView').tag(sync=True)
    _model_name = Unicode('AudioModel').tag(sync=True)

    # Define the custom state properties to sync with the front-end
    format = Unicode('mp3', help="The format of the audio.").tag(sync=True)
    autoplay = Bool(True, help="When true, the audio starts when it's displayed").tag(sync=True)
    loop = Bool(True, help="When true, the audio will start from the beginning after finishing").tag(sync=True)
    controls = Bool(True, help="Specifies that audio controls should be displayed (such as a play/pause button etc)").tag(sync=True)

    @classmethod
    def from_file(cls, filename, **kwargs):
        return cls._from_file('audio', filename, **kwargs)

    def __repr__(self):
        return self._get_repr(Audio)
```
