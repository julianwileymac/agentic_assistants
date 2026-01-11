# Chunk: aeca0fc73bc5_21

- source: `.venv-lab/Lib/site-packages/notebook/static/1584.5e136a9d8643093bc7e9.js`
- lines: 1385-1455
- chunk: 22/45

```
eld.define({
    create() {
        return _codemirror_view__WEBPACK_IMPORTED_MODULE_2__.Decoration.none;
    },
    update(folded, tr) {
        folded = folded.map(tr.changes);
        for (let e of tr.effects) {
            if (e.is(foldEffect) && !foldExists(folded, e.value.from, e.value.to)) {
                let { preparePlaceholder } = tr.state.facet(foldConfig);
                let widget = !preparePlaceholder ? foldWidget :
                    _codemirror_view__WEBPACK_IMPORTED_MODULE_2__.Decoration.replace({ widget: new PreparedFoldWidget(preparePlaceholder(tr.state, e.value)) });
                folded = folded.update({ add: [widget.range(e.value.from, e.value.to)] });
            }
            else if (e.is(unfoldEffect)) {
                folded = folded.update({ filter: (from, to) => e.value.from != from || e.value.to != to,
                    filterFrom: e.value.from, filterTo: e.value.to });
            }
        }
        // Clear folded ranges that cover the selection head
        if (tr.selection) {
            let onSelection = false, { head } = tr.selection.main;
            folded.between(head, head, (a, b) => { if (a < head && b > head)
                onSelection = true; });
            if (onSelection)
                folded = folded.update({
                    filterFrom: head,
                    filterTo: head,
                    filter: (a, b) => b <= head || a >= head
                });
        }
        return folded;
    },
    provide: f => _codemirror_view__WEBPACK_IMPORTED_MODULE_2__.EditorView.decorations.from(f),
    toJSON(folded, state) {
        let ranges = [];
        folded.between(0, state.doc.length, (from, to) => { ranges.push(from, to); });
        return ranges;
    },
    fromJSON(value) {
        if (!Array.isArray(value) || value.length % 2)
            throw new RangeError("Invalid JSON for fold state");
        let ranges = [];
        for (let i = 0; i < value.length;) {
            let from = value[i++], to = value[i++];
            if (typeof from != "number" || typeof to != "number")
                throw new RangeError("Invalid JSON for fold state");
            ranges.push(foldWidget.range(from, to));
        }
        return _codemirror_view__WEBPACK_IMPORTED_MODULE_2__.Decoration.set(ranges, true);
    }
});
/**
Get a [range set](https://codemirror.net/6/docs/ref/#state.RangeSet) containing the folded ranges
in the given state.
*/
function foldedRanges(state) {
    return state.field(foldState, false) || _codemirror_state__WEBPACK_IMPORTED_MODULE_1__.RangeSet.empty;
}
function findFold(state, from, to) {
    var _a;
    let found = null;
    (_a = state.field(foldState, false)) === null || _a === void 0 ? void 0 : _a.between(from, to, (from, to) => {
        if (!found || found.from > from)
            found = { from, to };
    });
    return found;
}
function foldExists(folded, from, to) {
    let found = false;
    folded.between(from, from, (a, b) => { if (a == from && b == to)
```
