# Chunk: a5bb5d133fdb_5

- source: `.venv-lab/Lib/site-packages/notebook/static/8378.c1a78f0d6f0124d37fa9.js.map`
- lines: 1-1
- chunk: 6/6

```
quote + '@'))) {\n    state.tokenize = tokenBase;\n  }\n  else if (quote === '\"') {\n    while (!stream.eol()) {\n      var ch = stream.peek();\n      if (ch === '$') {\n        state.tokenize = tokenHereStringInterpolation;\n        return 'string';\n      }\n\n      stream.next();\n      if (ch === '`') {\n        stream.next();\n      }\n    }\n  }\n  else {\n    stream.skipToEnd();\n  }\n\n  return 'string';\n}\n\nexport const powerShell = {\n  name: \"powershell\",\n\n  startState: function() {\n    return {\n      returnStack: [],\n      bracketNesting: 0,\n      tokenize: tokenBase\n    };\n  },\n\n  token: function(stream, state) {\n    return state.tokenize(stream, state);\n  },\n\n  languageData: {\n    commentTokens: {line: \"#\", block: {open: \"<#\", close: \"#>\"}}\n  }\n};\n"],"names":[],"sourceRoot":""}
```
