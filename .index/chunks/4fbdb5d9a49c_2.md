# Chunk: 4fbdb5d9a49c_2

- source: `.venv-lab/Lib/site-packages/prompt_toolkit/completion/base.py`
- lines: 153-228
- chunk: 3/6

```
ta):
    """
    Base class for completer implementations.
    """

    @abstractmethod
    def get_completions(
        self, document: Document, complete_event: CompleteEvent
    ) -> Iterable[Completion]:
        """
        This should be a generator that yields :class:`.Completion` instances.

        If the generation of completions is something expensive (that takes a
        lot of time), consider wrapping this `Completer` class in a
        `ThreadedCompleter`. In that case, the completer algorithm runs in a
        background thread and completions will be displayed as soon as they
        arrive.

        :param document: :class:`~prompt_toolkit.document.Document` instance.
        :param complete_event: :class:`.CompleteEvent` instance.
        """
        while False:
            yield

    async def get_completions_async(
        self, document: Document, complete_event: CompleteEvent
    ) -> AsyncGenerator[Completion, None]:
        """
        Asynchronous generator for completions. (Probably, you won't have to
        override this.)

        Asynchronous generator of :class:`.Completion` objects.
        """
        for item in self.get_completions(document, complete_event):
            yield item


class ThreadedCompleter(Completer):
    """
    Wrapper that runs the `get_completions` generator in a thread.

    (Use this to prevent the user interface from becoming unresponsive if the
    generation of completions takes too much time.)

    The completions will be displayed as soon as they are produced. The user
    can already select a completion, even if not all completions are displayed.
    """

    def __init__(self, completer: Completer) -> None:
        self.completer = completer

    def get_completions(
        self, document: Document, complete_event: CompleteEvent
    ) -> Iterable[Completion]:
        return self.completer.get_completions(document, complete_event)

    async def get_completions_async(
        self, document: Document, complete_event: CompleteEvent
    ) -> AsyncGenerator[Completion, None]:
        """
        Asynchronous generator of completions.
        """
        # NOTE: Right now, we are consuming the `get_completions` generator in
        #       a synchronous background thread, then passing the results one
        #       at a time over a queue, and consuming this queue in the main
        #       thread (that's what `generator_to_async_generator` does). That
        #       means that if the completer is *very* slow, we'll be showing
        #       completions in the UI once they are computed.

        #       It's very tempting to replace this implementation with the
        #       commented code below for several reasons:

        #       - `generator_to_async_generator` is not perfect and hard to get
        #         right. It's a lot of complexity for little gain. The
        #         implementation needs a huge buffer for it to be efficient
```
