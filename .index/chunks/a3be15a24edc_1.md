# Chunk: a3be15a24edc_1

- source: `.venv-lab/Lib/site-packages/prompt_toolkit/output/base.py`
- lines: 107-211
- chunk: 2/3

```
@abstractmethod
    def set_attributes(self, attrs: Attrs, color_depth: ColorDepth) -> None:
        "Set new color and styling attributes."

    @abstractmethod
    def disable_autowrap(self) -> None:
        "Disable auto line wrapping."

    @abstractmethod
    def enable_autowrap(self) -> None:
        "Enable auto line wrapping."

    @abstractmethod
    def cursor_goto(self, row: int = 0, column: int = 0) -> None:
        "Move cursor position."

    @abstractmethod
    def cursor_up(self, amount: int) -> None:
        "Move cursor `amount` place up."

    @abstractmethod
    def cursor_down(self, amount: int) -> None:
        "Move cursor `amount` place down."

    @abstractmethod
    def cursor_forward(self, amount: int) -> None:
        "Move cursor `amount` place forward."

    @abstractmethod
    def cursor_backward(self, amount: int) -> None:
        "Move cursor `amount` place backward."

    @abstractmethod
    def hide_cursor(self) -> None:
        "Hide cursor."

    @abstractmethod
    def show_cursor(self) -> None:
        "Show cursor."

    @abstractmethod
    def set_cursor_shape(self, cursor_shape: CursorShape) -> None:
        "Set cursor shape to block, beam or underline."

    @abstractmethod
    def reset_cursor_shape(self) -> None:
        "Reset cursor shape."

    def ask_for_cpr(self) -> None:
        """
        Asks for a cursor position report (CPR).
        (VT100 only.)
        """

    @property
    def responds_to_cpr(self) -> bool:
        """
        `True` if the `Application` can expect to receive a CPR response after
        calling `ask_for_cpr` (this will come back through the corresponding
        `Input`).

        This is used to determine the amount of available rows we have below
        the cursor position. In the first place, we have this so that the drop
        down autocompletion menus are sized according to the available space.

        On Windows, we don't need this, there we have
        `get_rows_below_cursor_position`.
        """
        return False

    @abstractmethod
    def get_size(self) -> Size:
        "Return the size of the output window."

    def bell(self) -> None:
        "Sound bell."

    def enable_bracketed_paste(self) -> None:
        "For vt100 only."

    def disable_bracketed_paste(self) -> None:
        "For vt100 only."

    def reset_cursor_key_mode(self) -> None:
        """
        For vt100 only.
        Put the terminal in normal cursor mode (instead of application mode).

        See: https://vt100.net/docs/vt100-ug/chapter3.html
        """

    def scroll_buffer_to_prompt(self) -> None:
        "For Win32 only."

    def get_rows_below_cursor_position(self) -> int:
        "For Windows only."
        raise NotImplementedError

    @abstractmethod
    def get_default_color_depth(self) -> ColorDepth:
        """
        Get default color depth for this output.

        This value will be used if no color depth was explicitly passed to the
```
