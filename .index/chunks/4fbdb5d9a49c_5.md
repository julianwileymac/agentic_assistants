# Chunk: 4fbdb5d9a49c_5

- source: `.venv-lab/Lib/site-packages/prompt_toolkit/completion/base.py`
- lines: 354-439
- chunk: 6/6

```
pleter(Completer):
    """
    Combine several completers into one.
    """

    def __init__(self, completers: Sequence[Completer]) -> None:
        self.completers = completers

    def get_completions(
        self, document: Document, complete_event: CompleteEvent
    ) -> Iterable[Completion]:
        # Get all completions from the other completers in a blocking way.
        for completer in self.completers:
            yield from completer.get_completions(document, complete_event)

    async def get_completions_async(
        self, document: Document, complete_event: CompleteEvent
    ) -> AsyncGenerator[Completion, None]:
        # Get all completions from the other completers in a non-blocking way.
        for completer in self.completers:
            async with aclosing(
                completer.get_completions_async(document, complete_event)
            ) as async_generator:
                async for item in async_generator:
                    yield item


def merge_completers(
    completers: Sequence[Completer], deduplicate: bool = False
) -> Completer:
    """
    Combine several completers into one.

    :param deduplicate: If `True`, wrap the result in a `DeduplicateCompleter`
        so that completions that would result in the same text will be
        deduplicated.
    """
    if deduplicate:
        from .deduplicate import DeduplicateCompleter

        return DeduplicateCompleter(_MergedCompleter(completers))

    return _MergedCompleter(completers)


def get_common_complete_suffix(
    document: Document, completions: Sequence[Completion]
) -> str:
    """
    Return the common prefix for all completions.
    """

    # Take only completions that don't change the text before the cursor.
    def doesnt_change_before_cursor(completion: Completion) -> bool:
        end = completion.text[: -completion.start_position]
        return document.text_before_cursor.endswith(end)

    completions2 = [c for c in completions if doesnt_change_before_cursor(c)]

    # When there is at least one completion that changes the text before the
    # cursor, don't return any common part.
    if len(completions2) != len(completions):
        return ""

    # Return the common prefix.
    def get_suffix(completion: Completion) -> str:
        return completion.text[-completion.start_position :]

    return _commonprefix([get_suffix(c) for c in completions2])


def _commonprefix(strings: Iterable[str]) -> str:
    # Similar to os.path.commonprefix
    if not strings:
        return ""

    else:
        s1 = min(strings)
        s2 = max(strings)

        for i, c in enumerate(s1):
            if c != s2[i]:
                return s1[:i]

        return s1
```
