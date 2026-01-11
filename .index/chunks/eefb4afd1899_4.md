# Chunk: eefb4afd1899_4

- source: `.venv-lab/Lib/site-packages/regex/_main.py`
- lines: 194-247
- chunk: 5/13

```
 matching, allowing other Python threads to run concurrently. If
the string changes during matching, the behaviour is undefined. This parameter
is not needed when working on the builtin (immutable) string classes.

Some of the functions in this module take flags as optional parameters. Most of
these flags can also be set within an RE:
    A   a   ASCII         Make \w, \W, \b, \B, \d, and \D match the
                          corresponding ASCII character categories. Default
                          when matching a bytestring.
    B   b   BESTMATCH     Find the best fuzzy match (default is first).
    D       DEBUG         Print the parsed pattern.
    E   e   ENHANCEMATCH  Attempt to improve the fit after finding the first
                          fuzzy match.
    F   f   FULLCASE      Use full case-folding when performing
                          case-insensitive matching in Unicode.
    I   i   IGNORECASE    Perform case-insensitive matching.
    L   L   LOCALE        Make \w, \W, \b, \B, \d, and \D dependent on the
                          current locale. (One byte per character only.)
    M   m   MULTILINE     "^" matches the beginning of lines (after a newline)
                          as well as the string. "$" matches the end of lines
                          (before a newline) as well as the end of the string.
    P   p   POSIX         Perform POSIX-standard matching (leftmost longest).
    R   r   REVERSE       Searches backwards.
    S   s   DOTALL        "." matches any character at all, including the
                          newline.
    U   u   UNICODE       Make \w, \W, \b, \B, \d, and \D dependent on the
                          Unicode locale. Default when matching a Unicode
                          string.
    V0  V0  VERSION0      Turn on the old legacy behaviour.
    V1  V1  VERSION1      Turn on the new enhanced behaviour. This flag
                          includes the FULLCASE flag.
    W   w   WORD          Make \b and \B work with default Unicode word breaks
                          and make ".", "^" and "$" work with Unicode line
                          breaks.
    X   x   VERBOSE       Ignore whitespace and comments for nicer looking REs.

This module also defines an exception 'error'.

"""

# Public symbols.
__all__ = ["cache_all", "compile", "DEFAULT_VERSION", "escape", "findall",
  "finditer", "fullmatch", "match", "purge", "search", "split", "splititer",
  "sub", "subf", "subfn", "subn", "template", "Scanner", "A", "ASCII", "B",
  "BESTMATCH", "D", "DEBUG", "E", "ENHANCEMATCH", "S", "DOTALL", "F",
  "FULLCASE", "I", "IGNORECASE", "L", "LOCALE", "M", "MULTILINE", "P", "POSIX",
  "R", "REVERSE", "T", "TEMPLATE", "U", "UNICODE", "V0", "VERSION0", "V1",
  "VERSION1", "X", "VERBOSE", "W", "WORD", "error", "Regex", "__version__",
  "__doc__", "RegexFlag"]

__version__ = "2025.11.3"

# --------------------------------------------------------------------
```
