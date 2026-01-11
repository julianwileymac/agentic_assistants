# Chunk: fdcaa9edca19_1

- source: `.venv-lab/Lib/site-packages/prompt_toolkit/shortcuts/progress_bar/base.py`
- lines: 107-184
- chunk: 2/6

```
ce.
    :param cancel_callback: Callback function that's called when control-c is
        pressed by the user. This can be used for instance to start "proper"
        cancellation if the wrapped code supports it.
    :param file: The file object used for rendering, by default `sys.stderr` is used.

    :param color_depth: `prompt_toolkit` `ColorDepth` instance.
    :param output: :class:`~prompt_toolkit.output.Output` instance.
    :param input: :class:`~prompt_toolkit.input.Input` instance.
    """

    def __init__(
        self,
        title: AnyFormattedText = None,
        formatters: Sequence[Formatter] | None = None,
        bottom_toolbar: AnyFormattedText = None,
        style: BaseStyle | None = None,
        key_bindings: KeyBindings | None = None,
        cancel_callback: Callable[[], None] | None = None,
        file: TextIO | None = None,
        color_depth: ColorDepth | None = None,
        output: Output | None = None,
        input: Input | None = None,
    ) -> None:
        self.title = title
        self.formatters = formatters or create_default_formatters()
        self.bottom_toolbar = bottom_toolbar
        self.counters: list[ProgressBarCounter[object]] = []
        self.style = style
        self.key_bindings = key_bindings
        self.cancel_callback = cancel_callback

        # If no `cancel_callback` was given, and we're creating the progress
        # bar from the main thread. Cancel by sending a `KeyboardInterrupt` to
        # the main thread.
        if self.cancel_callback is None and in_main_thread():

            def keyboard_interrupt_to_main_thread() -> None:
                os.kill(os.getpid(), signal.SIGINT)

            self.cancel_callback = keyboard_interrupt_to_main_thread

        # Note that we use __stderr__ as default error output, because that
        # works best with `patch_stdout`.
        self.color_depth = color_depth
        self.output = output or get_app_session().output
        self.input = input or get_app_session().input

        self._thread: threading.Thread | None = None

        self._has_sigwinch = False
        self._app_started = threading.Event()

    def __enter__(self) -> ProgressBar:
        # Create UI Application.
        title_toolbar = ConditionalContainer(
            Window(
                FormattedTextControl(lambda: self.title),
                height=1,
                style="class:progressbar,title",
            ),
            filter=Condition(lambda: self.title is not None),
        )

        bottom_toolbar = ConditionalContainer(
            Window(
                FormattedTextControl(
                    lambda: self.bottom_toolbar, style="class:bottom-toolbar.text"
                ),
                style="class:bottom-toolbar",
                height=1,
            ),
            filter=~is_done
            & renderer_height_is_known
            & Condition(lambda: self.bottom_toolbar is not None),
        )
```
