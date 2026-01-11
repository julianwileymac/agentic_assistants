# Chunk: b86eb5ec4e5a_3

- source: `.venv-lab/Lib/site-packages/pygments/lexers/ruby.py`
- lines: 187-241
- chunk: 4/9

```
*)(\2)',
             intp_string_callback),
        ]

        return states

    tokens = {
        'root': [
            (r'\A#!.+?$', Comment.Hashbang),
            (r'#.*?$', Comment.Single),
            (r'=begin\s.*?\n=end.*?$', Comment.Multiline),
            # keywords
            (words((
                'BEGIN', 'END', 'alias', 'begin', 'break', 'case', 'defined?',
                'do', 'else', 'elsif', 'end', 'ensure', 'for', 'if', 'in', 'next', 'redo',
                'rescue', 'raise', 'retry', 'return', 'super', 'then', 'undef',
                'unless', 'until', 'when', 'while', 'yield'), suffix=r'\b'),
             Keyword),
            # start of function, class and module names
            (r'(module)(\s+)([a-zA-Z_]\w*'
             r'(?:::[a-zA-Z_]\w*)*)',
             bygroups(Keyword, Whitespace, Name.Namespace)),
            (r'(def)(\s+)', bygroups(Keyword, Whitespace), 'funcname'),
            (r'def(?=[*%&^`~+-/\[<>=])', Keyword, 'funcname'),
            (r'(class)(\s+)', bygroups(Keyword, Whitespace), 'classname'),
            # special methods
            (words((
                'initialize', 'new', 'loop', 'include', 'extend', 'raise', 'attr_reader',
                'attr_writer', 'attr_accessor', 'attr', 'catch', 'throw', 'private',
                'module_function', 'public', 'protected', 'true', 'false', 'nil'),
                suffix=r'\b'),
             Keyword.Pseudo),
            (r'(not|and|or)\b', Operator.Word),
            (words((
                'autoload', 'block_given', 'const_defined', 'eql', 'equal', 'frozen', 'include',
                'instance_of', 'is_a', 'iterator', 'kind_of', 'method_defined', 'nil',
                'private_method_defined', 'protected_method_defined',
                'public_method_defined', 'respond_to', 'tainted'), suffix=r'\?'),
             Name.Builtin),
            (r'(chomp|chop|exit|gsub|sub)!', Name.Builtin),
            (words((
                'Array', 'Float', 'Integer', 'String', '__id__', '__send__', 'abort',
                'ancestors', 'at_exit', 'autoload', 'binding', 'callcc', 'caller',
                'catch', 'chomp', 'chop', 'class_eval', 'class_variables',
                'clone', 'const_defined?', 'const_get', 'const_missing', 'const_set',
                'constants', 'display', 'dup', 'eval', 'exec', 'exit', 'extend', 'fail', 'fork',
                'format', 'freeze', 'getc', 'gets', 'global_variables', 'gsub',
                'hash', 'id', 'included_modules', 'inspect', 'instance_eval',
                'instance_method', 'instance_methods',
                'instance_variable_get', 'instance_variable_set', 'instance_variables',
                'lambda', 'load', 'local_variables', 'loop',
                'method', 'method_missing', 'methods', 'module_eval', 'name',
                'object_id', 'open', 'p', 'print', 'printf', 'private_class_method',
                'private_instance_methods',
```
