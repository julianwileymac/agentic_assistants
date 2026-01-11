# Chunk: 6cce2bc32c4c_0

- source: `.venv-lab/Lib/site-packages/notebook/static/4843.7eed3c5267c10f3eb786.js`
- lines: 1-55
- chunk: 1/3

```
"use strict";
(self["webpackChunk_JUPYTERLAB_CORE_OUTPUT"] = self["webpackChunk_JUPYTERLAB_CORE_OUTPUT"] || []).push([[4843],{

/***/ 64843:
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   mscgen: () => (/* binding */ mscgen),
/* harmony export */   msgenny: () => (/* binding */ msgenny),
/* harmony export */   xu: () => (/* binding */ xu)
/* harmony export */ });
function mkParser(lang) {
  return {
    name: "mscgen",
    startState: startStateFn,
    copyState: copyStateFn,
    token: produceTokenFunction(lang),
    languageData: {
      commentTokens: {line: "#", block: {open: "/*", close: "*/"}}
    }
  }
}

const mscgen = mkParser({
  "keywords" : ["msc"],
  "options" : ["hscale", "width", "arcgradient", "wordwraparcs"],
  "constants" : ["true", "false", "on", "off"],
  "attributes" : ["label", "idurl", "id", "url", "linecolor", "linecolour", "textcolor", "textcolour", "textbgcolor", "textbgcolour", "arclinecolor", "arclinecolour", "arctextcolor", "arctextcolour", "arctextbgcolor", "arctextbgcolour", "arcskip"],
  "brackets" : ["\\{", "\\}"], // [ and  ] are brackets too, but these get handled in with lists
  "arcsWords" : ["note", "abox", "rbox", "box"],
  "arcsOthers" : ["\\|\\|\\|", "\\.\\.\\.", "---", "--", "<->", "==", "<<=>>", "<=>", "\\.\\.", "<<>>", "::", "<:>", "->", "=>>", "=>", ">>", ":>", "<-", "<<=", "<=", "<<", "<:", "x-", "-x"],
  "singlecomment" : ["//", "#"],
  "operators" : ["="]
})

const msgenny = mkParser({
  "keywords" : null,
  "options" : ["hscale", "width", "arcgradient", "wordwraparcs", "wordwrapentities", "watermark"],
  "constants" : ["true", "false", "on", "off", "auto"],
  "attributes" : null,
  "brackets" : ["\\{", "\\}"],
  "arcsWords" : ["note", "abox", "rbox", "box", "alt", "else", "opt", "break", "par", "seq", "strict", "neg", "critical", "ignore", "consider", "assert", "loop", "ref", "exc"],
  "arcsOthers" : ["\\|\\|\\|", "\\.\\.\\.", "---", "--", "<->", "==", "<<=>>", "<=>", "\\.\\.", "<<>>", "::", "<:>", "->", "=>>", "=>", ">>", ":>", "<-", "<<=", "<=", "<<", "<:", "x-", "-x"],
  "singlecomment" : ["//", "#"],
  "operators" : ["="]
})

const xu = mkParser({
  "keywords" : ["msc", "xu"],
  "options" : ["hscale", "width", "arcgradient", "wordwraparcs", "wordwrapentities", "watermark"],
  "constants" : ["true", "false", "on", "off", "auto"],
  "attributes" : ["label", "idurl", "id", "url", "linecolor", "linecolour", "textcolor", "textcolour", "textbgcolor", "textbgcolour", "arclinecolor", "arclinecolour", "arctextcolor", "arctextcolour", "arctextbgcolor", "arctextbgcolour", "arcskip", "title", "deactivate", "activate", "activation"],
  "brackets" : ["\\{", "\\}"],  // [ and  ] are brackets too, but these get handled in with lists
```
