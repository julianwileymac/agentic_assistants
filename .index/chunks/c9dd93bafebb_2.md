# Chunk: c9dd93bafebb_2

- source: `.venv-lab/Lib/site-packages/pygments/lexers/lilypond.py`
- lines: 142-192
- chunk: 3/4

```
   (?<= \s ) -\d+
               | (?: (?: \d+ | \\breve | \\longa | \\maxima )
                     \.* )
              """, Token.Number),
            # Separates duration and duration multiplier highlighted as fraction.
            (r"\*", Token.Number),

            # Ties, slurs, manual beams.
            (r"[~()[\]]", Token.Name.Builtin.Articulation),

            # Predefined articulation shortcuts. A direction specifier is
            # required here.
            (r"[\-_^][>^_!.\-+]", Token.Name.Builtin.Articulation),

            # Fingering numbers, string numbers.
            (r"[\-_^]?\\?\d+", Token.Name.Builtin.Articulation),

            # Builtins.
            (builtin_words(keywords, "mandatory"), Token.Keyword),
            (builtin_words(pitch_language_names, "disallowed"), Token.Name.PitchLanguage),
            (builtin_words(clefs, "disallowed"), Token.Name.Builtin.Clef),
            (builtin_words(scales, "mandatory"), Token.Name.Builtin.Scale),
            (builtin_words(repeat_types, "disallowed"), Token.Name.Builtin.RepeatType),
            (builtin_words(units, "mandatory"), Token.Number),
            (builtin_words(chord_modifiers, "disallowed"), Token.ChordModifier),
            (builtin_words(music_functions, "mandatory"), Token.Name.Builtin.MusicFunction),
            (builtin_words(dynamics, "mandatory"), Token.Name.Builtin.Dynamic),
            # Those like slurs that don't take a backslash are covered above.
            (builtin_words(articulations, "mandatory"), Token.Name.Builtin.Articulation),
            (builtin_words(music_commands, "mandatory"), Token.Name.Builtin.MusicCommand),
            (builtin_words(markup_commands, "mandatory"), Token.Name.Builtin.MarkupCommand),
            (builtin_words(grobs, "disallowed"), Token.Name.Builtin.Grob),
            (builtin_words(translators, "disallowed"), Token.Name.Builtin.Translator),
            # Optional backslash because of \layout { \context { \Score ... } }.
            (builtin_words(contexts, "optional"), Token.Name.Builtin.Context),
            (builtin_words(context_properties, "disallowed"), Token.Name.Builtin.ContextProperty),
            (builtin_words(grob_properties, "disallowed"),
             Token.Name.Builtin.GrobProperty,
             "maybe-subproperties"),
            # Optional backslashes here because output definitions are wrappers
            # around modules.  Concretely, you can do, e.g.,
            # \paper { oddHeaderMarkup = \evenHeaderMarkup }
            (builtin_words(paper_variables, "optional"), Token.Name.Builtin.PaperVariable),
            (builtin_words(header_variables, "optional"), Token.Name.Builtin.HeaderVariable),

            # Other backslashed-escaped names (like dereferencing a
            # music variable), possibly with a direction specifier.
            (r"[\-_^]?\\.+?" + NAME_END_RE, Token.Name.BackslashReference),

            # Definition of a variable. Support assignments to alist keys
```
