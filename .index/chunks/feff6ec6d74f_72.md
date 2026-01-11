# Chunk: feff6ec6d74f_72

- source: `.venv-lab/Lib/site-packages/notebook/static/1871.c375ee093b7e51966390.js`
- lines: 3569-3658
- chunk: 73/78

```
pack_unused_export__;

__webpack_unused_export__ = ({ value: true });
var typestyle_1 = __webpack_require__(53861);
__webpack_unused_export__ = typestyle_1.TypeStyle;
/**
 * All the CSS types in the 'types' namespace
 */
var types = __webpack_require__(66720);
__webpack_unused_export__ = types;
/**
 * Export certain utilities
 */
var utilities_1 = __webpack_require__(51833);
__webpack_unused_export__ = utilities_1.extend;
__webpack_unused_export__ = utilities_1.classes;
__webpack_unused_export__ = utilities_1.media;
/** Zero configuration, default instance of TypeStyle */
var ts = new typestyle_1.TypeStyle({ autoGenerateTag: true });
/** Sets the target tag where we write the css on style updates */
__webpack_unused_export__ = ts.setStylesTarget;
/**
 * Insert `raw` CSS as a string. This is useful for e.g.
 * - third party CSS that you are customizing with template strings
 * - generating raw CSS in JavaScript
 * - reset libraries like normalize.css that you can use without loaders
 */
__webpack_unused_export__ = ts.cssRaw;
/**
 * Takes CSSProperties and registers it to a global selector (body, html, etc.)
 */
__webpack_unused_export__ = ts.cssRule;
/**
 * Renders styles to the singleton tag imediately
 * NOTE: You should only call it on initial render to prevent any non CSS flash.
 * After that it is kept sync using `requestAnimationFrame` and we haven't noticed any bad flashes.
 **/
__webpack_unused_export__ = ts.forceRenderStyles;
/**
 * Utility function to register an @font-face
 */
__webpack_unused_export__ = ts.fontFace;
/**
 * Allows use to use the stylesheet in a node.js environment
 */
__webpack_unused_export__ = ts.getStyles;
/**
 * Takes keyframes and returns a generated animationName
 */
__webpack_unused_export__ = ts.keyframes;
/**
 * Helps with testing. Reinitializes FreeStyle + raw
 */
__webpack_unused_export__ = ts.reinit;
/**
 * Takes CSSProperties and return a generated className you can use on your component
 */
exports.oB = ts.style;
/**
 * Takes an object where property names are ideal class names and property values are CSSProperties, and
 * returns an object where property names are the same ideal class names and the property values are
 * the actual generated class names using the ideal class name as the $debugName
 */
__webpack_unused_export__ = ts.stylesheet;
/**
 * Creates a new instance of TypeStyle separate from the default instance.
 *
 * - Use this for creating a different typestyle instance for a shadow dom component.
 * - Use this if you don't want an auto tag generated and you just want to collect the CSS.
 *
 * NOTE: styles aren't shared between different instances.
 */
function createTypeStyle(target) {
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
```
