# Chunk: c9dd93bafebb_1

- source: `.venv-lab/Lib/site-packages/pygments/lexers/lilypond.py`
- lines: 77-150
- chunk: 2/4

```
ssed(text):
            if token is Token.Name.Function or token is Token.Name.Variable:
                if value in scheme_functions:
                    token = Token.Name.Builtin.SchemeFunction
            elif token is Token.Name.Builtin:
                token = Token.Name.Builtin.SchemeBuiltin
            yield index, token, value

    tokens = {
        "root": [
            # Whitespace.
            (r"\s+", Token.Text.Whitespace),

            # Multi-line comments. These are non-nestable.
            (r"%\{.*?%\}", Token.Comment.Multiline),

            # Simple comments.
            (r"%.*?$", Token.Comment.Single),

            # End of embedded LilyPond in Scheme.
            (r"#\}", Token.Punctuation, "#pop"),

            # Embedded Scheme, starting with # ("delayed"),
            # or $ (immediate). #@ and and $@ are the lesser known
            # "list splicing operators".
            (r"[#$]@?", Token.Punctuation, "value"),

            # Any kind of punctuation:
            # - sequential music: { },
            # - parallel music: << >>,
            # - voice separator: << \\ >>,
            # - chord: < >,
            # - bar check: |,
            # - dot in nested properties: \revert NoteHead.color,
            # - equals sign in assignments and lists for various commands:
            #   \override Stem.color = red,
            # - comma as alternative syntax for lists: \time 3,3,2 4/4,
            # - colon in tremolos: c:32,
            # - double hyphen and underscore in lyrics: li -- ly -- pond __
            #   (which must be preceded by ASCII whitespace)
            (r"""(?x)
               \\\\
               | (?<= \s ) (?: -- | __ )
               | [{}<>=.,:|]
              """, Token.Punctuation),

            # Pitches, with optional octavation marks, octave check,
            # and forced or cautionary accidental.
            (words(pitches, suffix=r"=?[',]*!?\??" + NAME_END_RE), Token.Pitch),

            # Strings, optionally with direction specifier.
            (r'[\-_^]?"', Token.String, "string"),

            # Numbers.
            (r"-?\d+\.\d+", Token.Number.Float), # 5. and .5 are not allowed
            (r"-?\d+/\d+", Token.Number.Fraction),
            # Integers, or durations with optional augmentation dots.
            # We have no way to distinguish these, so we highlight
            # them all as numbers.
            #
            # Normally, there is a space before the integer (being an
            # argument to a music function), which we check here.  The
            # case without a space is handled below (as a fingering
            # number).
            (r"""(?x)
               (?<= \s ) -\d+
               | (?: (?: \d+ | \\breve | \\longa | \\maxima )
                     \.* )
              """, Token.Number),
            # Separates duration and duration multiplier highlighted as fraction.
            (r"\*", Token.Number),

            # Ties, slurs, manual beams.
```
