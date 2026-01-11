# Chunk: b3cdf3ca3bb0_11

- source: `.venv-lab/Lib/site-packages/prompt_toolkit/document.py`
- lines: 886-965
- chunk: 12/16

```
re is no selection???
        """
        Return (from, to) tuple of the selection.
        start and end position are included.

        This doesn't take the selection type into account. Use
        `selection_ranges` instead.
        """
        if self.selection:
            from_, to = sorted(
                [self.cursor_position, self.selection.original_cursor_position]
            )
        else:
            from_, to = self.cursor_position, self.cursor_position

        return from_, to

    def selection_ranges(self) -> Iterable[tuple[int, int]]:
        """
        Return a list of `(from, to)` tuples for the selection or none if
        nothing was selected. The upper boundary is not included.

        This will yield several (from, to) tuples in case of a BLOCK selection.
        This will return zero ranges, like (8,8) for empty lines in a block
        selection.
        """
        if self.selection:
            from_, to = sorted(
                [self.cursor_position, self.selection.original_cursor_position]
            )

            if self.selection.type == SelectionType.BLOCK:
                from_line, from_column = self.translate_index_to_position(from_)
                to_line, to_column = self.translate_index_to_position(to)
                from_column, to_column = sorted([from_column, to_column])
                lines = self.lines

                if vi_mode():
                    to_column += 1

                for l in range(from_line, to_line + 1):
                    line_length = len(lines[l])

                    if from_column <= line_length:
                        yield (
                            self.translate_row_col_to_index(l, from_column),
                            self.translate_row_col_to_index(
                                l, min(line_length, to_column)
                            ),
                        )
            else:
                # In case of a LINES selection, go to the start/end of the lines.
                if self.selection.type == SelectionType.LINES:
                    from_ = max(0, self.text.rfind("\n", 0, from_) + 1)

                    if self.text.find("\n", to) >= 0:
                        to = self.text.find("\n", to)
                    else:
                        to = len(self.text) - 1

                # In Vi mode, the upper boundary is always included. For Emacs,
                # that's not the case.
                if vi_mode():
                    to += 1

                yield from_, to

    def selection_range_at_line(self, row: int) -> tuple[int, int] | None:
        """
        If the selection spans a portion of the given line, return a (from, to) tuple.

        The returned upper boundary is not included in the selection, so
        `(0, 0)` is an empty selection.  `(0, 1)`, is a one character selection.

        Returns None if the selection doesn't cover this line at all.
        """
        if self.selection:
            line = self.lines[row]
```
