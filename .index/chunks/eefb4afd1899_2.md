# Chunk: eefb4afd1899_2

- source: `.venv-lab/Lib/site-packages/regex/_main.py`
- lines: 97-155
- chunk: 3/13

```
ded then any type not
provided is not permitted.

A cost equation may be provided.

Examples:
    (?:fuzzy){i<=2}
    (?:fuzzy){i<=1,s<=2,d<=1,1i+1s+1d<3}

VERSION1: Set operators are supported, and a set can include nested sets. The
set operators, in order of increasing precedence, are:
    ||  Set union ("x||y" means "x or y").
    ~~  (double tilde) Symmetric set difference ("x~~y" means "x or y, but not
        both").
    &&  Set intersection ("x&&y" means "x and y").
    --  (double dash) Set difference ("x--y" means "x but not y").

Implicit union, ie, simple juxtaposition like in [ab], has the highest
precedence.

VERSION0 and VERSION1:
The special sequences consist of "\\" and a character from the list below. If
the ordinary character is not on the list, then the resulting RE will match the
second character.
    \number         Matches the contents of the group of the same number if
                    number is no more than 2 digits, otherwise the character
                    with the 3-digit octal code.
    \a              Matches the bell character.
    \A              Matches only at the start of the string.
    \b              Matches the empty string, but only at the start or end of a
                    word.
    \B              Matches the empty string, but not at the start or end of a
                    word.
    \d              Matches any decimal digit; equivalent to the set [0-9] when
                    matching a bytestring or a Unicode string with the ASCII
                    flag, or the whole range of Unicode digits when matching a
                    Unicode string.
    \D              Matches any non-digit character; equivalent to [^\d].
    \f              Matches the formfeed character.
    \g<name>        Matches the text matched by the group named name.
    \G              Matches the empty string, but only at the position where
                    the search started.
    \h              Matches horizontal whitespace.
    \K              Keeps only what follows for the entire match.
    \L<name>        Named list. The list is provided as a keyword argument.
    \m              Matches the empty string, but only at the start of a word.
    \M              Matches the empty string, but only at the end of a word.
    \n              Matches the newline character.
    \N{name}        Matches the named character.
    \p{name=value}  Matches the character if its property has the specified
                    value.
    \P{name=value}  Matches the character if its property hasn't the specified
                    value.
    \r              Matches the carriage-return character.
    \s              Matches any whitespace character; equivalent to
                    [ \t\n\r\f\v].
    \S              Matches any non-whitespace character; equivalent to [^\s].
    \t              Matches the tab character.
```
