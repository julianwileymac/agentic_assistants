# Chunk: 7e99c46adabf_0

- source: `.venv-lab/Lib/site-packages/notebook/static/1618.da67fb30732c49b969ba.js`
- lines: 1-56
- chunk: 1/3

```
"use strict";
(self["webpackChunk_JUPYTERLAB_CORE_OUTPUT"] = self["webpackChunk_JUPYTERLAB_CORE_OUTPUT"] || []).push([[1618],{

/***/ 51618:
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   swift: () => (/* binding */ swift)
/* harmony export */ });
function wordSet(words) {
  var set = {}
  for (var i = 0; i < words.length; i++) set[words[i]] = true
  return set
}

var keywords = wordSet(["_","var","let","actor","class","enum","extension","import","protocol","struct","func","typealias","associatedtype",
                        "open","public","internal","fileprivate","private","deinit","init","new","override","self","subscript","super",
                        "convenience","dynamic","final","indirect","lazy","required","static","unowned","unowned(safe)","unowned(unsafe)","weak","as","is",
                        "break","case","continue","default","else","fallthrough","for","guard","if","in","repeat","switch","where","while",
                        "defer","return","inout","mutating","nonmutating","isolated","nonisolated","catch","do","rethrows","throw","throws","async","await","try","didSet","get","set","willSet",
                        "assignment","associativity","infix","left","none","operator","postfix","precedence","precedencegroup","prefix","right",
                        "Any","AnyObject","Type","dynamicType","Self","Protocol","__COLUMN__","__FILE__","__FUNCTION__","__LINE__"])
var definingKeywords = wordSet(["var","let","actor","class","enum","extension","import","protocol","struct","func","typealias","associatedtype","for"])
var atoms = wordSet(["true","false","nil","self","super","_"])
var types = wordSet(["Array","Bool","Character","Dictionary","Double","Float","Int","Int8","Int16","Int32","Int64","Never","Optional","Set","String",
                     "UInt8","UInt16","UInt32","UInt64","Void"])
var operators = "+-/*%=|&<>~^?!"
var punc = ":;,.(){}[]"
var binary = /^\-?0b[01][01_]*/
var octal = /^\-?0o[0-7][0-7_]*/
var hexadecimal = /^\-?0x[\dA-Fa-f][\dA-Fa-f_]*(?:(?:\.[\dA-Fa-f][\dA-Fa-f_]*)?[Pp]\-?\d[\d_]*)?/
var decimal = /^\-?\d[\d_]*(?:\.\d[\d_]*)?(?:[Ee]\-?\d[\d_]*)?/
var identifier = /^\$\d+|(`?)[_A-Za-z][_A-Za-z$0-9]*\1/
var property = /^\.(?:\$\d+|(`?)[_A-Za-z][_A-Za-z$0-9]*\1)/
var instruction = /^\#[A-Za-z]+/
var attribute = /^@(?:\$\d+|(`?)[_A-Za-z][_A-Za-z$0-9]*\1)/
//var regexp = /^\/(?!\s)(?:\/\/)?(?:\\.|[^\/])+\//

function tokenBase(stream, state, prev) {
  if (stream.sol()) state.indented = stream.indentation()
  if (stream.eatSpace()) return null

  var ch = stream.peek()
  if (ch == "/") {
    if (stream.match("//")) {
      stream.skipToEnd()
      return "comment"
    }
    if (stream.match("/*")) {
      state.tokenize.push(tokenComment)
      return tokenComment(stream, state)
    }
  }
  if (stream.match(instruction)) return "builtin"
```
