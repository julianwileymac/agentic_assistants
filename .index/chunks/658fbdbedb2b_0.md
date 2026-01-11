# Chunk: 658fbdbedb2b_0

- source: `.venv-lab/Lib/site-packages/pygments/lexers/rust.py`
- lines: 1-81
- chunk: 1/3

```
"""
    pygments.lexers.rust
    ~~~~~~~~~~~~~~~~~~~~

    Lexers for the Rust language.

    :copyright: Copyright 2006-2025 by the Pygments team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

from pygments.lexer import RegexLexer, include, bygroups, words, default
from pygments.token import Text, Comment, Operator, Keyword, Name, String, \
    Number, Punctuation, Whitespace

__all__ = ['RustLexer']


class RustLexer(RegexLexer):
    """
    Lexer for the Rust programming language (version 1.47).
    """
    name = 'Rust'
    url = 'https://www.rust-lang.org/'
    filenames = ['*.rs', '*.rs.in']
    aliases = ['rust', 'rs']
    mimetypes = ['text/rust', 'text/x-rust']
    version_added = '1.6'

    keyword_types = (words((
        'u8', 'u16', 'u32', 'u64', 'u128', 'i8', 'i16', 'i32', 'i64', 'i128',
        'usize', 'isize', 'f32', 'f64', 'char', 'str', 'bool',
    ), suffix=r'\b'), Keyword.Type)

    builtin_funcs_types = (words((
        'Copy', 'Send', 'Sized', 'Sync', 'Unpin',
        'Drop', 'Fn', 'FnMut', 'FnOnce', 'drop',
        'Box', 'ToOwned', 'Clone',
        'PartialEq', 'PartialOrd', 'Eq', 'Ord',
        'AsRef', 'AsMut', 'Into', 'From', 'Default',
        'Iterator', 'Extend', 'IntoIterator', 'DoubleEndedIterator',
        'ExactSizeIterator',
        'Option', 'Some', 'None',
        'Result', 'Ok', 'Err',
        'String', 'ToString', 'Vec',
    ), suffix=r'\b'), Name.Builtin)

    builtin_macros = (words((
        'asm', 'assert', 'assert_eq', 'assert_ne', 'cfg', 'column',
        'compile_error', 'concat', 'concat_idents', 'dbg', 'debug_assert',
        'debug_assert_eq', 'debug_assert_ne', 'env', 'eprint', 'eprintln',
        'file', 'format', 'format_args', 'format_args_nl', 'global_asm',
        'include', 'include_bytes', 'include_str',
        'is_aarch64_feature_detected',
        'is_arm_feature_detected',
        'is_mips64_feature_detected',
        'is_mips_feature_detected',
        'is_powerpc64_feature_detected',
        'is_powerpc_feature_detected',
        'is_x86_feature_detected',
        'line', 'llvm_asm', 'log_syntax', 'macro_rules', 'matches',
        'module_path', 'option_env', 'panic', 'print', 'println', 'stringify',
        'thread_local', 'todo', 'trace_macros', 'unimplemented', 'unreachable',
        'vec', 'write', 'writeln',
    ), suffix=r'!'), Name.Function.Magic)

    tokens = {
        'root': [
            # rust allows a file to start with a shebang, but if the first line
            # starts with #![ then it's not a shebang but a crate attribute.
            (r'#![^[\r\n].*$', Comment.Preproc),
            default('base'),
        ],
        'base': [
            # Whitespace and Comments
            (r'\n', Whitespace),
            (r'\s+', Whitespace),
            (r'//!.*?\n', String.Doc),
            (r'///(\n|[^/].*?\n)', String.Doc),
            (r'//(.*?)\n', Comment.Single),
            (r'/\*\*(\n|[^/*])', String.Doc, 'doccomment'),
```
