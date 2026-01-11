# Chunk: feff6ec6d74f_73

- source: `.venv-lab/Lib/site-packages/notebook/static/1871.c375ee093b7e51966390.js`
- lines: 3641-3742
- chunk: 74/78

```
 {
    var instance = new typestyle_1.TypeStyle({ autoGenerateTag: false });
    if (target) {
        instance.setStylesTarget(target);
    }
    return instance;
}
__webpack_unused_export__ = createTypeStyle;


/***/ }),

/***/ 62034:
/***/ ((__unused_webpack_module, exports) => {

"use strict";

Object.defineProperty(exports, "__esModule", ({ value: true }));
/**
 * We need to do the following to *our* objects before passing to freestyle:
 * - For any `$nest` directive move up to FreeStyle style nesting
 * - For any `$unique` directive map to FreeStyle Unique
 * - For any `$debugName` directive return the debug name
 */
function convertToStyles(object) {
    /** The final result we will return */
    var styles = {};
    for (var key in object) {
        /** Grab the value upfront */
        var val = object[key];
        /** TypeStyle configuration options */
        if (key === '$nest') {
            var nested = val;
            for (var selector in nested) {
                var subproperties = nested[selector];
                styles[selector] = convertToStyles(subproperties);
            }
        }
        else if (key === '$debugName') {
            styles.$displayName = val;
        }
        else {
            styles[key] = val;
        }
    }
    return styles;
}
exports.convertToStyles = convertToStyles;
// todo: better name here
function convertToKeyframes(frames) {
    var result = {};
    for (var offset in frames) {
        if (offset !== '$debugName') {
            result[offset] = frames[offset];
        }
    }
    if (frames.$debugName) {
        result.$displayName = frames.$debugName;
    }
    return result;
}
exports.convertToKeyframes = convertToKeyframes;


/***/ }),

/***/ 53861:
/***/ ((__unused_webpack_module, exports, __webpack_require__) => {

"use strict";

Object.defineProperty(exports, "__esModule", ({ value: true }));
var FreeStyle = __webpack_require__(8843);
var formatting_1 = __webpack_require__(62034);
var utilities_1 = __webpack_require__(51833);
/**
 * Creates an instance of free style with our options
 */
var createFreeStyle = function () { return FreeStyle.create(); };
/**
 * Maintains a single stylesheet and keeps it in sync with requested styles
 */
var TypeStyle = /** @class */ (function () {
    function TypeStyle(_a) {
        var _this = this;
        var autoGenerateTag = _a.autoGenerateTag;
        /**
         * Insert `raw` CSS as a string. This is useful for e.g.
         * - third party CSS that you are customizing with template strings
         * - generating raw CSS in JavaScript
         * - reset libraries like normalize.css that you can use without loaders
         */
        this.cssRaw = function (mustBeValidCSS) {
            if (!mustBeValidCSS) {
                return;
            }
            _this._raw += mustBeValidCSS || '';
            _this._pendingRawChange = true;
            _this._styleUpdated();
        };
        /**
```
