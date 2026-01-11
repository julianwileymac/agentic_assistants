# Chunk: 56ac2eed69ab_2

- source: `.venv-lab/Lib/site-packages/notebook/static/3211.2e93fd406e5c4e53774f.js`
- lines: 203-273
- chunk: 3/3

```
'key'
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
      token: 'string',
      regex: '.*?\\]>',
      next: 'key'
    }, stringfill
  ]
};
for (var idx in Rules) {
  var r = Rules[idx];
  if (r.splice) {
    for (var i = 0, len = r.length; i < len; ++i) {
      var rr = r[i];
      if (typeof rr.regex === 'string') {
        Rules[idx][i].regex = new RegExp('^' + rr.regex);
      }
    }
  } else if (typeof rr.regex === 'string') {
    Rules[idx].regex = new RegExp('^' + r.regex);
  }
}

const liveScript = {
  name: "livescript",
  startState: function(){
    return {
      next: 'start',
      lastToken: {style: null, indent: 0, content: ""}
    };
  },
  token: function(stream, state){
    while (stream.pos == stream.start)
      var style = tokenBase(stream, state);
    state.lastToken = {
      style: style,
      indent: stream.indentation(),
      content: stream.current()
    };
    return style.replace(/\./g, ' ');
  },
  indent: function(state){
    var indentation = state.lastToken.indent;
    if (state.lastToken.content.match(indenter)) {
      indentation += 2;
    }
    return indentation;
  }
};


/***/ })

}]);
//# sourceMappingURL=3211.2e93fd406e5c4e53774f.js.map?v=2e93fd406e5c4e53774f
```
