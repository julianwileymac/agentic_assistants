# Chunk: fdcaa9edca19_4

- source: `.venv-lab/Lib/site-packages/prompt_toolkit/shortcuts/progress_bar/base.py`
- lines: 339-427
- chunk: 5/6

```
t | None

        if total is None:
            try:
                self.total = len(cast(Sized, data))
            except TypeError:
                self.total = None  # We don't know the total length.
        else:
            self.total = total

    def __iter__(self) -> Iterator[_CounterItem]:
        if self.data is not None:
            try:
                for item in self.data:
                    yield item
                    self.item_completed()

                # Only done if we iterate to the very end.
                self.done = True
            finally:
                # Ensure counter has stopped even if we did not iterate to the
                # end (e.g. break or exceptions).
                self.stopped = True
        else:
            raise NotImplementedError("No data defined to iterate over.")

    def item_completed(self) -> None:
        """
        Start handling the next item.

        (Can be called manually in case we don't have a collection to loop through.)
        """
        self.items_completed += 1
        self.progress_bar.invalidate()

    @property
    def done(self) -> bool:
        """Whether a counter has been completed.

        Done counter have been stopped (see stopped) and removed depending on
        remove_when_done value.

        Contrast this with stopped. A stopped counter may be terminated before
        100% completion. A done counter has reached its 100% completion.
        """
        return self._done

    @done.setter
    def done(self, value: bool) -> None:
        self._done = value
        self.stopped = value

        if value and self.remove_when_done:
            self.progress_bar.counters.remove(self)

    @property
    def stopped(self) -> bool:
        """Whether a counter has been stopped.

        Stopped counters no longer have increasing time_elapsed. This distinction is
        also used to prevent the Bar formatter with unknown totals from continuing to run.

        A stopped counter (but not done) can be used to signal that a given counter has
        encountered an error but allows other counters to continue
        (e.g. download X of Y failed). Given how only done counters are removed
        (see remove_when_done) this can help aggregate failures from a large number of
        successes.

        Contrast this with done. A done counter has reached its 100% completion.
        A stopped counter may be terminated before 100% completion.
        """
        return self.stop_time is not None

    @stopped.setter
    def stopped(self, value: bool) -> None:
        if value:
            # This counter has not already been stopped.
            if not self.stop_time:
                self.stop_time = datetime.datetime.now()
        else:
            # Clearing any previously set stop_time.
            self.stop_time = None

    @property
    def percentage(self) -> float:
        if self.total is None:
            return 0
        else:
```
