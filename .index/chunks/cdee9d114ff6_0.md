# Chunk: cdee9d114ff6_0

- source: `.venv-lab/Lib/site-packages/notebook/static/5425.2e42adccd47405a6a6a3.js`
- lines: 1-112
- chunk: 1/3

```
"use strict";
(self["webpackChunk_JUPYTERLAB_CORE_OUTPUT"] = self["webpackChunk_JUPYTERLAB_CORE_OUTPUT"] || []).push([[5425],{

/***/ 15425:
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   tiki: () => (/* binding */ tiki)
/* harmony export */ });
function inBlock(style, terminator, returnTokenizer) {
  return function(stream, state) {
    while (!stream.eol()) {
      if (stream.match(terminator)) {
        state.tokenize = inText;
        break;
      }
      stream.next();
    }

    if (returnTokenizer) state.tokenize = returnTokenizer;

    return style;
  };
}

function inLine(style) {
  return function(stream, state) {
    while(!stream.eol()) {
      stream.next();
    }
    state.tokenize = inText;
    return style;
  };
}

function inText(stream, state) {
  function chain(parser) {
    state.tokenize = parser;
    return parser(stream, state);
  }

  var sol = stream.sol();
  var ch = stream.next();

  //non start of line
  switch (ch) { //switch is generally much faster than if, so it is used here
  case "{": //plugin
    stream.eat("/");
    stream.eatSpace();
    stream.eatWhile(/[^\s\u00a0=\"\'\/?(}]/);
    state.tokenize = inPlugin;
    return "tag";
  case "_": //bold
    if (stream.eat("_"))
      return chain(inBlock("strong", "__", inText));
    break;
  case "'": //italics
    if (stream.eat("'"))
      return chain(inBlock("em", "''", inText));
    break;
  case "(":// Wiki Link
    if (stream.eat("("))
      return chain(inBlock("link", "))", inText));
    break;
  case "[":// Weblink
    return chain(inBlock("url", "]", inText));
    break;
  case "|": //table
    if (stream.eat("|"))
      return chain(inBlock("comment", "||"));
    break;
  case "-":
    if (stream.eat("=")) {//titleBar
      return chain(inBlock("header string", "=-", inText));
    } else if (stream.eat("-")) {//deleted
      return chain(inBlock("error tw-deleted", "--", inText));
    }
    break;
  case "=": //underline
    if (stream.match("=="))
      return chain(inBlock("tw-underline", "===", inText));
    break;
  case ":":
    if (stream.eat(":"))
      return chain(inBlock("comment", "::"));
    break;
  case "^": //box
    return chain(inBlock("tw-box", "^"));
    break;
  case "~": //np
    if (stream.match("np~"))
      return chain(inBlock("meta", "~/np~"));
    break;
  }

  //start of line types
  if (sol) {
    switch (ch) {
    case "!": //header at start of line
      if (stream.match('!!!!!')) {
        return chain(inLine("header string"));
      } else if (stream.match('!!!!')) {
        return chain(inLine("header string"));
      } else if (stream.match('!!!')) {
        return chain(inLine("header string"));
      } else if (stream.match('!!')) {
        return chain(inLine("header string"));
      } else {
        return chain(inLine("header string"));
      }
```
