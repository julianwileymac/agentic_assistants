# Chunk: e7171dfbebe2_4

- source: `.venv-lab/Lib/site-packages/urllib3/contrib/emscripten/fetch.py`
- lines: 304-405
- chunk: 5/9

```

    response. This requires support for WebAssembly JavaScript Promise Integration
    in the containing browser, and for pyodide to be launched via runPythonAsync.

    :param js_read_stream:
        The JavaScript stream reader

    :param timeout:
        Timeout in seconds

    :param request:
        The request we're handling

    :param response:
        The response this stream relates to

    :param js_abort_controller:
        A JavaScript AbortController object, used for timeouts
    """

    def __init__(
        self,
        js_read_stream: Any,
        timeout: float,
        request: EmscriptenRequest,
        response: EmscriptenResponse,
        js_abort_controller: Any,  # JavaScript AbortController for timeouts
    ):
        self.js_read_stream = js_read_stream
        self.timeout = timeout
        self._is_closed = False
        self._is_done = False
        self.request: EmscriptenRequest | None = request
        self.response: EmscriptenResponse | None = response
        self.current_buffer = None
        self.current_buffer_pos = 0
        self.js_abort_controller = js_abort_controller

    def __del__(self) -> None:
        self.close()

    # this is compatible with _base_connection
    def is_closed(self) -> bool:
        return self._is_closed

    # for compatibility with RawIOBase
    @property
    def closed(self) -> bool:
        return self.is_closed()

    def close(self) -> None:
        if self.is_closed():
            return
        self.read_len = 0
        self.read_pos = 0
        self.js_read_stream.cancel()
        self.js_read_stream = None
        self._is_closed = True
        self._is_done = True
        self.request = None
        self.response = None
        super().close()

    def readable(self) -> bool:
        return True

    def writable(self) -> bool:
        return False

    def seekable(self) -> bool:
        return False

    def _get_next_buffer(self) -> bool:
        result_js = _run_sync_with_timeout(
            self.js_read_stream.read(),
            self.timeout,
            self.js_abort_controller,
            request=self.request,
            response=self.response,
        )
        if result_js.done:
            self._is_done = True
            return False
        else:
            self.current_buffer = result_js.value.to_py()
            self.current_buffer_pos = 0
            return True

    def readinto(self, byte_obj: Buffer) -> int:
        if self.current_buffer is None:
            if not self._get_next_buffer() or self.current_buffer is None:
                self.close()
                return 0
        ret_length = min(
            len(byte_obj), len(self.current_buffer) - self.current_buffer_pos
        )
        byte_obj[0:ret_length] = self.current_buffer[
            self.current_buffer_pos : self.current_buffer_pos + ret_length
        ]
        self.current_buffer_pos += ret_length
        if self.current_buffer_pos == len(self.current_buffer):
```
