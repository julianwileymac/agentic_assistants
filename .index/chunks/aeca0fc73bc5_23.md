# Chunk: aeca0fc73bc5_23

- source: `.venv-lab/Lib/site-packages/notebook/static/1584.5e136a9d8643093bc7e9.js`
- lines: 1518-1597
- chunk: 24/45

```
= view => {
    let field = view.state.field(foldState, false);
    if (!field || !field.size)
        return false;
    let effects = [];
    field.between(0, view.state.doc.length, (from, to) => { effects.push(unfoldEffect.of({ from, to })); });
    view.dispatch({ effects });
    return true;
};
// Find the foldable region containing the given line, if one exists
function foldableContainer(view, lineBlock) {
    // Look backwards through line blocks until we find a foldable region that
    // intersects with the line
    for (let line = lineBlock;;) {
        let foldableRegion = foldable(view.state, line.from, line.to);
        if (foldableRegion && foldableRegion.to > lineBlock.from)
            return foldableRegion;
        if (!line.from)
            return null;
        line = view.lineBlockAt(line.from - 1);
    }
}
/**
Toggle folding at cursors. Unfolds if there is an existing fold
starting in that line, tries to find a foldable range around it
otherwise.
*/
const toggleFold = (view) => {
    let effects = [];
    for (let line of selectedLines(view)) {
        let folded = findFold(view.state, line.from, line.to);
        if (folded) {
            effects.push(unfoldEffect.of(folded), announceFold(view, folded, false));
        }
        else {
            let foldRange = foldableContainer(view, line);
            if (foldRange)
                effects.push(foldEffect.of(foldRange), announceFold(view, foldRange));
        }
    }
    if (effects.length > 0)
        view.dispatch({ effects: maybeEnable(view.state, effects) });
    return !!effects.length;
};
/**
Default fold-related key bindings.

 - Ctrl-Shift-[ (Cmd-Alt-[ on macOS): [`foldCode`](https://codemirror.net/6/docs/ref/#language.foldCode).
 - Ctrl-Shift-] (Cmd-Alt-] on macOS): [`unfoldCode`](https://codemirror.net/6/docs/ref/#language.unfoldCode).
 - Ctrl-Alt-[: [`foldAll`](https://codemirror.net/6/docs/ref/#language.foldAll).
 - Ctrl-Alt-]: [`unfoldAll`](https://codemirror.net/6/docs/ref/#language.unfoldAll).
*/
const foldKeymap = [
    { key: "Ctrl-Shift-[", mac: "Cmd-Alt-[", run: foldCode },
    { key: "Ctrl-Shift-]", mac: "Cmd-Alt-]", run: unfoldCode },
    { key: "Ctrl-Alt-[", run: foldAll },
    { key: "Ctrl-Alt-]", run: unfoldAll }
];
const defaultConfig = {
    placeholderDOM: null,
    preparePlaceholder: null,
    placeholderText: "…"
};
const foldConfig = /*@__PURE__*/_codemirror_state__WEBPACK_IMPORTED_MODULE_1__.Facet.define({
    combine(values) { return (0,_codemirror_state__WEBPACK_IMPORTED_MODULE_1__.combineConfig)(values, defaultConfig); }
});
/**
Create an extension that configures code folding.
*/
function codeFolding(config) {
    let result = [foldState, baseTheme$1];
    if (config)
        result.push(foldConfig.of(config));
    return result;
}
function widgetToDOM(view, prepared) {
    let { state } = view, conf = state.facet(foldConfig);
    let onclick = (event) => {
        let line = view.lineBlockAt(view.posAtDOM(event.target));
```
