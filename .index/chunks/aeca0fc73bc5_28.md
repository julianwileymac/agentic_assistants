# Chunk: aeca0fc73bc5_28

- source: `.venv-lab/Lib/site-packages/notebook/static/1584.5e136a9d8643093bc7e9.js`
- lines: 1838-1886
- chunk: 29/45

```
is.tree || update.viewportChanged || styleChange) {
            this.tree = tree;
            this.decorations = this.buildDeco(update.view, highlighters);
            this.decoratedTo = viewport.to;
        }
    }
    buildDeco(view, highlighters) {
        if (!highlighters || !this.tree.length)
            return _codemirror_view__WEBPACK_IMPORTED_MODULE_2__.Decoration.none;
        let builder = new _codemirror_state__WEBPACK_IMPORTED_MODULE_1__.RangeSetBuilder();
        for (let { from, to } of view.visibleRanges) {
            (0,_lezer_highlight__WEBPACK_IMPORTED_MODULE_3__.highlightTree)(this.tree, highlighters, (from, to, style) => {
                builder.add(from, to, this.markCache[style] || (this.markCache[style] = _codemirror_view__WEBPACK_IMPORTED_MODULE_2__.Decoration.mark({ class: style })));
            }, from, to);
        }
        return builder.finish();
    }
}
const treeHighlighter = /*@__PURE__*/_codemirror_state__WEBPACK_IMPORTED_MODULE_1__.Prec.high(/*@__PURE__*/_codemirror_view__WEBPACK_IMPORTED_MODULE_2__.ViewPlugin.fromClass(TreeHighlighter, {
    decorations: v => v.decorations
}));
/**
A default highlight style (works well with light themes).
*/
const defaultHighlightStyle = /*@__PURE__*/HighlightStyle.define([
    { tag: _lezer_highlight__WEBPACK_IMPORTED_MODULE_3__.tags.meta,
        color: "#404740" },
    { tag: _lezer_highlight__WEBPACK_IMPORTED_MODULE_3__.tags.link,
        textDecoration: "underline" },
    { tag: _lezer_highlight__WEBPACK_IMPORTED_MODULE_3__.tags.heading,
        textDecoration: "underline",
        fontWeight: "bold" },
    { tag: _lezer_highlight__WEBPACK_IMPORTED_MODULE_3__.tags.emphasis,
        fontStyle: "italic" },
    { tag: _lezer_highlight__WEBPACK_IMPORTED_MODULE_3__.tags.strong,
        fontWeight: "bold" },
    { tag: _lezer_highlight__WEBPACK_IMPORTED_MODULE_3__.tags.strikethrough,
        textDecoration: "line-through" },
    { tag: _lezer_highlight__WEBPACK_IMPORTED_MODULE_3__.tags.keyword,
        color: "#708" },
    { tag: [_lezer_highlight__WEBPACK_IMPORTED_MODULE_3__.tags.atom, _lezer_highlight__WEBPACK_IMPORTED_MODULE_3__.tags.bool, _lezer_highlight__WEBPACK_IMPORTED_MODULE_3__.tags.url, _lezer_highlight__WEBPACK_IMPORTED_MODULE_3__.tags.contentSeparator, _lezer_highlight__WEBPACK_IMPORTED_MODULE_3__.tags.labelName],
        color: "#219" },
    { tag: [_lezer_highlight__WEBPACK_IMPORTED_MODULE_3__.tags.literal, _lezer_highlight__WEBPACK_IMPORTED_MODULE_3__.tags.inserted],
        color: "#164" },
    { tag: [_lezer_highlight__WEBPACK_IMPORTED_MODULE_3__.tags.string, _lezer_highlight__WEBPACK_IMPORTED_MODULE_3__.tags.deleted],
        color: "#a11" },
    { tag: [_lezer_highlight__WEBPACK_IMPORTED_MODULE_3__.tags.regexp, _lezer_highlight__WEBPACK_IMPORTED_MODULE_3__.tags.escape, /*@__PURE__*/_lezer_highlight__WEBPACK_IMPORTED_MODULE_3__.tags.special(_lezer_highlight__WEBPACK_IMPORTED_MODULE_3__.tags.string)],
        color: "#e40" },
```
