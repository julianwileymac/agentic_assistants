# Chunk: 8d3f3ddbdf4d_1

- source: `.venv-lab/Lib/site-packages/notebook/static/4965.591924d7805c15261494.js.map`
- lines: 1-1
- chunk: 2/2

```
te.emailPermitted = true;\n      state.header = match[1];\n      return \"atom\";\n    }\n\n    state.inHeaders = false;\n    stream.skipToEnd();\n    return null;\n  }\n\n  if (state.inSeparator) {\n    if (stream.match(email)) return \"link\";\n    if (stream.match(untilEmail)) return \"atom\";\n    stream.skipToEnd();\n    return \"atom\";\n  }\n\n  if (state.inHeader) {\n    var style = styleForHeader(state.header);\n\n    if (state.emailPermitted) {\n      if (stream.match(bracketedEmail)) return style + \" link\";\n      if (stream.match(untilBracketedEmail)) return style;\n    }\n    stream.skipToEnd();\n    return style;\n  }\n\n  stream.skipToEnd();\n  return null;\n};\n\nexport const mbox = {\n  name: \"mbox\",\n  startState: function() {\n    return {\n      // Is in a mbox separator\n      inSeparator: false,\n      // Is in a mail header\n      inHeader: false,\n      // If bracketed email is permitted. Only applicable when inHeader\n      emailPermitted: false,\n      // Name of current header\n      header: null,\n      // Is in a region of mail headers\n      inHeaders: false\n    };\n  },\n  token: readToken,\n  blankLine: function(state) {\n    state.inHeaders = state.inSeparator = state.inHeader = false;\n  },\n  languageData: {\n    autocomplete: rfc2822.concat(rfc2822NoEmail)\n  }\n}\n\n"],"names":[],"sourceRoot":""}
```
