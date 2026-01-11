# Chunk: feff6ec6d74f_70

- source: `.venv-lab/Lib/site-packages/notebook/static/1871.c375ee093b7e51966390.js`
- lines: 3351-3455
- chunk: 71/78

```
d)}`;
    if (true)
        return key;
    return `${styles.$displayName}_${key}`;
}
/**
 * The FreeStyle class implements the API for everything else.
 */
class FreeStyle extends Cache {
    constructor(id, changes) {
        super(changes);
        this.id = id;
    }
    registerStyle(styles) {
        const rulesList = [];
        const stylesList = [];
        const pid = stylize("&", styles, rulesList, stylesList);
        const id = key(pid, styles);
        const selector = `.${ true ? id : 0}`;
        composeStylize(this, pid, rulesList, stylesList, selector, true);
        return id;
    }
    registerKeyframes(keyframes) {
        return this.registerHashRule("@keyframes", keyframes);
    }
    registerHashRule(prefix, styles) {
        const rulesList = [];
        const stylesList = [];
        const pid = stylize("", styles, rulesList, stylesList);
        const id = key(pid, styles);
        const selector = `${prefix} ${ true ? id : 0}`;
        const rule = new Rule(selector, "", `h\0${pid}\0${prefix}`);
        composeStylize(rule, pid, rulesList, stylesList, "", false);
        this.add(rule);
        return id;
    }
    registerRule(rule, styles) {
        const rulesList = [];
        const stylesList = [];
        const pid = stylize(rule, styles, rulesList, stylesList);
        composeStylize(this, pid, rulesList, stylesList, "", false);
    }
    registerCss(styles) {
        return this.registerRule("", styles);
    }
    getStyles() {
        return join(this.sheet);
    }
    clone() {
        return new FreeStyle(this.id, this.changes).merge(this);
    }
}
/**
 * Exports a simple function to create a new instance.
 */
function create(changes) {
    return new FreeStyle(`f${(++uniqueId).toString(36)}`, changes);
}
//# sourceMappingURL=index.js.map

/***/ }),

/***/ 63005:
/***/ ((module, __unused_webpack_exports, __webpack_require__) => {

var basePickBy = __webpack_require__(10228),
    hasIn = __webpack_require__(79749);

/**
 * The base implementation of `_.pick` without support for individual
 * property identifiers.
 *
 * @private
 * @param {Object} object The source object.
 * @param {string[]} paths The property paths to pick.
 * @returns {Object} Returns the new object.
 */
function basePick(object, paths) {
  return basePickBy(object, paths, function(value, path) {
    return hasIn(object, path);
  });
}

module.exports = basePick;


/***/ }),

/***/ 10228:
/***/ ((module, __unused_webpack_exports, __webpack_require__) => {

var baseGet = __webpack_require__(79867),
    baseSet = __webpack_require__(78859),
    castPath = __webpack_require__(76747);

/**
 * The base implementation of  `_.pickBy` without support for iteratee shorthands.
 *
 * @private
 * @param {Object} object The source object.
 * @param {string[]} paths The property paths to pick.
 * @param {Function} predicate The function invoked per property.
 * @returns {Object} Returns the new object.
 */
```
