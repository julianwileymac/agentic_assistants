# Chunk: fdcaa9edca19_3

- source: `.venv-lab/Lib/site-packages/prompt_toolkit/shortcuts/progress_bar/base.py`
- lines: 253-350
- chunk: 4/6

```
    label: AnyFormattedText = "",
        remove_when_done: bool = False,
        total: int | None = None,
    ) -> ProgressBarCounter[_T]:
        """
        Start a new counter.

        :param label: Title text or description for this progress. (This can be
            formatted text as well).
        :param remove_when_done: When `True`, hide this progress bar.
        :param total: Specify the maximum value if it can't be calculated by
            calling ``len``.
        """
        counter = ProgressBarCounter(
            self, data, label=label, remove_when_done=remove_when_done, total=total
        )
        self.counters.append(counter)
        return counter

    def invalidate(self) -> None:
        self.app.invalidate()


class _ProgressControl(UIControl):
    """
    User control for the progress bar.
    """

    def __init__(
        self,
        progress_bar: ProgressBar,
        formatter: Formatter,
        cancel_callback: Callable[[], None] | None,
    ) -> None:
        self.progress_bar = progress_bar
        self.formatter = formatter
        self._key_bindings = create_key_bindings(cancel_callback)

    def create_content(self, width: int, height: int) -> UIContent:
        items: list[StyleAndTextTuples] = []

        for pr in self.progress_bar.counters:
            try:
                text = self.formatter.format(self.progress_bar, pr, width)
            except BaseException:
                traceback.print_exc()
                text = "ERROR"

            items.append(to_formatted_text(text))

        def get_line(i: int) -> StyleAndTextTuples:
            return items[i]

        return UIContent(get_line=get_line, line_count=len(items), show_cursor=False)

    def is_focusable(self) -> bool:
        return True  # Make sure that the key bindings work.

    def get_key_bindings(self) -> KeyBindings:
        return self._key_bindings


_CounterItem = TypeVar("_CounterItem", covariant=True)


class ProgressBarCounter(Generic[_CounterItem]):
    """
    An individual counter (A progress bar can have multiple counters).
    """

    def __init__(
        self,
        progress_bar: ProgressBar,
        data: Iterable[_CounterItem] | None = None,
        label: AnyFormattedText = "",
        remove_when_done: bool = False,
        total: int | None = None,
    ) -> None:
        self.start_time = datetime.datetime.now()
        self.stop_time: datetime.datetime | None = None
        self.progress_bar = progress_bar
        self.data = data
        self.items_completed = 0
        self.label = label
        self.remove_when_done = remove_when_done
        self._done = False
        self.total: int | None

        if total is None:
            try:
                self.total = len(cast(Sized, data))
            except TypeError:
                self.total = None  # We don't know the total length.
        else:
            self.total = total

    def __iter__(self) -> Iterator[_CounterItem]:
```
