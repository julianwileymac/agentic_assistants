# Chunk: ec19b1bd5c6e_6

- source: `.venv-lab/Lib/site-packages/notebook/static/2913.274b19d8f201991f4a69.js`
- lines: 435-530
- chunk: 7/104

```
for the specific language governing permissions and
limitations under the License.
*/
/*
 require('foo').shim or require('foo/shim') is a function that when invoked, will call getPolyfill,
 and if the polyfill doesn’t match the built-in value, will install it into the global environment.
 */
const getPolyfill = __webpack_require__(5565);
function shim() {
    const polyfill = getPolyfill();
    if (RegExp.prototype.exec !== polyfill) {
        RegExp.prototype.exec = polyfill;
    }
}
module.exports = shim;
//# sourceMappingURL=shim.js.map

/***/ }),

/***/ 47921:
/***/ ((module, __unused_webpack_exports, __webpack_require__) => {

/**
 * The MIT License (MIT)
 * Copyright (c) 2017-present Dmitry Soshnikov <dmitry.soshnikov@gmail.com>
 */



var compatTransforms = __webpack_require__(24845);
var _transform = __webpack_require__(42113);

module.exports = {
  /**
   * Translates a regexp in new syntax to equivalent regexp in old syntax.
   *
   * @param string|RegExp|AST - regexp
   * @param Array transformsWhitelist - names of the transforms to apply
   */
  transform: function transform(regexp) {
    var transformsWhitelist = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : [];

    var transformToApply = transformsWhitelist.length > 0 ? transformsWhitelist : Object.keys(compatTransforms);

    var result = void 0;

    // Collect extra data per transform.
    var extra = {};

    transformToApply.forEach(function (transformName) {

      if (!compatTransforms.hasOwnProperty(transformName)) {
        throw new Error('Unknown compat-transform: ' + transformName + '. ' + 'Available transforms are: ' + Object.keys(compatTransforms).join(', '));
      }

      var handler = compatTransforms[transformName];

      result = _transform.transform(regexp, handler);
      regexp = result.getAST();

      // Collect `extra` transform result.
      if (typeof handler.getExtra === 'function') {
        extra[transformName] = handler.getExtra();
      }
    });

    // Set the final extras for all transforms.
    result.setExtra(extra);

    return result;
  }
};

/***/ }),

/***/ 3561:
/***/ ((module) => {

/**
 * The MIT License (MIT)
 * Copyright (c) 2017-present Dmitry Soshnikov <dmitry.soshnikov@gmail.com>
 */



/**
 * The `RegExpTree` class provides runtime support for `compat-transpiler`
 * module from `regexp-tree`.
 *
 * E.g. it tracks names of the capturing groups, in order to access the
 * names on the matched result.
 *
 * It's a thin-wrapper on top of original regexp.
 */
```
