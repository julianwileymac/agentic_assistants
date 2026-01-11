# Chunk: 56ac2eed69ab_1

- source: `.venv-lab/Lib/site-packages/notebook/static/3211.2e93fd406e5c4e53774f.js`
- lines: 72-222
- chunk: 2/3

```
}, {
      token: 'variableName.standard',
      regex: '(?:t(?:hat|il|o)|f(?:rom|allthrough)|it|by|e)' + keywordend
    }, {
      token: 'variableName',
      regex: identifier + '\\s*:(?![:=])'
    }, {
      token: 'variableName',
      regex: identifier
    }, {
      token: 'operatorKeyword',
      regex: '(?:\\.{3}|\\s+\\?)'
    }, {
      token: 'keyword',
      regex: '(?:@+|::|\\.\\.)',
      next: 'key'
    }, {
      token: 'operatorKeyword',
      regex: '\\.\\s*',
      next: 'key'
    }, {
      token: 'string',
      regex: '\\\\\\S[^\\s,;)}\\]]*'
    }, {
      token: 'docString',
      regex: '\'\'\'',
      next: 'qdoc'
    }, {
      token: 'docString',
      regex: '"""',
      next: 'qqdoc'
    }, {
      token: 'string',
      regex: '\'',
      next: 'qstring'
    }, {
      token: 'string',
      regex: '"',
      next: 'qqstring'
    }, {
      token: 'string',
      regex: '`',
      next: 'js'
    }, {
      token: 'string',
      regex: '<\\[',
      next: 'words'
    }, {
      token: 'regexp',
      regex: '//',
      next: 'heregex'
    }, {
      token: 'regexp',
      regex: '\\/(?:[^[\\/\\n\\\\]*(?:(?:\\\\.|\\[[^\\]\\n\\\\]*(?:\\\\.[^\\]\\n\\\\]*)*\\])[^[\\/\\n\\\\]*)*)\\/[gimy$]{0,4}',
      next: 'key'
    }, {
      token: 'number',
      regex: '(?:0x[\\da-fA-F][\\da-fA-F_]*|(?:[2-9]|[12]\\d|3[0-6])r[\\da-zA-Z][\\da-zA-Z_]*|(?:\\d[\\d_]*(?:\\.\\d[\\d_]*)?|\\.\\d[\\d_]*)(?:e[+-]?\\d[\\d_]*)?[\\w$]*)'
    }, {
      token: 'paren',
      regex: '[({[]'
    }, {
      token: 'paren',
      regex: '[)}\\]]',
      next: 'key'
    }, {
      token: 'operatorKeyword',
      regex: '\\S+'
    }, {
      token: 'content',
      regex: '\\s+'
    }
  ],
  heregex: [
    {
      token: 'regexp',
      regex: '.*?//[gimy$?]{0,4}',
      next: 'start'
    }, {
      token: 'regexp',
      regex: '\\s*#{'
    }, {
      token: 'comment',
      regex: '\\s+(?:#.*)?'
    }, {
      token: 'regexp',
      regex: '\\S+'
    }
  ],
  key: [
    {
      token: 'operatorKeyword',
      regex: '[.?@!]+'
    }, {
      token: 'variableName',
      regex: identifier,
      next: 'start'
    }, {
      token: 'content',
      regex: '',
      next: 'start'
    }
  ],
  comment: [
    {
      token: 'docComment',
      regex: '.*?\\*/',
      next: 'start'
    }, {
      token: 'docComment',
      regex: '.+'
    }
  ],
  qdoc: [
    {
      token: 'string',
      regex: ".*?'''",
      next: 'key'
    }, stringfill
  ],
  qqdoc: [
    {
      token: 'string',
      regex: '.*?"""',
      next: 'key'
    }, stringfill
  ],
  qstring: [
    {
      token: 'string',
      regex: '[^\\\\\']*(?:\\\\.[^\\\\\']*)*\'',
      next: 'key'
    }, stringfill
  ],
  qqstring: [
    {
      token: 'string',
      regex: '[^\\\\"]*(?:\\\\.[^\\\\"]*)*"',
      next: 'key'
    }, stringfill
  ],
  js: [
    {
      token: 'string',
      regex: '[^\\\\`]*(?:\\\\.[^\\\\`]*)*`',
      next: 'key'
    }, stringfill
  ],
  words: [
    {
```
