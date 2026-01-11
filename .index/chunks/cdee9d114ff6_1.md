# Chunk: cdee9d114ff6_1

- source: `.venv-lab/Lib/site-packages/notebook/static/5425.2e42adccd47405a6a6a3.js`
- lines: 103-219
- chunk: 2/3

```
!!!!')) {
        return chain(inLine("header string"));
      } else if (stream.match('!!!')) {
        return chain(inLine("header string"));
      } else if (stream.match('!!')) {
        return chain(inLine("header string"));
      } else {
        return chain(inLine("header string"));
      }
      break;
    case "*": //unordered list line item, or <li /> at start of line
    case "#": //ordered list line item, or <li /> at start of line
    case "+": //ordered list line item, or <li /> at start of line
      return chain(inLine("tw-listitem bracket"));
      break;
    }
  }

  //stream.eatWhile(/[&{]/); was eating up plugins, turned off to act less like html and more like tiki
  return null;
}

// Return variables for tokenizers
var pluginName, type;
function inPlugin(stream, state) {
  var ch = stream.next();
  var peek = stream.peek();

  if (ch == "}") {
    state.tokenize = inText;
    //type = ch == ")" ? "endPlugin" : "selfclosePlugin"; inPlugin
    return "tag";
  } else if (ch == "(" || ch == ")") {
    return "bracket";
  } else if (ch == "=") {
    type = "equals";

    if (peek == ">") {
      stream.next();
      peek = stream.peek();
    }

    //here we detect values directly after equal character with no quotes
    if (!/[\'\"]/.test(peek)) {
      state.tokenize = inAttributeNoQuote();
    }
    //end detect values

    return "operator";
  } else if (/[\'\"]/.test(ch)) {
    state.tokenize = inAttribute(ch);
    return state.tokenize(stream, state);
  } else {
    stream.eatWhile(/[^\s\u00a0=\"\'\/?]/);
    return "keyword";
  }
}

function inAttribute(quote) {
  return function(stream, state) {
    while (!stream.eol()) {
      if (stream.next() == quote) {
        state.tokenize = inPlugin;
        break;
      }
    }
    return "string";
  };
}

function inAttributeNoQuote() {
  return function(stream, state) {
    while (!stream.eol()) {
      var ch = stream.next();
      var peek = stream.peek();
      if (ch == " " || ch == "," || /[ )}]/.test(peek)) {
        state.tokenize = inPlugin;
        break;
      }
    }
    return "string";
  };
}

var curState, setStyle;
function pass() {
  for (var i = arguments.length - 1; i >= 0; i--) curState.cc.push(arguments[i]);
}

function cont() {
  pass.apply(null, arguments);
  return true;
}

function pushContext(pluginName, startOfLine) {
  var noIndent = curState.context && curState.context.noIndent;
  curState.context = {
    prev: curState.context,
    pluginName: pluginName,
    indent: curState.indented,
    startOfLine: startOfLine,
    noIndent: noIndent
  };
}

function popContext() {
  if (curState.context) curState.context = curState.context.prev;
}

function element(type) {
  if (type == "openPlugin") {curState.pluginName = pluginName; return cont(attributes, endplugin(curState.startOfLine));}
  else if (type == "closePlugin") {
    var err = false;
    if (curState.context) {
      err = curState.context.pluginName != pluginName;
      popContext();
```
