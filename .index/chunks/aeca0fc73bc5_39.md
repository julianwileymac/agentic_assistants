# Chunk: aeca0fc73bc5_39

- source: `.venv-lab/Lib/site-packages/notebook/static/1584.5e136a9d8643093bc7e9.js`
- lines: 2536-2621
- chunk: 40/45

```
e.none];
const nodeSet = /*@__PURE__*/new _lezer_common__WEBPACK_IMPORTED_MODULE_0__.NodeSet(typeArray);
const warned = [];
// Cache of node types by name and tags
const byTag = /*@__PURE__*/Object.create(null);
const defaultTable = /*@__PURE__*/Object.create(null);
for (let [legacyName, name] of [
    ["variable", "variableName"],
    ["variable-2", "variableName.special"],
    ["string-2", "string.special"],
    ["def", "variableName.definition"],
    ["tag", "tagName"],
    ["attribute", "attributeName"],
    ["type", "typeName"],
    ["builtin", "variableName.standard"],
    ["qualifier", "modifier"],
    ["error", "invalid"],
    ["header", "heading"],
    ["property", "propertyName"]
])
    defaultTable[legacyName] = /*@__PURE__*/createTokenType(noTokens, name);
class TokenTable {
    constructor(extra) {
        this.extra = extra;
        this.table = Object.assign(Object.create(null), defaultTable);
    }
    resolve(tag) {
        return !tag ? 0 : this.table[tag] || (this.table[tag] = createTokenType(this.extra, tag));
    }
}
const defaultTokenTable = /*@__PURE__*/new TokenTable(noTokens);
function warnForPart(part, msg) {
    if (warned.indexOf(part) > -1)
        return;
    warned.push(part);
    console.warn(msg);
}
function createTokenType(extra, tagStr) {
    let tags$1 = [];
    for (let name of tagStr.split(" ")) {
        let found = [];
        for (let part of name.split(".")) {
            let value = (extra[part] || _lezer_highlight__WEBPACK_IMPORTED_MODULE_3__.tags[part]);
            if (!value) {
                warnForPart(part, `Unknown highlighting tag ${part}`);
            }
            else if (typeof value == "function") {
                if (!found.length)
                    warnForPart(part, `Modifier ${part} used at start of tag`);
                else
                    found = found.map(value);
            }
            else {
                if (found.length)
                    warnForPart(part, `Tag ${part} used as modifier`);
                else
                    found = Array.isArray(value) ? value : [value];
            }
        }
        for (let tag of found)
            tags$1.push(tag);
    }
    if (!tags$1.length)
        return 0;
    let name = tagStr.replace(/ /g, "_"), key = name + " " + tags$1.map(t => t.id);
    let known = byTag[key];
    if (known)
        return known.id;
    let type = byTag[key] = _lezer_common__WEBPACK_IMPORTED_MODULE_0__.NodeType.define({
        id: typeArray.length,
        name,
        props: [(0,_lezer_highlight__WEBPACK_IMPORTED_MODULE_3__.styleTags)({ [name]: tags$1 })]
    });
    typeArray.push(type);
    return type.id;
}
function docID(data, lang) {
    let type = _lezer_common__WEBPACK_IMPORTED_MODULE_0__.NodeType.define({ id: typeArray.length, name: "Document", props: [
            languageDataProp.add(() => data),
            indentNodeProp.add(() => cx => lang.getIndent(cx))
        ], top: true });
    typeArray.push(type);
    return type;
}
```
