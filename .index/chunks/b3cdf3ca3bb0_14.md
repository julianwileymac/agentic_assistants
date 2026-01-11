# Chunk: b3cdf3ca3bb0_14

- source: `.venv-lab/Lib/site-packages/prompt_toolkit/document.py`
- lines: 1089-1181
- chunk: 15/16

```
 len(lines):
                    lines.append("")

                lines[index] = lines[index].ljust(start_column)
                lines[index] = (
                    lines[index][:start_column]
                    + line * count
                    + lines[index][start_column:]
                )

            new_text = "\n".join(lines)
            new_cursor_position = self.cursor_position + (0 if before else 1)

        return Document(text=new_text, cursor_position=new_cursor_position)

    def empty_line_count_at_the_end(self) -> int:
        """
        Return number of empty lines at the end of the document.
        """
        count = 0
        for line in self.lines[::-1]:
            if not line or line.isspace():
                count += 1
            else:
                break

        return count

    def start_of_paragraph(self, count: int = 1, before: bool = False) -> int:
        """
        Return the start of the current paragraph. (Relative cursor position.)
        """

        def match_func(text: str) -> bool:
            return not text or text.isspace()

        line_index = self.find_previous_matching_line(
            match_func=match_func, count=count
        )

        if line_index:
            add = 0 if before else 1
            return min(0, self.get_cursor_up_position(count=-line_index) + add)
        else:
            return -self.cursor_position

    def end_of_paragraph(self, count: int = 1, after: bool = False) -> int:
        """
        Return the end of the current paragraph. (Relative cursor position.)
        """

        def match_func(text: str) -> bool:
            return not text or text.isspace()

        line_index = self.find_next_matching_line(match_func=match_func, count=count)

        if line_index:
            add = 0 if after else 1
            return max(0, self.get_cursor_down_position(count=line_index) - add)
        else:
            return len(self.text_after_cursor)

    # Modifiers.

    def insert_after(self, text: str) -> Document:
        """
        Create a new document, with this text inserted after the buffer.
        It keeps selection ranges and cursor position in sync.
        """
        return Document(
            text=self.text + text,
            cursor_position=self.cursor_position,
            selection=self.selection,
        )

    def insert_before(self, text: str) -> Document:
        """
        Create a new document, with this text inserted before the buffer.
        It keeps selection ranges and cursor position in sync.
        """
        selection_state = self.selection

        if selection_state:
            selection_state = SelectionState(
                original_cursor_position=selection_state.original_cursor_position
                + len(text),
                type=selection_state.type,
            )

        return Document(
            text=text + self.text,
            cursor_position=self.cursor_position + len(text),
```
