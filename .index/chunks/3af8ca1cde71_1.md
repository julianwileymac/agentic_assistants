# Chunk: 3af8ca1cde71_1

- source: `.venv-lab/Lib/site-packages/prompt_toolkit/input/win32_pipe.py`
- lines: 86-157
- chunk: 2/2

```
ctive in the current
        event loop.
        """
        return attach_win32_input(self, input_ready_callback)

    def detach(self) -> ContextManager[None]:
        """
        Return a context manager that makes sure that this input is not active
        in the current event loop.
        """
        return detach_win32_input(self)

    def read_keys(self) -> list[KeyPress]:
        "Read list of KeyPress."

        # Return result.
        result = self._buffer
        self._buffer = []

        # Reset event.
        if not self._closed:
            # (If closed, the event should not reset.)
            windll.kernel32.ResetEvent(self._event)

        return result

    def flush_keys(self) -> list[KeyPress]:
        """
        Flush pending keys and return them.
        (Used for flushing the 'escape' key.)
        """
        # Flush all pending keys. (This is most important to flush the vt100
        # 'Escape' key early when nothing else follows.)
        self.vt100_parser.flush()

        # Return result.
        result = self._buffer
        self._buffer = []
        return result

    def send_bytes(self, data: bytes) -> None:
        "Send bytes to the input."
        self.send_text(data.decode("utf-8", "ignore"))

    def send_text(self, text: str) -> None:
        "Send text to the input."
        if self._closed:
            raise ValueError("Attempt to write into a closed pipe.")

        # Pass it through our vt100 parser.
        self.vt100_parser.feed(text)

        # Set event.
        windll.kernel32.SetEvent(self._event)

    def raw_mode(self) -> ContextManager[None]:
        return DummyContext()

    def cooked_mode(self) -> ContextManager[None]:
        return DummyContext()

    def close(self) -> None:
        "Close write-end of the pipe."
        self._closed = True
        windll.kernel32.SetEvent(self._event)

    def typeahead_hash(self) -> str:
        """
        This needs to be unique for every `PipeInput`.
        """
        return f"pipe-input-{self._id}"
```
