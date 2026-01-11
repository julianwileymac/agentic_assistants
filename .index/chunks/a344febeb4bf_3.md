# Chunk: a344febeb4bf_3

- source: `.venv-lab/Lib/site-packages/notebook/static/3211.2e93fd406e5c4e53774f.js.map`
- lines: 1-1
- chunk: 4/4

```
 {style: null, indent: 0, content: \"\"}\n    };\n  },\n  token: function(stream, state){\n    while (stream.pos == stream.start)\n      var style = tokenBase(stream, state);\n    state.lastToken = {\n      style: style,\n      indent: stream.indentation(),\n      content: stream.current()\n    };\n    return style.replace(/\\./g, ' ');\n  },\n  indent: function(state){\n    var indentation = state.lastToken.indent;\n    if (state.lastToken.content.match(indenter)) {\n      indentation += 2;\n    }\n    return indentation;\n  }\n};\n"],"names":[],"sourceRoot":""}
```
