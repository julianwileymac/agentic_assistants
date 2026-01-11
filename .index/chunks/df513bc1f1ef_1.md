# Chunk: df513bc1f1ef_1

- source: `.venv-lab/Lib/site-packages/notebook/static/7811.fa11577c84ea92d4102c.js`
- lines: 102-211
- chunk: 2/21

```
ltiple sources
 * or `customizer` functions.
 *
 * @private
 * @param {Object} object The destination object.
 * @param {Object} source The source object.
 * @returns {Object} Returns `object`.
 */
function baseAssign(object, source) {
  return object && copyObject(source, keys(source), object);
}

module.exports = baseAssign;


/***/ }),

/***/ 5947:
/***/ ((module, __unused_webpack_exports, __webpack_require__) => {

var copyObject = __webpack_require__(35159),
    keysIn = __webpack_require__(53893);

/**
 * The base implementation of `_.assignIn` without support for multiple sources
 * or `customizer` functions.
 *
 * @private
 * @param {Object} object The destination object.
 * @param {Object} source The source object.
 * @returns {Object} Returns `object`.
 */
function baseAssignIn(object, source) {
  return object && copyObject(source, keysIn(source), object);
}

module.exports = baseAssignIn;


/***/ }),

/***/ 88799:
/***/ ((module, __unused_webpack_exports, __webpack_require__) => {

var defineProperty = __webpack_require__(42630);

/**
 * The base implementation of `assignValue` and `assignMergeValue` without
 * value checks.
 *
 * @private
 * @param {Object} object The object to modify.
 * @param {string} key The key of the property to assign.
 * @param {*} value The value to assign.
 */
function baseAssignValue(object, key, value) {
  if (key == '__proto__' && defineProperty) {
    defineProperty(object, key, {
      'configurable': true,
      'enumerable': true,
      'value': value,
      'writable': true
    });
  } else {
    object[key] = value;
  }
}

module.exports = baseAssignValue;


/***/ }),

/***/ 40699:
/***/ ((module, __unused_webpack_exports, __webpack_require__) => {

var Stack = __webpack_require__(23694),
    arrayEach = __webpack_require__(80594),
    assignValue = __webpack_require__(71928),
    baseAssign = __webpack_require__(41876),
    baseAssignIn = __webpack_require__(5947),
    cloneBuffer = __webpack_require__(2734),
    copyArray = __webpack_require__(37561),
    copySymbols = __webpack_require__(31102),
    copySymbolsIn = __webpack_require__(37048),
    getAllKeys = __webpack_require__(51385),
    getAllKeysIn = __webpack_require__(39759),
    getTag = __webpack_require__(3533),
    initCloneArray = __webpack_require__(86541),
    initCloneByTag = __webpack_require__(2078),
    initCloneObject = __webpack_require__(9560),
    isArray = __webpack_require__(19785),
    isBuffer = __webpack_require__(43854),
    isMap = __webpack_require__(98247),
    isObject = __webpack_require__(11611),
    isSet = __webpack_require__(47614),
    keys = __webpack_require__(50098),
    keysIn = __webpack_require__(53893);

/** Used to compose bitmasks for cloning. */
var CLONE_DEEP_FLAG = 1,
    CLONE_FLAT_FLAG = 2,
    CLONE_SYMBOLS_FLAG = 4;

/** `Object#toString` result references. */
var argsTag = '[object Arguments]',
    arrayTag = '[object Array]',
    boolTag = '[object Boolean]',
    dateTag = '[object Date]',
```
