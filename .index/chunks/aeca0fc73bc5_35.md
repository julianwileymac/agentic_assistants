# Chunk: aeca0fc73bc5_35

- source: `.venv-lab/Lib/site-packages/notebook/static/1584.5e136a9d8643093bc7e9.js`
- lines: 2284-2355
- chunk: 36/45

```
       self = this;
        this.streamParser = p;
        this.stateAfter = new _lezer_common__WEBPACK_IMPORTED_MODULE_0__.NodeProp({ perNode: true });
        this.tokenTable = parser.tokenTable ? new TokenTable(p.tokenTable) : defaultTokenTable;
    }
    /**
    Define a stream language.
    */
    static define(spec) { return new StreamLanguage(spec); }
    /**
    @internal
    */
    getIndent(cx) {
        let from = undefined;
        let { overrideIndentation } = cx.options;
        if (overrideIndentation) {
            from = IndentedFrom.get(cx.state);
            if (from != null && from < cx.pos - 1e4)
                from = undefined;
        }
        let start = findState(this, cx.node.tree, cx.node.from, cx.node.from, from !== null && from !== void 0 ? from : cx.pos), statePos, state;
        if (start) {
            state = start.state;
            statePos = start.pos + 1;
        }
        else {
            state = this.streamParser.startState(cx.unit);
            statePos = cx.node.from;
        }
        if (cx.pos - statePos > 10000 /* C.MaxIndentScanDist */)
            return null;
        while (statePos < cx.pos) {
            let line = cx.state.doc.lineAt(statePos), end = Math.min(cx.pos, line.to);
            if (line.length) {
                let indentation = overrideIndentation ? overrideIndentation(line.from) : -1;
                let stream = new StringStream(line.text, cx.state.tabSize, cx.unit, indentation < 0 ? undefined : indentation);
                while (stream.pos < end - line.from)
                    readToken(this.streamParser.token, stream, state);
            }
            else {
                this.streamParser.blankLine(state, cx.unit);
            }
            if (end == cx.pos)
                break;
            statePos = line.to + 1;
        }
        let line = cx.lineAt(cx.pos);
        if (overrideIndentation && from == null)
            IndentedFrom.set(cx.state, line.from);
        return this.streamParser.indent(state, /^\s*(.*)/.exec(line.text)[1], cx);
    }
    get allowsNesting() { return false; }
}
function findState(lang, tree, off, startPos, before) {
    let state = off >= startPos && off + tree.length <= before && tree.prop(lang.stateAfter);
    if (state)
        return { state: lang.streamParser.copyState(state), pos: off + tree.length };
    for (let i = tree.children.length - 1; i >= 0; i--) {
        let child = tree.children[i], pos = off + tree.positions[i];
        let found = child instanceof _lezer_common__WEBPACK_IMPORTED_MODULE_0__.Tree && pos < before && findState(lang, child, pos, startPos, before);
        if (found)
            return found;
    }
    return null;
}
function cutTree(lang, tree, from, to, inside) {
    if (inside && from <= 0 && to >= tree.length)
        return tree;
    if (!inside && from == 0 && tree.type == lang.topNode)
        inside = true;
    for (let i = tree.children.length - 1; i >= 0; i--) {
```
