# Chunk: 7e99c46adabf_2

- source: `.venv-lab/Lib/site-packages/notebook/static/1618.da67fb30732c49b969ba.js`
- lines: 152-216
- chunk: 3/3

```
 Context(prev, align, indented) {
  this.prev = prev
  this.align = align
  this.indented = indented
}

function pushContext(state, stream) {
  var align = stream.match(/^\s*($|\/[\/\*]|[)}\]])/, false) ? null : stream.column() + 1
  state.context = new Context(state.context, align, state.indented)
}

function popContext(state) {
  if (state.context) {
    state.indented = state.context.indented
    state.context = state.context.prev
  }
}

const swift = {
  name: "swift",
  startState: function() {
    return {
      prev: null,
      context: null,
      indented: 0,
      tokenize: []
    }
  },

  token: function(stream, state) {
    var prev = state.prev
    state.prev = null
    var tokenize = state.tokenize[state.tokenize.length - 1] || tokenBase
    var style = tokenize(stream, state, prev)
    if (!style || style == "comment") state.prev = prev
    else if (!state.prev) state.prev = style

    if (style == "punctuation") {
      var bracket = /[\(\[\{]|([\]\)\}])/.exec(stream.current())
      if (bracket) (bracket[1] ? popContext : pushContext)(state, stream)
    }

    return style
  },

  indent: function(state, textAfter, iCx) {
    var cx = state.context
    if (!cx) return 0
    var closing = /^[\]\}\)]/.test(textAfter)
    if (cx.align != null) return cx.align - (closing ? 1 : 0)
    return cx.indented + (closing ? 0 : iCx.unit)
  },

  languageData: {
    indentOnInput: /^\s*[\)\}\]]$/,
    commentTokens: {line: "//", block: {open: "/*", close: "*/"}},
    closeBrackets: {brackets: ["(", "[", "{", "'", '"', "`"]}
  }
}


/***/ })

}]);
//# sourceMappingURL=1618.da67fb30732c49b969ba.js.map?v=da67fb30732c49b969ba
```
