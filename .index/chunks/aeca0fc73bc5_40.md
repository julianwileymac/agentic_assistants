# Chunk: aeca0fc73bc5_40

- source: `.venv-lab/Lib/site-packages/notebook/static/1584.5e136a9d8643093bc7e9.js`
- lines: 2613-2679
- chunk: 41/45

```
et type = _lezer_common__WEBPACK_IMPORTED_MODULE_0__.NodeType.define({ id: typeArray.length, name: "Document", props: [
            languageDataProp.add(() => data),
            indentNodeProp.add(() => cx => lang.getIndent(cx))
        ], top: true });
    typeArray.push(type);
    return type;
}

function buildForLine(line) {
    return line.length <= 4096 && /[\u0590-\u05f4\u0600-\u06ff\u0700-\u08ac\ufb50-\ufdff]/.test(line);
}
function textHasRTL(text) {
    for (let i = text.iter(); !i.next().done;)
        if (buildForLine(i.value))
            return true;
    return false;
}
function changeAddsRTL(change) {
    let added = false;
    change.iterChanges((fA, tA, fB, tB, ins) => {
        if (!added && textHasRTL(ins))
            added = true;
    });
    return added;
}
const alwaysIsolate = /*@__PURE__*/_codemirror_state__WEBPACK_IMPORTED_MODULE_1__.Facet.define({ combine: values => values.some(x => x) });
/**
Make sure nodes
[marked](https://lezer.codemirror.net/docs/ref/#common.NodeProp^isolate)
as isolating for bidirectional text are rendered in a way that
isolates them from the surrounding text.
*/
function bidiIsolates(options = {}) {
    let extensions = [isolateMarks];
    if (options.alwaysIsolate)
        extensions.push(alwaysIsolate.of(true));
    return extensions;
}
const isolateMarks = /*@__PURE__*/_codemirror_view__WEBPACK_IMPORTED_MODULE_2__.ViewPlugin.fromClass(class {
    constructor(view) {
        this.always = view.state.facet(alwaysIsolate) ||
            view.textDirection != _codemirror_view__WEBPACK_IMPORTED_MODULE_2__.Direction.LTR ||
            view.state.facet(_codemirror_view__WEBPACK_IMPORTED_MODULE_2__.EditorView.perLineTextDirection);
        this.hasRTL = !this.always && textHasRTL(view.state.doc);
        this.tree = syntaxTree(view.state);
        this.decorations = this.always || this.hasRTL ? buildDeco(view, this.tree, this.always) : _codemirror_view__WEBPACK_IMPORTED_MODULE_2__.Decoration.none;
    }
    update(update) {
        let always = update.state.facet(alwaysIsolate) ||
            update.view.textDirection != _codemirror_view__WEBPACK_IMPORTED_MODULE_2__.Direction.LTR ||
            update.state.facet(_codemirror_view__WEBPACK_IMPORTED_MODULE_2__.EditorView.perLineTextDirection);
        if (!always && !this.hasRTL && changeAddsRTL(update.changes))
            this.hasRTL = true;
        if (!always && !this.hasRTL)
            return;
        let tree = syntaxTree(update.state);
        if (always != this.always || tree != this.tree || update.docChanged || update.viewportChanged) {
            this.tree = tree;
            this.always = always;
            this.decorations = buildDeco(update.view, tree, always);
        }
    }
}, {
    provide: plugin => {
        function access(view) {
            var _a, _b;
```
