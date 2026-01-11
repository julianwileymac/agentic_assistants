# Chunk: da3ec6f55a9c_5

- source: `.venv-lab/Lib/site-packages/notebook/static/4002.7d2089cf976c84095255.js`
- lines: 166-277
- chunk: 6/7

```
acket"];
  if (stream.eat(/^[)\]}]/)) return ["close", "bracket"];
  if (stream.eat(/^;/)) {stream.skipToEnd(); return ["space", "comment"];}
  if (stream.eat(/^[#'@^`~]/)) return [null, "meta"];

  var matches = stream.match(qualifiedSymbol);
  var symbol = matches && matches[0];

  if (!symbol) {
    // advance stream by at least one character so we don't get stuck.
    stream.next();
    stream.eatWhile(function (c) {return !is(c, delimiter);});
    return [null, "error"];
  }

  if (symbol === "comment" && state.lastToken === "(")
    return (state.tokenize = inComment)(stream, state);
  if (is(symbol, atom) || symbol.charAt(0) === ":") return ["symbol", "atom"];
  if (is(symbol, specialForm) || is(symbol, coreSymbol)) return ["symbol", "keyword"];
  if (state.lastToken === "(") return ["symbol", "builtin"]; // other operator

  return ["symbol", "variable"];
}

function inString(stream, state) {
  var escaped = false, next;

  while (next = stream.next()) {
    if (next === "\"" && !escaped) {state.tokenize = base; break;}
    escaped = !escaped && next === "\\";
  }

  return [null, "string"];
}

function inComment(stream, state) {
  var parenthesisCount = 1;
  var next;

  while (next = stream.next()) {
    if (next === ")") parenthesisCount--;
    if (next === "(") parenthesisCount++;
    if (parenthesisCount === 0) {
      stream.backUp(1);
      state.tokenize = base;
      break;
    }
  }

  return ["space", "comment"];
}

function createLookupMap(words) {
  var obj = {};

  for (var i = 0; i < words.length; ++i) obj[words[i]] = true;

  return obj;
}

function is(value, test) {
  if (test instanceof RegExp) return test.test(value);
  if (test instanceof Object) return test.propertyIsEnumerable(value);
}

const clojure = {
  name: "clojure",
  startState: function () {
    return {
      ctx: {prev: null, start: 0, indentTo: 0},
      lastToken: null,
      tokenize: base
    };
  },

  token: function (stream, state) {
    if (stream.sol() && (typeof state.ctx.indentTo !== "number"))
      state.ctx.indentTo = state.ctx.start + 1;

    var typeStylePair = state.tokenize(stream, state);
    var type = typeStylePair[0];
    var style = typeStylePair[1];
    var current = stream.current();

    if (type !== "space") {
      if (state.lastToken === "(" && state.ctx.indentTo === null) {
        if (type === "symbol" && is(current, hasBodyParameter))
          state.ctx.indentTo = state.ctx.start + stream.indentUnit;
        else state.ctx.indentTo = "next";
      } else if (state.ctx.indentTo === "next") {
        state.ctx.indentTo = stream.column();
      }

      state.lastToken = current;
    }

    if (type === "open")
      state.ctx = {prev: state.ctx, start: stream.column(), indentTo: null};
    else if (type === "close") state.ctx = state.ctx.prev || state.ctx;

    return style;
  },

  indent: function (state) {
    var i = state.ctx.indentTo;

    return (typeof i === "number") ?
      i :
      state.ctx.start + 1;
  },
```
