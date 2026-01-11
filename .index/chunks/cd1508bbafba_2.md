# Chunk: cd1508bbafba_2

- source: `.venv-lab/Lib/site-packages/IPython/terminal/shortcuts/__init__.py`
- lines: 190-284
- chunk: 3/7

```
uggest.accept_or_jump_to_end,
        ["end"],
        "has_suggestion & default_buffer_focused & emacs_like_insert_mode",
    ),
    Binding(
        auto_suggest.accept_or_jump_to_end,
        ["c-e"],
        "has_suggestion & default_buffer_focused & emacs_like_insert_mode",
    ),
    Binding(
        auto_suggest.accept,
        ["c-f"],
        "has_suggestion & default_buffer_focused & emacs_like_insert_mode",
    ),
    Binding(
        auto_suggest.accept,
        ["right"],
        "has_suggestion & default_buffer_focused & emacs_like_insert_mode & is_cursor_at_the_end_of_line",
    ),
    Binding(
        auto_suggest.accept_word,
        ["escape", "f"],
        "has_suggestion & default_buffer_focused & emacs_like_insert_mode",
    ),
    Binding(
        auto_suggest.accept_token,
        ["c-right"],
        "has_suggestion & default_buffer_focused & emacs_like_insert_mode",
    ),
    Binding(
        auto_suggest.discard,
        ["escape"],
        # note this one is using `emacs_insert_mode`, not `emacs_like_insert_mode`
        # as in `vi_insert_mode` we do not want `escape` to be shadowed (ever).
        "has_suggestion & default_buffer_focused & emacs_insert_mode",
    ),
    Binding(
        auto_suggest.discard,
        ["delete"],
        "has_suggestion & default_buffer_focused & emacs_insert_mode",
    ),
    Binding(
        auto_suggest.swap_autosuggestion_up,
        ["c-up"],
        "navigable_suggestions"
        " & ~has_line_above"
        " & has_suggestion"
        " & default_buffer_focused",
    ),
    Binding(
        auto_suggest.swap_autosuggestion_down,
        ["c-down"],
        "navigable_suggestions"
        " & ~has_line_below"
        " & has_suggestion"
        " & default_buffer_focused",
    ),
    Binding(
        auto_suggest.up_and_update_hint,
        ["c-up"],
        "has_line_above & navigable_suggestions & default_buffer_focused",
    ),
    Binding(
        auto_suggest.down_and_update_hint,
        ["c-down"],
        "has_line_below & navigable_suggestions & default_buffer_focused",
    ),
    Binding(
        auto_suggest.accept_character,
        ["escape", "right"],
        "has_suggestion & default_buffer_focused & emacs_like_insert_mode",
    ),
    Binding(
        auto_suggest.accept_and_move_cursor_left,
        ["c-left"],
        "has_suggestion & default_buffer_focused & emacs_like_insert_mode",
    ),
    Binding(
        auto_suggest.accept_and_keep_cursor,
        ["escape", "down"],
        "has_suggestion & default_buffer_focused & emacs_insert_mode",
    ),
    Binding(
        auto_suggest.backspace_and_resume_hint,
        ["backspace"],
        # no `has_suggestion` here to allow resuming if no suggestion
        "default_buffer_focused & emacs_like_insert_mode",
    ),
    Binding(
        auto_suggest.resume_hinting,
        ["right"],
        "is_cursor_at_the_end_of_line"
        " & default_buffer_focused"
        " & emacs_like_insert_mode"
```
