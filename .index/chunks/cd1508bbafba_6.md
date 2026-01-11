# Chunk: cd1508bbafba_6

- source: `.venv-lab/Lib/site-packages/IPython/terminal/shortcuts/__init__.py`
- lines: 553-639
- chunk: 7/7

```
om IPython.core.error import TryNext
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
                text = tkinter_clipboard_get()
            except (TryNext, ClipboardEmpty):
                return
        except ClipboardEmpty:
            return
        event.current_buffer.insert_text(text.replace("\t", " " * 4))

else:

    @undoc
    def win_paste(event):
        """Stub used on other platforms"""
        pass


KEY_BINDINGS = [
    Binding(
        handle_return_or_newline_or_execute,
        ["enter"],
        "default_buffer_focused & ~has_selection & insert_mode",
    ),
    Binding(
        reformat_and_execute,
        ["escape", "enter"],
        "default_buffer_focused & ~has_selection & insert_mode & ebivim",
    ),
    Binding(quit, ["c-\\"]),
    Binding(
        previous_history_or_previous_completion,
        ["c-p"],
        "vi_insert_mode & default_buffer_focused",
    ),
    Binding(
        next_history_or_next_completion,
        ["c-n"],
        "vi_insert_mode & default_buffer_focused",
    ),
    Binding(dismiss_completion, ["c-g"], "default_buffer_focused & has_completions"),
    Binding(reset_buffer, ["c-c"], "default_buffer_focused"),
    Binding(reset_search_buffer, ["c-c"], "search_buffer_focused"),
    Binding(suspend_to_bg, ["c-z"], "supports_suspend"),
    Binding(
        indent_buffer,
        ["tab"],  # Ctrl+I == Tab
        "default_buffer_focused & ~has_selection & insert_mode & cursor_in_leading_ws",
    ),
    Binding(newline_autoindent, ["c-o"], "default_buffer_focused & emacs_insert_mode"),
    Binding(open_input_in_editor, ["f2"], "default_buffer_focused"),
    *AUTO_MATCH_BINDINGS,
    *AUTO_SUGGEST_BINDINGS,
    Binding(
        display_completions_like_readline,
        ["c-i"],
        "readline_like_completions"
        " & default_buffer_focused"
        " & ~has_selection"
        " & insert_mode"
        " & ~cursor_in_leading_ws",
    ),
    Binding(win_paste, ["c-v"], "default_buffer_focused & ~vi_mode & is_windows_os"),
    *SIMPLE_CONTROL_BINDINGS,
    *ALT_AND_COMOBO_CONTROL_BINDINGS,
]

UNASSIGNED_ALLOWED_COMMANDS = [
    auto_suggest.llm_autosuggestion,
    nc.beginning_of_buffer,
    nc.end_of_buffer,
    nc.end_of_line,
    nc.forward_char,
    nc.forward_word,
    nc.unix_line_discard,
]
```
