# Chunk: 00eec93c2cfa_6

- source: `.venv-lab/Lib/site-packages/pip/_vendor/rich/text.py`
- lines: 481-562
- chunk: 7/18

```
end), style))

    def stylize_before(
        self,
        style: Union[str, Style],
        start: int = 0,
        end: Optional[int] = None,
    ) -> None:
        """Apply a style to the text, or a portion of the text. Styles will be applied before other styles already present.

        Args:
            style (Union[str, Style]): Style instance or style definition to apply.
            start (int): Start offset (negative indexing is supported). Defaults to 0.
            end (Optional[int], optional): End offset (negative indexing is supported), or None for end of text. Defaults to None.
        """
        if style:
            length = len(self)
            if start < 0:
                start = length + start
            if end is None:
                end = length
            if end < 0:
                end = length + end
            if start >= length or end <= start:
                # Span not in text or not valid
                return
            self._spans.insert(0, Span(start, min(length, end), style))

    def apply_meta(
        self, meta: Dict[str, Any], start: int = 0, end: Optional[int] = None
    ) -> None:
        """Apply metadata to the text, or a portion of the text.

        Args:
            meta (Dict[str, Any]): A dict of meta information.
            start (int): Start offset (negative indexing is supported). Defaults to 0.
            end (Optional[int], optional): End offset (negative indexing is supported), or None for end of text. Defaults to None.

        """
        style = Style.from_meta(meta)
        self.stylize(style, start=start, end=end)

    def on(self, meta: Optional[Dict[str, Any]] = None, **handlers: Any) -> "Text":
        """Apply event handlers (used by Textual project).

        Example:
            >>> from rich.text import Text
            >>> text = Text("hello world")
            >>> text.on(click="view.toggle('world')")

        Args:
            meta (Dict[str, Any]): Mapping of meta information.
            **handlers: Keyword args are prefixed with "@" to defined handlers.

        Returns:
            Text: Self is returned to method may be chained.
        """
        meta = {} if meta is None else meta
        meta.update({f"@{key}": value for key, value in handlers.items()})
        self.stylize(Style.from_meta(meta))
        return self

    def remove_suffix(self, suffix: str) -> None:
        """Remove a suffix if it exists.

        Args:
            suffix (str): Suffix to remove.
        """
        if self.plain.endswith(suffix):
            self.right_crop(len(suffix))

    def get_style_at_offset(self, console: "Console", offset: int) -> Style:
        """Get the style of a character at give offset.

        Args:
            console (~Console): Console where text will be rendered.
            offset (int): Offset in to text (negative indexing supported)

        Returns:
            Style: A Style instance.
        """
```
