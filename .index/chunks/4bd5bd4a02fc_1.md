# Chunk: 4bd5bd4a02fc_1

- source: `.venv-lab/Lib/site-packages/prompt_toolkit/history.py`
- lines: 91-180
- chunk: 2/4

```
e:
            yield

    @abstractmethod
    def store_string(self, string: str) -> None:
        """
        Store the string in persistent storage.
        """


class ThreadedHistory(History):
    """
    Wrapper around `History` implementations that run the `load()` generator in
    a thread.

    Use this to increase the start-up time of prompt_toolkit applications.
    History entries are available as soon as they are loaded. We don't have to
    wait for everything to be loaded.
    """

    def __init__(self, history: History) -> None:
        super().__init__()

        self.history = history

        self._load_thread: threading.Thread | None = None

        # Lock for accessing/manipulating `_loaded_strings` and `_loaded`
        # together in a consistent state.
        self._lock = threading.Lock()

        # Events created by each `load()` call. Used to wait for new history
        # entries from the loader thread.
        self._string_load_events: list[threading.Event] = []

    async def load(self) -> AsyncGenerator[str, None]:
        """
        Like `History.load(), but call `self.load_history_strings()` in a
        background thread.
        """
        # Start the load thread, if this is called for the first time.
        if not self._load_thread:
            self._load_thread = threading.Thread(
                target=self._in_load_thread,
                daemon=True,
            )
            self._load_thread.start()

        # Consume the `_loaded_strings` list, using asyncio.
        loop = get_running_loop()

        # Create threading Event so that we can wait for new items.
        event = threading.Event()
        event.set()
        self._string_load_events.append(event)

        items_yielded = 0

        try:
            while True:
                # Wait for new items to be available.
                # (Use a timeout, because the executor thread is not a daemon
                # thread. The "slow-history.py" example would otherwise hang if
                # Control-C is pressed before the history is fully loaded,
                # because there's still this non-daemon executor thread waiting
                # for this event.)
                got_timeout = await loop.run_in_executor(
                    None, lambda: event.wait(timeout=0.5)
                )
                if not got_timeout:
                    continue

                # Read new items (in lock).
                def in_executor() -> tuple[list[str], bool]:
                    with self._lock:
                        new_items = self._loaded_strings[items_yielded:]
                        done = self._loaded
                        event.clear()
                    return new_items, done

                new_items, done = await loop.run_in_executor(None, in_executor)

                items_yielded += len(new_items)

                for item in new_items:
                    yield item

                if done:
                    break
```
