# Chunk: b3cdf3ca3bb0_13

- source: `.venv-lab/Lib/site-packages/prompt_toolkit/document.py`
- lines: 1020-1099
- chunk: 14/16

```
parts.append(self.text[from_:to])
                last_to = to

            remaining_parts.append(self.text[last_to:])

            cut_text = "\n".join(cut_parts)
            remaining_text = "".join(remaining_parts)

            # In case of a LINES selection, don't include the trailing newline.
            if self.selection.type == SelectionType.LINES and cut_text.endswith("\n"):
                cut_text = cut_text[:-1]

            return (
                Document(text=remaining_text, cursor_position=new_cursor_position),
                ClipboardData(cut_text, self.selection.type),
            )
        else:
            return self, ClipboardData("")

    def paste_clipboard_data(
        self,
        data: ClipboardData,
        paste_mode: PasteMode = PasteMode.EMACS,
        count: int = 1,
    ) -> Document:
        """
        Return a new :class:`.Document` instance which contains the result if
        we would paste this data at the current cursor position.

        :param paste_mode: Where to paste. (Before/after/emacs.)
        :param count: When >1, Paste multiple times.
        """
        before = paste_mode == PasteMode.VI_BEFORE
        after = paste_mode == PasteMode.VI_AFTER

        if data.type == SelectionType.CHARACTERS:
            if after:
                new_text = (
                    self.text[: self.cursor_position + 1]
                    + data.text * count
                    + self.text[self.cursor_position + 1 :]
                )
            else:
                new_text = (
                    self.text_before_cursor + data.text * count + self.text_after_cursor
                )

            new_cursor_position = self.cursor_position + len(data.text) * count
            if before:
                new_cursor_position -= 1

        elif data.type == SelectionType.LINES:
            l = self.cursor_position_row
            if before:
                lines = self.lines[:l] + [data.text] * count + self.lines[l:]
                new_text = "\n".join(lines)
                new_cursor_position = len("".join(self.lines[:l])) + l
            else:
                lines = self.lines[: l + 1] + [data.text] * count + self.lines[l + 1 :]
                new_cursor_position = len("".join(self.lines[: l + 1])) + l + 1
                new_text = "\n".join(lines)

        elif data.type == SelectionType.BLOCK:
            lines = self.lines[:]
            start_line = self.cursor_position_row
            start_column = self.cursor_position_col + (0 if before else 1)

            for i, line in enumerate(data.text.split("\n")):
                index = i + start_line
                if index >= len(lines):
                    lines.append("")

                lines[index] = lines[index].ljust(start_column)
                lines[index] = (
                    lines[index][:start_column]
                    + line * count
                    + lines[index][start_column:]
                )
```
