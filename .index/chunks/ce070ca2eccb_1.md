# Chunk: ce070ca2eccb_1

- source: `.venv-lab/Lib/site-packages/pygments/lexers/webassembly.py`
- lines: 52-117
- chunk: 2/3

```
p_i64', 'i32.trunc_f32_s', 'i32.trunc_f32_u',
    'i32.trunc_f64_s', 'i32.trunc_f64_u', 'i64.extend_i32_s',
    'i64.extend_i32_u', 'i64.trunc_f32_s', 'i64.trunc_f32_u',
    'i64.trunc_f64_s', 'i64.trunc_f64_u', 'f32.convert_i32_s',
    'f32.convert_i32_u', 'f32.convert_i64_s', 'f32.convert_i64_u',
    'f32.demote_f64', 'f64.convert_i32_s', 'f64.convert_i32_u',
    'f64.convert_i64_s', 'f64.convert_i64_u', 'f64.promote_f32',
    'i32.reinterpret_f32', 'i64.reinterpret_f64', 'f32.reinterpret_i32',
    'f64.reinterpret_i64',
)


class WatLexer(RegexLexer):
    """Lexer for the WebAssembly text format.
    """

    name = 'WebAssembly'
    url = 'https://webassembly.org/'
    aliases = ['wast', 'wat']
    filenames = ['*.wat', '*.wast']
    version_added = '2.9'

    tokens = {
        'root': [
            (words(keywords, suffix=r'(?=[^a-z_\.])'), Keyword),
            (words(builtins), Name.Builtin, 'arguments'),
            (words(['i32', 'i64', 'f32', 'f64']), Keyword.Type),
            (r'\$[A-Za-z0-9!#$%&\'*+./:<=>?@\\^_`|~-]+', Name.Variable), # yes, all of the are valid in identifiers
            (r';;.*?$', Comment.Single),
            (r'\(;', Comment.Multiline, 'nesting_comment'),
            (r'[+-]?0x[\dA-Fa-f](_?[\dA-Fa-f])*(.([\dA-Fa-f](_?[\dA-Fa-f])*)?)?([pP][+-]?[\dA-Fa-f](_?[\dA-Fa-f])*)?', Number.Float),
            (r'[+-]?\d.\d(_?\d)*[eE][+-]?\d(_?\d)*', Number.Float),
            (r'[+-]?\d.\d(_?\d)*', Number.Float),
            (r'[+-]?\d.[eE][+-]?\d(_?\d)*', Number.Float),
            (r'[+-]?(inf|nan:0x[\dA-Fa-f](_?[\dA-Fa-f])*|nan)', Number.Float),
            (r'[+-]?0x[\dA-Fa-f](_?[\dA-Fa-f])*', Number.Hex),
            (r'[+-]?\d(_?\d)*', Number.Integer),
            (r'[\(\)]', Punctuation),
            (r'"', String.Double, 'string'),
            (r'\s+', Text),
        ],
        'nesting_comment': [
            (r'\(;', Comment.Multiline, '#push'),
            (r';\)', Comment.Multiline, '#pop'),
            (r'[^;(]+', Comment.Multiline),
            (r'[;(]', Comment.Multiline),
        ],
        'string': [
            (r'\\[\dA-Fa-f][\dA-Fa-f]', String.Escape), # must have exactly two hex digits
            (r'\\t', String.Escape),
            (r'\\n', String.Escape),
            (r'\\r', String.Escape),
            (r'\\"', String.Escape),
            (r"\\'", String.Escape),
            (r'\\u\{[\dA-Fa-f](_?[\dA-Fa-f])*\}', String.Escape),
            (r'\\\\', String.Escape),
            (r'"', String.Double, '#pop'),
            (r'[^"\\]+', String.Double),
        ],
        'arguments': [
            (r'\s+', Text),
            (r'(offset)(=)(0x[\dA-Fa-f](_?[\dA-Fa-f])*)', bygroups(Keyword, Operator, Number.Hex)),
            (r'(offset)(=)(\d(_?\d)*)', bygroups(Keyword, Operator, Number.Integer)),
            (r'(align)(=)(0x[\dA-Fa-f](_?[\dA-Fa-f])*)', bygroups(Keyword, Operator, Number.Hex)),
            (r'(align)(=)(\d(_?\d)*)', bygroups(Keyword, Operator, Number.Integer)),
```
