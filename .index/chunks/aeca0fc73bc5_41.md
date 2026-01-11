# Chunk: aeca0fc73bc5_41

- source: `.venv-lab/Lib/site-packages/notebook/static/1584.5e136a9d8643093bc7e9.js`
- lines: 2669-2742
- chunk: 42/45

```
e != this.tree || update.docChanged || update.viewportChanged) {
            this.tree = tree;
            this.always = always;
            this.decorations = buildDeco(update.view, tree, always);
        }
    }
}, {
    provide: plugin => {
        function access(view) {
            var _a, _b;
            return (_b = (_a = view.plugin(plugin)) === null || _a === void 0 ? void 0 : _a.decorations) !== null && _b !== void 0 ? _b : _codemirror_view__WEBPACK_IMPORTED_MODULE_2__.Decoration.none;
        }
        return [_codemirror_view__WEBPACK_IMPORTED_MODULE_2__.EditorView.outerDecorations.of(access),
            _codemirror_state__WEBPACK_IMPORTED_MODULE_1__.Prec.lowest(_codemirror_view__WEBPACK_IMPORTED_MODULE_2__.EditorView.bidiIsolatedRanges.of(access))];
    }
});
function buildDeco(view, tree, always) {
    let deco = new _codemirror_state__WEBPACK_IMPORTED_MODULE_1__.RangeSetBuilder();
    let ranges = view.visibleRanges;
    if (!always)
        ranges = clipRTLLines(ranges, view.state.doc);
    for (let { from, to } of ranges) {
        tree.iterate({
            enter: node => {
                let iso = node.type.prop(_lezer_common__WEBPACK_IMPORTED_MODULE_0__.NodeProp.isolate);
                if (iso)
                    deco.add(node.from, node.to, marks[iso]);
            },
            from, to
        });
    }
    return deco.finish();
}
function clipRTLLines(ranges, doc) {
    let cur = doc.iter(), pos = 0, result = [], last = null;
    for (let { from, to } of ranges) {
        if (last && last.to > from) {
            from = last.to;
            if (from >= to)
                continue;
        }
        if (pos + cur.value.length < from) {
            cur.next(from - (pos + cur.value.length));
            pos = from;
        }
        for (;;) {
            let start = pos, end = pos + cur.value.length;
            if (!cur.lineBreak && buildForLine(cur.value)) {
                if (last && last.to > start - 10)
                    last.to = Math.min(to, end);
                else
                    result.push(last = { from: start, to: Math.min(to, end) });
            }
            if (end >= to)
                break;
            pos = end;
            cur.next();
        }
    }
    return result;
}
const marks = {
    rtl: /*@__PURE__*/_codemirror_view__WEBPACK_IMPORTED_MODULE_2__.Decoration.mark({ class: "cm-iso", inclusive: true, attributes: { dir: "rtl" }, bidiIsolate: _codemirror_view__WEBPACK_IMPORTED_MODULE_2__.Direction.RTL }),
    ltr: /*@__PURE__*/_codemirror_view__WEBPACK_IMPORTED_MODULE_2__.Decoration.mark({ class: "cm-iso", inclusive: true, attributes: { dir: "ltr" }, bidiIsolate: _codemirror_view__WEBPACK_IMPORTED_MODULE_2__.Direction.LTR }),
    auto: /*@__PURE__*/_codemirror_view__WEBPACK_IMPORTED_MODULE_2__.Decoration.mark({ class: "cm-iso", inclusive: true, attributes: { dir: "auto" }, bidiIsolate: null })
};




/***/ }),

/***/ 4434:
```
