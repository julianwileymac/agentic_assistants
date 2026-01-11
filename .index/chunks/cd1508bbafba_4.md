# Chunk: cd1508bbafba_4

- source: `.venv-lab/Lib/site-packages/IPython/terminal/shortcuts/__init__.py`
- lines: 371-465
- chunk: 5/7

```
.write(cursor)
        sys.stdout.flush()

        self._input_mode = mode

    if shell.editing_mode == "vi" and shell.modal_cursor:
        ViState._input_mode = InputMode.INSERT  # type: ignore
        ViState.input_mode = property(get_input_mode, set_input_mode)  # type: ignore

    return kb


def reformat_and_execute(event):
    """Reformat code and execute it"""
    shell = get_ipython()
    reformat_text_before_cursor(
        event.current_buffer, event.current_buffer.document, shell
    )
    event.current_buffer.validate_and_handle()


def reformat_text_before_cursor(buffer, document, shell):
    text = buffer.delete_before_cursor(len(document.text[: document.cursor_position]))
    try:
        formatted_text = shell.reformat_handler(text)
        buffer.insert_text(formatted_text)
    except Exception as e:
        buffer.insert_text(text)


def handle_return_or_newline_or_execute(event):
    shell = get_ipython()
    if getattr(shell, "handle_return", None):
        return shell.handle_return(shell)(event)
    else:
        return newline_or_execute_outer(shell)(event)


def newline_or_execute_outer(shell):
    def newline_or_execute(event):
        """When the user presses return, insert a newline or execute the code."""
        b = event.current_buffer
        d = b.document

        if b.complete_state:
            cc = b.complete_state.current_completion
            if cc:
                b.apply_completion(cc)
            else:
                b.cancel_completion()
            return

        # If there's only one line, treat it as if the cursor is at the end.
        # See https://github.com/ipython/ipython/issues/10425
        if d.line_count == 1:
            check_text = d.text
        else:
            check_text = d.text[: d.cursor_position]
        status, indent = shell.check_complete(check_text)

        # if all we have after the cursor is whitespace: reformat current text
        # before cursor
        after_cursor = d.text[d.cursor_position :]
        reformatted = False
        if not after_cursor.strip():
            reformat_text_before_cursor(b, d, shell)
            reformatted = True
        if not (
            d.on_last_line
            or d.cursor_position_row >= d.line_count - d.empty_line_count_at_the_end()
        ):
            if shell.autoindent:
                b.insert_text("\n" + indent)
            else:
                b.insert_text("\n")
            return

        if (status != "incomplete") and b.accept_handler:
            if not reformatted:
                reformat_text_before_cursor(b, d, shell)
            b.validate_and_handle()
        else:
            if shell.autoindent:
                b.insert_text("\n" + indent)
            else:
                b.insert_text("\n")

    return newline_or_execute


def previous_history_or_previous_completion(event):
    """
    Control-P in vi edit mode on readline is history next, unlike default prompt toolkit.
```
