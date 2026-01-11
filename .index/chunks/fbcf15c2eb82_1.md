# Chunk: fbcf15c2eb82_1

- source: `.venv-lab/Lib/site-packages/prompt_toolkit/formatted_text/html.py`
- lines: 83-146
- chunk: 2/2

```
Name)
                    if fg:
                        fg_stack.append(fg)
                    if bg:
                        bg_stack.append(bg)

                    process_node(child)

                    if add_to_name_stack:
                        name_stack.pop()
                    if fg:
                        fg_stack.pop()
                    if bg:
                        bg_stack.pop()

        process_node(document)

        self.formatted_text = FormattedText(result)

    def __repr__(self) -> str:
        return f"HTML({self.value!r})"

    def __pt_formatted_text__(self) -> StyleAndTextTuples:
        return self.formatted_text

    def format(self, *args: object, **kwargs: object) -> HTML:
        """
        Like `str.format`, but make sure that the arguments are properly
        escaped.
        """
        return HTML(FORMATTER.vformat(self.value, args, kwargs))

    def __mod__(self, value: object) -> HTML:
        """
        HTML('<b>%s</b>') % value
        """
        if not isinstance(value, tuple):
            value = (value,)

        value = tuple(html_escape(i) for i in value)
        return HTML(self.value % value)


class HTMLFormatter(Formatter):
    def format_field(self, value: object, format_spec: str) -> str:
        return html_escape(format(value, format_spec))


def html_escape(text: object) -> str:
    # The string interpolation functions also take integers and other types.
    # Convert to string first.
    if not isinstance(text, str):
        text = f"{text}"

    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


FORMATTER = HTMLFormatter()
```
