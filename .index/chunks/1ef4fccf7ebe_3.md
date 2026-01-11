# Chunk: 1ef4fccf7ebe_3

- source: `.venv-lab/Lib/site-packages/notebook/static/311.d6a177e2f8f1b1690911.js.map`
- lines: 1-1
- chunk: 4/4

```
\n    setState(state, normal);\n    popCommand(state);\n\n    return normal(source, state);\n  }\n\n  return {\n    name: \"stex\",\n    startState: function() {\n      var f = mathMode ? function(source, state){ return inMathMode(source, state); } : normal;\n      return {\n        cmdState: [],\n        f: f\n      };\n    },\n    copyState: function(s) {\n      return {\n        cmdState: s.cmdState.slice(),\n        f: s.f\n      };\n    },\n    token: function(stream, state) {\n      return state.f(stream, state);\n    },\n    blankLine: function(state) {\n      state.f = normal;\n      state.cmdState.length = 0;\n    },\n    languageData: {\n      commentTokens: {line: \"%\"}\n    }\n  };\n};\n\nexport const stex = mkStex(false)\nexport const stexMath = mkStex(true)\n"],"names":[],"sourceRoot":""}
```
