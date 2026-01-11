# Chunk: ad4daf127d6b_6

- source: `.venv-lab/Lib/site-packages/tornado/iostream.py`
- lines: 447-529
- chunk: 7/25

```
st copy data already in read buffer
        available_bytes = self._read_buffer_size
        n = len(buf)
        if available_bytes >= n:
            buf[:] = memoryview(self._read_buffer)[:n]
            del self._read_buffer[:n]
            self._after_user_read_buffer = self._read_buffer
        elif available_bytes > 0:
            buf[:available_bytes] = memoryview(self._read_buffer)[:]

        # Set up the supplied buffer as our temporary read buffer.
        # The original (if it had any data remaining) has been
        # saved for later.
        self._user_read_buffer = True
        self._read_buffer = buf
        self._read_buffer_size = available_bytes
        self._read_bytes = n
        self._read_partial = partial

        try:
            self._try_inline_read()
        except:
            future.add_done_callback(lambda f: f.exception())
            raise
        return future

    def read_until_close(self) -> Awaitable[bytes]:
        """Asynchronously reads all data from the socket until it is closed.

        This will buffer all available data until ``max_buffer_size``
        is reached. If flow control or cancellation are desired, use a
        loop with `read_bytes(partial=True) <.read_bytes>` instead.

        .. versionchanged:: 4.0
            The callback argument is now optional and a `.Future` will
            be returned if it is omitted.

        .. versionchanged:: 6.0

           The ``callback`` and ``streaming_callback`` arguments have
           been removed. Use the returned `.Future` (and `read_bytes`
           with ``partial=True`` for ``streaming_callback``) instead.

        """
        future = self._start_read()
        if self.closed():
            self._finish_read(self._read_buffer_size)
            return future
        self._read_until_close = True
        try:
            self._try_inline_read()
        except:
            future.add_done_callback(lambda f: f.exception())
            raise
        return future

    def write(self, data: Union[bytes, memoryview]) -> "Future[None]":
        """Asynchronously write the given data to this stream.

        This method returns a `.Future` that resolves (with a result
        of ``None``) when the write has been completed.

        The ``data`` argument may be of type `bytes` or `memoryview`.

        .. versionchanged:: 4.0
            Now returns a `.Future` if no callback is given.

        .. versionchanged:: 4.5
            Added support for `memoryview` arguments.

        .. versionchanged:: 6.0

           The ``callback`` argument was removed. Use the returned
           `.Future` instead.

        """
        self._check_closed()
        if data:
            if isinstance(data, memoryview):
                # Make sure that ``len(data) == data.nbytes``
                data = memoryview(data).cast("B")
            if (
```
