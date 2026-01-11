# Chunk: feff6ec6d74f_67

- source: `.venv-lab/Lib/site-packages/notebook/static/1871.c375ee093b7e51966390.js`
- lines: 3078-3180
- chunk: 68/78

```
%&()*+,./;<=>?@[\]^`{|}~"'\\]/g, "\\$&");
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
 * Generate a hash value from a string.
 */
function stringHash(str) {
    let value = 5381;
    let len = str.length;
    while (len--)
        value = (value * 33) ^ str.charCodeAt(len);
    return (value >>> 0).toString(36);
}
/**
 * Transform a style string to a CSS string.
 */
function styleToString(key, value) {
    if (value && typeof value === "number" && !CSS_NUMBER[key]) {
        return `${key}:${value}px`;
    }
    return `${key}:${value}`;
}
/**
 * Sort an array of tuples by first value.
 */
function sortTuples(value) {
    return value.sort((a, b) => (a[0] > b[0] ? 1 : -1));
}
/**
 * Categorize user styles.
 */
function parseStyles(styles, hasNestedStyles) {
    const properties = [];
    const nestedStyles = [];
    // Sort keys before adding to styles.
    for (const key of Object.keys(styles)) {
        const name = key.trim();
        const value = styles[key];
        if (name.charCodeAt(0) !== 36 /* $ */ && value != null) {
            if (typeof value === "object" && !Array.isArray(value)) {
                nestedStyles.push([name, value]);
            }
            else {
                properties.push([hyphenate(name), value]);
            }
        }
    }
    return {
        style: stringifyProperties(sortTuples(properties)),
        nested: hasNestedStyles ? nestedStyles : sortTuples(nestedStyles),
        isUnique: !!styles.$unique
    };
}
/**
 * Stringify an array of property tuples.
 */
function stringifyProperties(properties) {
    return properties
        .map(([name, value]) => {
        if (!Array.isArray(value))
            return styleToString(name, value);
        return value.map(x => styleToString(name, x)).join(";");
    })
        .join(";");
}
/**
 * Interpolate CSS selectors.
 */
function interpolate(selector, parent) {
    if (selector.indexOf("&") === -1)
        return `${parent} ${selector}`;
    return selector.replace(/&/g, parent);
}
/**
 * Recursive loop building styles with deferred selectors.
 */
function stylize(selector, styles, rulesList, stylesList, parent) {
    const { style, nested, isUnique } = parseStyles(styles, selector !== "");
    let pid = style;
    if (selector.charCodeAt(0) === 64 /* @ */) {
        const child = {
            selector,
            styles: [],
            rules: [],
            style: parent ? "" : style
        };
        rulesList.push(child);
        // Nested styles support (e.g. `.foo > @media > .bar`).
        if (style && parent) {
            child.styles.push({ selector: parent, style, isUnique });
        }
        for (const [name, value] of nested) {
            pid += name + stylize(name, value, child.rules, child.styles, parent);
        }
    }
```
