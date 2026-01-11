# Chunk: b3cdf3ca3bb0_12

- source: `.venv-lab/Lib/site-packages/prompt_toolkit/document.py`
- lines: 957-1029
- chunk: 13/16

```
        The returned upper boundary is not included in the selection, so
        `(0, 0)` is an empty selection.  `(0, 1)`, is a one character selection.

        Returns None if the selection doesn't cover this line at all.
        """
        if self.selection:
            line = self.lines[row]

            row_start = self.translate_row_col_to_index(row, 0)
            row_end = self.translate_row_col_to_index(row, len(line))

            from_, to = sorted(
                [self.cursor_position, self.selection.original_cursor_position]
            )

            # Take the intersection of the current line and the selection.
            intersection_start = max(row_start, from_)
            intersection_end = min(row_end, to)

            if intersection_start <= intersection_end:
                if self.selection.type == SelectionType.LINES:
                    intersection_start = row_start
                    intersection_end = row_end

                elif self.selection.type == SelectionType.BLOCK:
                    _, col1 = self.translate_index_to_position(from_)
                    _, col2 = self.translate_index_to_position(to)
                    col1, col2 = sorted([col1, col2])

                    if col1 > len(line):
                        return None  # Block selection doesn't cross this line.

                    intersection_start = self.translate_row_col_to_index(row, col1)
                    intersection_end = self.translate_row_col_to_index(row, col2)

                _, from_column = self.translate_index_to_position(intersection_start)
                _, to_column = self.translate_index_to_position(intersection_end)

                # In Vi mode, the upper boundary is always included. For Emacs
                # mode, that's not the case.
                if vi_mode():
                    to_column += 1

                return from_column, to_column
        return None

    def cut_selection(self) -> tuple[Document, ClipboardData]:
        """
        Return a (:class:`.Document`, :class:`.ClipboardData`) tuple, where the
        document represents the new document when the selection is cut, and the
        clipboard data, represents whatever has to be put on the clipboard.
        """
        if self.selection:
            cut_parts = []
            remaining_parts = []
            new_cursor_position = self.cursor_position

            last_to = 0
            for from_, to in self.selection_ranges():
                if last_to == 0:
                    new_cursor_position = from_

                remaining_parts.append(self.text[last_to:from_])
                cut_parts.append(self.text[from_:to])
                last_to = to

            remaining_parts.append(self.text[last_to:])

            cut_text = "\n".join(cut_parts)
            remaining_text = "".join(remaining_parts)

            # In case of a LINES selection, don't include the trailing newline.
```
