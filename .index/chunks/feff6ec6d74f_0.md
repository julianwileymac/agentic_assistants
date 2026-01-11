# Chunk: feff6ec6d74f_0

- source: `.venv-lab/Lib/site-packages/notebook/static/1871.c375ee093b7e51966390.js`
- lines: 1-62
- chunk: 1/78

```
(self["webpackChunk_JUPYTERLAB_CORE_OUTPUT"] = self["webpackChunk_JUPYTERLAB_CORE_OUTPUT"] || []).push([[1871,7634,9531,8701],{

/***/ 40018:
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";

// EXPORTS
__webpack_require__.d(__webpack_exports__, {
  ZP: () => (/* binding */ lib)
});

// UNUSED EXPORTS: getDefaultRegistry, withTheme

// EXTERNAL MODULE: ../node_modules/react/jsx-runtime.js
var jsx_runtime = __webpack_require__(24246);
// EXTERNAL MODULE: consume shared module (default) react@~18.2.0 (singleton) (fallback: ../node_modules/react/index.js)
var index_js_ = __webpack_require__(78156);
// EXTERNAL MODULE: consume shared module (default) @rjsf/utils@^5.13.4 (strict) (fallback: ../node_modules/@rjsf/utils/lib/index.js)
var lib_index_js_ = __webpack_require__(24885);
// EXTERNAL MODULE: ../node_modules/lodash/get.js
var get = __webpack_require__(99729);
var get_default = /*#__PURE__*/__webpack_require__.n(get);
// EXTERNAL MODULE: ../node_modules/lodash/isEmpty.js
var isEmpty = __webpack_require__(90104);
var isEmpty_default = /*#__PURE__*/__webpack_require__.n(isEmpty);
// EXTERNAL MODULE: ../node_modules/lodash/pick.js
var pick = __webpack_require__(14648);
var pick_default = /*#__PURE__*/__webpack_require__.n(pick);
// EXTERNAL MODULE: ../node_modules/lodash/toPath.js
var toPath = __webpack_require__(40110);
var toPath_default = /*#__PURE__*/__webpack_require__.n(toPath);
// EXTERNAL MODULE: ../node_modules/lodash/cloneDeep.js
var cloneDeep = __webpack_require__(30454);
var cloneDeep_default = /*#__PURE__*/__webpack_require__.n(cloneDeep);
// EXTERNAL MODULE: ../node_modules/lodash/isObject.js
var isObject = __webpack_require__(11611);
var isObject_default = /*#__PURE__*/__webpack_require__.n(isObject);
// EXTERNAL MODULE: ../node_modules/lodash/set.js
var set = __webpack_require__(47215);
var set_default = /*#__PURE__*/__webpack_require__.n(set);
;// CONCATENATED MODULE: ../node_modules/nanoid/index.browser.js
// This file replaces `index.js` in bundlers like webpack or Rollup,
// according to `browser` config in `package.json`.



let random = bytes => crypto.getRandomValues(new Uint8Array(bytes))

let customRandom = (alphabet, defaultSize, getRandom) => {
  // First, a bitmask is necessary to generate the ID. The bitmask makes bytes
  // values closer to the alphabet size. The bitmask calculates the closest
  // `2^31 - 1` number, which exceeds the alphabet size.
  // For example, the bitmask for the alphabet size 30 is 31 (00011111).
  // `Math.clz32` is not used, because it is not available in browsers.
  let mask = (2 << (Math.log(alphabet.length - 1) / Math.LN2)) - 1
  // Though, the bitmask solution is not perfect since the bytes exceeding
  // the alphabet size are refused. Therefore, to reliably generate the ID,
  // the random bytes redundancy has to be satisfied.

  // Note: every hardware random generator call is performance expensive,
```
