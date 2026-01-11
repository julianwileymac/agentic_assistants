# Chunk: feff6ec6d74f_66

- source: `.venv-lab/Lib/site-packages/notebook/static/1871.c375ee093b7e51966390.js`
- lines: 2977-3089
- chunk: 67/78

```
id 0 ? void 0 : _a.ButtonTemplates,
                ...templates === null || templates === void 0 ? void 0 : templates.ButtonTemplates,
            },
        };
        return (_jsx(Form, { ...themeProps, ...directProps, fields: fields, widgets: widgets, templates: templates, ref: ref }));
    });
}
//# sourceMappingURL=withTheme.js.map
;// CONCATENATED MODULE: ../node_modules/@rjsf/core/lib/index.js




/* harmony default export */ const lib = (Form_Form);
//# sourceMappingURL=index.js.map

/***/ }),

/***/ 8843:
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   Cache: () => (/* binding */ Cache),
/* harmony export */   FreeStyle: () => (/* binding */ FreeStyle),
/* harmony export */   Rule: () => (/* binding */ Rule),
/* harmony export */   Selector: () => (/* binding */ Selector),
/* harmony export */   Style: () => (/* binding */ Style),
/* harmony export */   create: () => (/* binding */ create)
/* harmony export */ });
/**
 * The unique id is used for unique hashes.
 */
let uniqueId = 0;
/**
 * Quick dictionary lookup for unit-less numbers.
 */
const CSS_NUMBER = Object.create(null);
/**
 * CSS properties that are valid unit-less numbers.
 *
 * Ref: https://github.com/facebook/react/blob/master/packages/react-dom/src/shared/CSSProperty.js
 */
const CSS_NUMBER_KEYS = [
    "animation-iteration-count",
    "border-image-outset",
    "border-image-slice",
    "border-image-width",
    "box-flex",
    "box-flex-group",
    "box-ordinal-group",
    "column-count",
    "columns",
    "counter-increment",
    "counter-reset",
    "flex",
    "flex-grow",
    "flex-positive",
    "flex-shrink",
    "flex-negative",
    "flex-order",
    "font-weight",
    "grid-area",
    "grid-column",
    "grid-column-end",
    "grid-column-span",
    "grid-column-start",
    "grid-row",
    "grid-row-end",
    "grid-row-span",
    "grid-row-start",
    "line-clamp",
    "line-height",
    "opacity",
    "order",
    "orphans",
    "tab-size",
    "widows",
    "z-index",
    "zoom",
    // SVG properties.
    "fill-opacity",
    "flood-opacity",
    "stop-opacity",
    "stroke-dasharray",
    "stroke-dashoffset",
    "stroke-miterlimit",
    "stroke-opacity",
    "stroke-width"
];
// Add vendor prefixes to all unit-less properties.
for (const property of CSS_NUMBER_KEYS) {
    for (const prefix of ["-webkit-", "-ms-", "-moz-", "-o-", ""]) {
        CSS_NUMBER[prefix + property] = true;
    }
}
/**
 * Escape a CSS class name.
 */
function escape(str) {
    return str.replace(/[ !#$%&()*+,./;<=>?@[\]^`{|}~"'\\]/g, "\\$&");
}
/**
 * Transform a JavaScript property into a CSS property.
 */
function hyphenate(propertyName) {
    return propertyName
        .replace(/[A-Z]/g, (m) => `-${m.toLowerCase()}`)
        .replace(/^ms-/, "-ms-"); // Internet Explorer vendor prefix.
}
/**
```
