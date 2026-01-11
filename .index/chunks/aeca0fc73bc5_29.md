# Chunk: aeca0fc73bc5_29

- source: `.venv-lab/Lib/site-packages/notebook/static/1584.5e136a9d8643093bc7e9.js`
- lines: 1883-1930
- chunk: 30/45

```
: "#a11" },
    { tag: [_lezer_highlight__WEBPACK_IMPORTED_MODULE_3__.tags.regexp, _lezer_highlight__WEBPACK_IMPORTED_MODULE_3__.tags.escape, /*@__PURE__*/_lezer_highlight__WEBPACK_IMPORTED_MODULE_3__.tags.special(_lezer_highlight__WEBPACK_IMPORTED_MODULE_3__.tags.string)],
        color: "#e40" },
    { tag: /*@__PURE__*/_lezer_highlight__WEBPACK_IMPORTED_MODULE_3__.tags.definition(_lezer_highlight__WEBPACK_IMPORTED_MODULE_3__.tags.variableName),
        color: "#00f" },
    { tag: /*@__PURE__*/_lezer_highlight__WEBPACK_IMPORTED_MODULE_3__.tags.local(_lezer_highlight__WEBPACK_IMPORTED_MODULE_3__.tags.variableName),
        color: "#30a" },
    { tag: [_lezer_highlight__WEBPACK_IMPORTED_MODULE_3__.tags.typeName, _lezer_highlight__WEBPACK_IMPORTED_MODULE_3__.tags.namespace],
        color: "#085" },
    { tag: _lezer_highlight__WEBPACK_IMPORTED_MODULE_3__.tags.className,
        color: "#167" },
    { tag: [/*@__PURE__*/_lezer_highlight__WEBPACK_IMPORTED_MODULE_3__.tags.special(_lezer_highlight__WEBPACK_IMPORTED_MODULE_3__.tags.variableName), _lezer_highlight__WEBPACK_IMPORTED_MODULE_3__.tags.macroName],
        color: "#256" },
    { tag: /*@__PURE__*/_lezer_highlight__WEBPACK_IMPORTED_MODULE_3__.tags.definition(_lezer_highlight__WEBPACK_IMPORTED_MODULE_3__.tags.propertyName),
        color: "#00c" },
    { tag: _lezer_highlight__WEBPACK_IMPORTED_MODULE_3__.tags.comment,
        color: "#940" },
    { tag: _lezer_highlight__WEBPACK_IMPORTED_MODULE_3__.tags.invalid,
        color: "#f00" }
]);

const baseTheme = /*@__PURE__*/_codemirror_view__WEBPACK_IMPORTED_MODULE_2__.EditorView.baseTheme({
    "&.cm-focused .cm-matchingBracket": { backgroundColor: "#328c8252" },
    "&.cm-focused .cm-nonmatchingBracket": { backgroundColor: "#bb555544" }
});
const DefaultScanDist = 10000, DefaultBrackets = "()[]{}";
const bracketMatchingConfig = /*@__PURE__*/_codemirror_state__WEBPACK_IMPORTED_MODULE_1__.Facet.define({
    combine(configs) {
        return (0,_codemirror_state__WEBPACK_IMPORTED_MODULE_1__.combineConfig)(configs, {
            afterCursor: true,
            brackets: DefaultBrackets,
            maxScanDistance: DefaultScanDist,
            renderMatch: defaultRenderMatch
        });
    }
});
const matchingMark = /*@__PURE__*/_codemirror_view__WEBPACK_IMPORTED_MODULE_2__.Decoration.mark({ class: "cm-matchingBracket" }), nonmatchingMark = /*@__PURE__*/_codemirror_view__WEBPACK_IMPORTED_MODULE_2__.Decoration.mark({ class: "cm-nonmatchingBracket" });
function defaultRenderMatch(match) {
    let decorations = [];
    let mark = match.matched ? matchingMark : nonmatchingMark;
    decorations.push(mark.range(match.start.from, match.start.to));
    if (match.end)
        decorations.push(mark.range(match.end.from, match.end.to));
    return decorations;
}
const bracketMatchingState = /*@__PURE__*/_codemirror_state__WEBPACK_IMPORTED_MODULE_1__.StateField.define({
    create() { return _codemirror_view__WEBPACK_IMPORTED_MODULE_2__.Decoration.none; },
```
