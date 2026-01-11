# Chunk: fdcaa9edca19_5

- source: `.venv-lab/Lib/site-packages/prompt_toolkit/shortcuts/progress_bar/base.py`
- lines: 416-450
- chunk: 6/6

```
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
            return self.items_completed * 100 / max(self.total, 1)

    @property
    def time_elapsed(self) -> datetime.timedelta:
        """
        Return how much time has been elapsed since the start.
        """
        if self.stop_time is None:
            return datetime.datetime.now() - self.start_time
        else:
            return self.stop_time - self.start_time

    @property
    def time_left(self) -> datetime.timedelta | None:
        """
        Timedelta representing the time left.
        """
        if self.total is None or not self.percentage:
            return None
        elif self.done or self.stopped:
            return datetime.timedelta(0)
        else:
            return self.time_elapsed * (100 - self.percentage) / self.percentage
```
