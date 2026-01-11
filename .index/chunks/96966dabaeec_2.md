# Chunk: 96966dabaeec_2

- source: `.venv-lab/Lib/site-packages/notebook/static/9022.16842ed509ced9c32e9c.js.map`
- lines: 1-1
- chunk: 3/3

```
|| tokenBase)(stream, state);\n    if (style == \"comment\") return style;\n    if (ctx.align == null) ctx.align = true;\n\n    if (curPunc == \"{\") pushContext(state, stream.column(), \"}\");\n    else if (curPunc == \"[\") pushContext(state, stream.column(), \"]\");\n    else if (curPunc == \"(\") pushContext(state, stream.column(), \")\");\n    else if (curPunc == \"case\") ctx.type = \"case\";\n    else if (curPunc == \"}\" && ctx.type == \"}\") popContext(state);\n    else if (curPunc == ctx.type) popContext(state);\n    state.startOfLine = false;\n    return style;\n  },\n\n  indent: function(state, textAfter, cx) {\n    if (state.tokenize != tokenBase && state.tokenize != null) return null;\n    var ctx = state.context, firstChar = textAfter && textAfter.charAt(0);\n    if (ctx.type == \"case\" && /^(?:case|default)\\b/.test(textAfter)) return ctx.indented;\n    var closing = firstChar == ctx.type;\n    if (ctx.align) return ctx.column + (closing ? 0 : 1);\n    else return ctx.indented + (closing ? 0 : cx.unit);\n  },\n\n  languageData: {\n    indentOnInput: /^\\s([{}]|case |default\\s*:)$/,\n    commentTokens: {line: \"//\", block: {open: \"/*\", close: \"*/\"}}\n  }\n};\n\n"],"names":[],"sourceRoot":""}
```
