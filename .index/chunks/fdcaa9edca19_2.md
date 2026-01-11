# Chunk: fdcaa9edca19_2

- source: `.venv-lab/Lib/site-packages/prompt_toolkit/shortcuts/progress_bar/base.py`
- lines: 174-262
- chunk: 3/6

```
bottom_toolbar, style="class:bottom-toolbar.text"
                ),
                style="class:bottom-toolbar",
                height=1,
            ),
            filter=~is_done
            & renderer_height_is_known
            & Condition(lambda: self.bottom_toolbar is not None),
        )

        def width_for_formatter(formatter: Formatter) -> AnyDimension:
            # Needs to be passed as callable (partial) to the 'width'
            # parameter, because we want to call it on every resize.
            return formatter.get_width(progress_bar=self)

        progress_controls = [
            Window(
                content=_ProgressControl(self, f, self.cancel_callback),
                width=functools.partial(width_for_formatter, f),
            )
            for f in self.formatters
        ]

        self.app: Application[None] = Application(
            min_redraw_interval=0.05,
            layout=Layout(
                HSplit(
                    [
                        title_toolbar,
                        VSplit(
                            progress_controls,
                            height=lambda: D(
                                preferred=len(self.counters), max=len(self.counters)
                            ),
                        ),
                        Window(),
                        bottom_toolbar,
                    ]
                )
            ),
            style=self.style,
            key_bindings=self.key_bindings,
            refresh_interval=0.3,
            color_depth=self.color_depth,
            output=self.output,
            input=self.input,
        )

        # Run application in different thread.
        def run() -> None:
            try:
                self.app.run(pre_run=self._app_started.set)
            except BaseException as e:
                traceback.print_exc()
                print(e)

        ctx: contextvars.Context = contextvars.copy_context()

        self._thread = threading.Thread(target=ctx.run, args=(run,))
        self._thread.start()

        return self

    def __exit__(self, *a: object) -> None:
        # Wait for the app to be started. Make sure we don't quit earlier,
        # otherwise `self.app.exit` won't terminate the app because
        # `self.app.future` has not yet been set.
        self._app_started.wait()

        # Quit UI application.
        if self.app.is_running and self.app.loop is not None:
            self.app.loop.call_soon_threadsafe(self.app.exit)

        if self._thread is not None:
            self._thread.join()

    def __call__(
        self,
        data: Iterable[_T] | None = None,
        label: AnyFormattedText = "",
        remove_when_done: bool = False,
        total: int | None = None,
    ) -> ProgressBarCounter[_T]:
        """
        Start a new counter.

        :param label: Title text or description for this progress. (This can be
            formatted text as well).
```
