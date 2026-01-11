# Chunk: e2edcde24cee_4

- source: `.venv-lab/Lib/site-packages/pygments/lexers/rebol.py`
- lines: 252-300
- chunk: 5/7

```
SE | re.MULTILINE

    escape_re = r'(?:\^\([0-9a-f]{1,4}\)*)'

    def word_callback(lexer, match):
        word = match.group()

        if re.match(".*:$", word):
            yield match.start(), Generic.Subheading, word
        elif re.match(r'(if|unless|either|any|all|while|until|loop|repeat|'
                      r'foreach|forall|func|function|does|has|switch|'
                      r'case|reduce|compose|get|set|print|prin|equal\?|'
                      r'not-equal\?|strict-equal\?|lesser\?|greater\?|lesser-or-equal\?|'
                      r'greater-or-equal\?|same\?|not|type\?|stats|'
                      r'bind|union|replace|charset|routine)$', word):
            yield match.start(), Name.Builtin, word
        elif re.match(r'(make|random|reflect|to|form|mold|absolute|add|divide|multiply|negate|'
                      r'power|remainder|round|subtract|even\?|odd\?|and~|complement|or~|xor~|'
                      r'append|at|back|change|clear|copy|find|head|head\?|index\?|insert|'
                      r'length\?|next|pick|poke|remove|reverse|select|sort|skip|swap|tail|tail\?|'
                      r'take|trim|create|close|delete|modify|open|open\?|query|read|rename|'
                      r'update|write)$', word):
            yield match.start(), Name.Function, word
        elif re.match(r'(yes|on|no|off|true|false|tab|cr|lf|newline|escape|slash|sp|space|null|'
                      r'none|crlf|dot|null-byte)$', word):
            yield match.start(), Name.Builtin.Pseudo, word
        elif re.match(r'(#system-global|#include|#enum|#define|#either|#if|#import|#export|'
                      r'#switch|#default|#get-definition)$', word):
            yield match.start(), Keyword.Namespace, word
        elif re.match(r'(system|halt|quit|quit-return|do|load|q|recycle|call|run|ask|parse|'
                      r'raise-error|return|exit|break|alias|push|pop|probe|\?\?|spec-of|body-of|'
                      r'quote|forever)$', word):
            yield match.start(), Name.Exception, word
        elif re.match(r'(action\?|block\?|char\?|datatype\?|file\?|function\?|get-path\?|zero\?|'
                      r'get-word\?|integer\?|issue\?|lit-path\?|lit-word\?|logic\?|native\?|'
                      r'op\?|paren\?|path\?|refinement\?|set-path\?|set-word\?|string\?|unset\?|'
                      r'any-struct\?|none\?|word\?|any-series\?)$', word):
            yield match.start(), Keyword, word
        elif re.match(r'(JNICALL|stdcall|cdecl|infix)$', word):
            yield match.start(), Keyword.Namespace, word
        elif re.match("to-.*", word):
            yield match.start(), Keyword, word
        elif re.match(r'(\+|-\*\*|-|\*\*|//|/|\*|and|or|xor|=\?|===|==|=|<>|<=|>=|'
                      r'<<<|>>>|<<|>>|<|>%)$', word):
            yield match.start(), Operator, word
        elif re.match(r".*\!$", word):
            yield match.start(), Keyword.Type, word
        elif re.match("'.*", word):
```
