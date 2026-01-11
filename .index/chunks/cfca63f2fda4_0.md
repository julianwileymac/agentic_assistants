# Chunk: cfca63f2fda4_0

- source: `.venv-lab/Lib/site-packages/notebook/static/9676.0476942dc748eb1854c5.js`
- lines: 1-74
- chunk: 1/2

```
"use strict";
(self["webpackChunk_JUPYTERLAB_CORE_OUTPUT"] = self["webpackChunk_JUPYTERLAB_CORE_OUTPUT"] || []).push([[9676],{

/***/ 39676:
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   ntriples: () => (/* binding */ ntriples)
/* harmony export */ });
var Location = {
  PRE_SUBJECT         : 0,
  WRITING_SUB_URI     : 1,
  WRITING_BNODE_URI   : 2,
  PRE_PRED            : 3,
  WRITING_PRED_URI    : 4,
  PRE_OBJ             : 5,
  WRITING_OBJ_URI     : 6,
  WRITING_OBJ_BNODE   : 7,
  WRITING_OBJ_LITERAL : 8,
  WRITING_LIT_LANG    : 9,
  WRITING_LIT_TYPE    : 10,
  POST_OBJ            : 11,
  ERROR               : 12
};
function transitState(currState, c) {
  var currLocation = currState.location;
  var ret;

  // Opening.
  if     (currLocation == Location.PRE_SUBJECT && c == '<') ret = Location.WRITING_SUB_URI;
  else if(currLocation == Location.PRE_SUBJECT && c == '_') ret = Location.WRITING_BNODE_URI;
  else if(currLocation == Location.PRE_PRED    && c == '<') ret = Location.WRITING_PRED_URI;
  else if(currLocation == Location.PRE_OBJ     && c == '<') ret = Location.WRITING_OBJ_URI;
  else if(currLocation == Location.PRE_OBJ     && c == '_') ret = Location.WRITING_OBJ_BNODE;
  else if(currLocation == Location.PRE_OBJ     && c == '"') ret = Location.WRITING_OBJ_LITERAL;

  // Closing.
  else if(currLocation == Location.WRITING_SUB_URI     && c == '>') ret = Location.PRE_PRED;
  else if(currLocation == Location.WRITING_BNODE_URI   && c == ' ') ret = Location.PRE_PRED;
  else if(currLocation == Location.WRITING_PRED_URI    && c == '>') ret = Location.PRE_OBJ;
  else if(currLocation == Location.WRITING_OBJ_URI     && c == '>') ret = Location.POST_OBJ;
  else if(currLocation == Location.WRITING_OBJ_BNODE   && c == ' ') ret = Location.POST_OBJ;
  else if(currLocation == Location.WRITING_OBJ_LITERAL && c == '"') ret = Location.POST_OBJ;
  else if(currLocation == Location.WRITING_LIT_LANG && c == ' ') ret = Location.POST_OBJ;
  else if(currLocation == Location.WRITING_LIT_TYPE && c == '>') ret = Location.POST_OBJ;

  // Closing typed and language literal.
  else if(currLocation == Location.WRITING_OBJ_LITERAL && c == '@') ret = Location.WRITING_LIT_LANG;
  else if(currLocation == Location.WRITING_OBJ_LITERAL && c == '^') ret = Location.WRITING_LIT_TYPE;

  // Spaces.
  else if( c == ' ' &&
           (
             currLocation == Location.PRE_SUBJECT ||
               currLocation == Location.PRE_PRED    ||
               currLocation == Location.PRE_OBJ     ||
               currLocation == Location.POST_OBJ
           )
         ) ret = currLocation;

  // Reset.
  else if(currLocation == Location.POST_OBJ && c == '.') ret = Location.PRE_SUBJECT;

  // Error
  else ret = Location.ERROR;

  currState.location=ret;
}

const ntriples = {
  name: "ntriples",
  startState: function() {
```
