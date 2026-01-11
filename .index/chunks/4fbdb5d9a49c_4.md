# Chunk: 4fbdb5d9a49c_4

- source: `.venv-lab/Lib/site-packages/prompt_toolkit/completion/base.py`
- lines: 272-365
- chunk: 5/6

```
eter({self.completer!r})"


class DummyCompleter(Completer):
    """
    A completer that doesn't return any completion.
    """

    def get_completions(
        self, document: Document, complete_event: CompleteEvent
    ) -> Iterable[Completion]:
        return []

    def __repr__(self) -> str:
        return "DummyCompleter()"


class DynamicCompleter(Completer):
    """
    Completer class that can dynamically returns any Completer.

    :param get_completer: Callable that returns a :class:`.Completer` instance.
    """

    def __init__(self, get_completer: Callable[[], Completer | None]) -> None:
        self.get_completer = get_completer

    def get_completions(
        self, document: Document, complete_event: CompleteEvent
    ) -> Iterable[Completion]:
        completer = self.get_completer() or DummyCompleter()
        return completer.get_completions(document, complete_event)

    async def get_completions_async(
        self, document: Document, complete_event: CompleteEvent
    ) -> AsyncGenerator[Completion, None]:
        completer = self.get_completer() or DummyCompleter()

        async for completion in completer.get_completions_async(
            document, complete_event
        ):
            yield completion

    def __repr__(self) -> str:
        return f"DynamicCompleter({self.get_completer!r} -> {self.get_completer()!r})"


class ConditionalCompleter(Completer):
    """
    Wrapper around any other completer that will enable/disable the completions
    depending on whether the received condition is satisfied.

    :param completer: :class:`.Completer` instance.
    :param filter: :class:`.Filter` instance.
    """

    def __init__(self, completer: Completer, filter: FilterOrBool) -> None:
        self.completer = completer
        self.filter = to_filter(filter)

    def __repr__(self) -> str:
        return f"ConditionalCompleter({self.completer!r}, filter={self.filter!r})"

    def get_completions(
        self, document: Document, complete_event: CompleteEvent
    ) -> Iterable[Completion]:
        # Get all completions in a blocking way.
        if self.filter():
            yield from self.completer.get_completions(document, complete_event)

    async def get_completions_async(
        self, document: Document, complete_event: CompleteEvent
    ) -> AsyncGenerator[Completion, None]:
        # Get all completions in a non-blocking way.
        if self.filter():
            async with aclosing(
                self.completer.get_completions_async(document, complete_event)
            ) as async_generator:
                async for item in async_generator:
                    yield item


class _MergedCompleter(Completer):
    """
    Combine several completers into one.
    """

    def __init__(self, completers: Sequence[Completer]) -> None:
        self.completers = completers

    def get_completions(
        self, document: Document, complete_event: CompleteEvent
    ) -> Iterable[Completion]:
```
