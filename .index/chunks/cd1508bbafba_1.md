# Chunk: cd1508bbafba_1

- source: `.venv-lab/Lib/site-packages/IPython/terminal/shortcuts/__init__.py`
- lines: 93-200
- chunk: 2/7

```

        " & followed_by_closing_paren_or_end",
    ),
    Binding(
        match.single_quote,
        ["'"],
        "focused_insert"
        " & auto_match"
        " & not_inside_unclosed_string"
        " & preceded_by_paired_single_quotes"
        " & followed_by_closing_paren_or_end",
    ),
    Binding(
        match.docstring_double_quotes,
        ['"'],
        "focused_insert"
        " & auto_match"
        " & not_inside_unclosed_string"
        " & preceded_by_two_double_quotes",
    ),
    Binding(
        match.docstring_single_quotes,
        ["'"],
        "focused_insert"
        " & auto_match"
        " & not_inside_unclosed_string"
        " & preceded_by_two_single_quotes",
    ),
    Binding(
        match.skip_over,
        [")"],
        "focused_insert & auto_match & followed_by_closing_round_paren",
    ),
    Binding(
        match.skip_over,
        ["]"],
        "focused_insert & auto_match & followed_by_closing_bracket",
    ),
    Binding(
        match.skip_over,
        ["}"],
        "focused_insert & auto_match & followed_by_closing_brace",
    ),
    Binding(
        match.skip_over, ['"'], "focused_insert & auto_match & followed_by_double_quote"
    ),
    Binding(
        match.skip_over, ["'"], "focused_insert & auto_match & followed_by_single_quote"
    ),
    Binding(
        match.delete_pair,
        ["backspace"],
        "focused_insert"
        " & preceded_by_opening_round_paren"
        " & auto_match"
        " & followed_by_closing_round_paren",
    ),
    Binding(
        match.delete_pair,
        ["backspace"],
        "focused_insert"
        " & preceded_by_opening_bracket"
        " & auto_match"
        " & followed_by_closing_bracket",
    ),
    Binding(
        match.delete_pair,
        ["backspace"],
        "focused_insert"
        " & preceded_by_opening_brace"
        " & auto_match"
        " & followed_by_closing_brace",
    ),
    Binding(
        match.delete_pair,
        ["backspace"],
        "focused_insert"
        " & preceded_by_double_quote"
        " & auto_match"
        " & followed_by_double_quote",
    ),
    Binding(
        match.delete_pair,
        ["backspace"],
        "focused_insert"
        " & preceded_by_single_quote"
        " & auto_match"
        " & followed_by_single_quote",
    ),
]

AUTO_SUGGEST_BINDINGS = [
    # there are two reasons for re-defining bindings defined upstream:
    # 1) prompt-toolkit does not execute autosuggestion bindings in vi mode,
    # 2) prompt-toolkit checks if we are at the end of text, not end of line
    #    hence it does not work in multi-line mode of navigable provider
    Binding(
        auto_suggest.accept_or_jump_to_end,
        ["end"],
        "has_suggestion & default_buffer_focused & emacs_like_insert_mode",
    ),
    Binding(
        auto_suggest.accept_or_jump_to_end,
        ["c-e"],
        "has_suggestion & default_buffer_focused & emacs_like_insert_mode",
    ),
    Binding(
```
