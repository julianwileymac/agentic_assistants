# Chunk: 4fbdb5d9a49c_3

- source: `.venv-lab/Lib/site-packages/prompt_toolkit/completion/base.py`
- lines: 222-286
- chunk: 4/6

```
tion with the
        #       commented code below for several reasons:

        #       - `generator_to_async_generator` is not perfect and hard to get
        #         right. It's a lot of complexity for little gain. The
        #         implementation needs a huge buffer for it to be efficient
        #         when there are many completions (like 50k+).
        #       - Normally, a completer is supposed to be fast, users can have
        #         "complete while typing" enabled, and want to see the
        #         completions within a second. Handling one completion at a
        #         time, and rendering once we get it here doesn't make any
        #         sense if this is quick anyway.
        #       - Completers like `FuzzyCompleter` prepare all completions
        #         anyway so that they can be sorted by accuracy before they are
        #         yielded. At the point that we start yielding completions
        #         here, we already have all completions.
        #       - The `Buffer` class has complex logic to invalidate the UI
        #         while it is consuming the completions. We don't want to
        #         invalidate the UI for every completion (if there are many),
        #         but we want to do it often enough so that completions are
        #         being displayed while they are produced.

        #       We keep the current behavior mainly for backward-compatibility.
        #       Similarly, it would be better for this function to not return
        #       an async generator, but simply be a coroutine that returns a
        #       list of `Completion` objects, containing all completions at
        #       once.

        #       Note that this argument doesn't mean we shouldn't use
        #       `ThreadedCompleter`. It still makes sense to produce
        #       completions in a background thread, because we don't want to
        #       freeze the UI while the user is typing. But sending the
        #       completions one at a time to the UI maybe isn't worth it.

        # def get_all_in_thread() -> List[Completion]:
        #   return list(self.get_completions(document, complete_event))

        # completions = await get_running_loop().run_in_executor(None, get_all_in_thread)
        # for completion in completions:
        #   yield completion

        async with aclosing(
            generator_to_async_generator(
                lambda: self.completer.get_completions(document, complete_event)
            )
        ) as async_generator:
            async for completion in async_generator:
                yield completion

    def __repr__(self) -> str:
        return f"ThreadedCompleter({self.completer!r})"


class DummyCompleter(Completer):
    """
    A completer that doesn't return any completion.
    """

    def get_completions(
        self, document: Document, complete_event: CompleteEvent
    ) -> Iterable[Completion]:
        return []

    def __repr__(self) -> str:
```
