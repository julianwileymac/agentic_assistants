# Chunk: ebc3013a5ffd_3

- source: `.venv-lab/Lib/site-packages/notebook/static/7360.b3741cc7257cecd9efe9.js.map`
- lines: 1-1
- chunk: 4/4

```
(state, stream.column(), \"]\");\n    else if (curPunc == \"(\") pushContext(state, stream.column(), \")\");\n    else if (curPunc == \"}\") {\n      while (ctx.type == \"statement\") ctx = popContext(state);\n      if (ctx.type == \"}\") ctx = popContext(state);\n      while (ctx.type == \"statement\") ctx = popContext(state);\n    }\n    else if (curPunc == ctx.type) popContext(state);\n    else if (ctx.type == \"}\" || ctx.type == \"top\" || (ctx.type == \"statement\" && curPunc == \"newstatement\"))\n      pushContext(state, stream.column(), \"statement\");\n    state.startOfLine = false;\n    state.lastToken = curPunc || style;\n    return style;\n  },\n\n  indent: function(state, textAfter, cx) {\n    if (!state.tokenize[state.tokenize.length-1].isBase) return null;\n    var firstChar = textAfter && textAfter.charAt(0), ctx = state.context;\n    if (ctx.type == \"statement\" && !expectExpression(state.lastToken, true)) ctx = ctx.prev;\n    var closing = firstChar == ctx.type;\n    if (ctx.type == \"statement\") return ctx.indented + (firstChar == \"{\" ? 0 : cx.unit);\n    else if (ctx.align) return ctx.column + (closing ? 0 : 1);\n    else return ctx.indented + (closing ? 0 : cx.unit);\n  },\n\n  languageData: {\n    indentOnInput: /^\\s*[{}]$/,\n    commentTokens: {line: \"//\", block: {open: \"/*\", close: \"*/\"}},\n    closeBrackets: {brackets: [\"(\", \"[\", \"{\", \"'\", '\"', \"'''\", '\"\"\"']}\n  }\n};\n"],"names":[],"sourceRoot":""}
```
