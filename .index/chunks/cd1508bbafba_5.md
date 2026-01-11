# Chunk: cd1508bbafba_5

- source: `.venv-lab/Lib/site-packages/IPython/terminal/shortcuts/__init__.py`
- lines: 453-566
- chunk: 6/7

```
hell.autoindent:
                b.insert_text("\n" + indent)
            else:
                b.insert_text("\n")

    return newline_or_execute


def previous_history_or_previous_completion(event):
    """
    Control-P in vi edit mode on readline is history next, unlike default prompt toolkit.

    If completer is open this still select previous completion.
    """
    event.current_buffer.auto_up()


def next_history_or_next_completion(event):
    """
    Control-N in vi edit mode on readline is history previous, unlike default prompt toolkit.

    If completer is open this still select next completion.
    """
    event.current_buffer.auto_down()


def dismiss_completion(event):
    """Dismiss completion"""
    b = event.current_buffer
    if b.complete_state:
        b.cancel_completion()


def reset_buffer(event):
    """Reset buffer"""
    b = event.current_buffer
    if b.complete_state:
        b.cancel_completion()
    else:
        b.reset()


def reset_search_buffer(event):
    """Reset search buffer"""
    if event.current_buffer.document.text:
        event.current_buffer.reset()
    else:
        event.app.layout.focus(DEFAULT_BUFFER)


def suspend_to_bg(event):
    """Suspend to background"""
    event.app.suspend_to_background()


def quit(event):
    """
    Quit application with ``SIGQUIT`` if supported or ``sys.exit`` otherwise.

    On platforms that support SIGQUIT, send SIGQUIT to the current process.
    On other platforms, just exit the process with a message.
    """
    sigquit = getattr(signal, "SIGQUIT", None)
    if sigquit is not None:
        os.kill(0, signal.SIGQUIT)
    else:
        sys.exit("Quit")


def indent_buffer(event):
    """Indent buffer"""
    event.current_buffer.insert_text(" " * 4)


def newline_autoindent(event):
    """Insert a newline after the cursor indented appropriately.

    Fancier version of former ``newline_with_copy_margin`` which should
    compute the correct indentation of the inserted line. That is to say, indent
    by 4 extra space after a function definition, class definition, context
    manager... And dedent by 4 space after ``pass``, ``return``, ``raise ...``.
    """
    shell = get_ipython()
    inputsplitter = shell.input_transformer_manager
    b = event.current_buffer
    d = b.document

    if b.complete_state:
        b.cancel_completion()
    text = d.text[: d.cursor_position] + "\n"
    _, indent = inputsplitter.check_complete(text)
    b.insert_text("\n" + (" " * (indent or 0)), move_cursor=False)


def open_input_in_editor(event):
    """Open code from input in external editor"""
    event.app.current_buffer.open_in_editor()


if sys.platform == "win32":
    from IPython.core.error import TryNext
    from IPython.lib.clipboard import (
        ClipboardEmpty,
        tkinter_clipboard_get,
        win32_clipboard_get,
    )

    @undoc
    def win_paste(event):
        try:
            text = win32_clipboard_get()
        except TryNext:
            try:
```
