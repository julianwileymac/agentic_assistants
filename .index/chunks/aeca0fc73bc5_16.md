# Chunk: aeca0fc73bc5_16

- source: `.venv-lab/Lib/site-packages/notebook/static/1584.5e136a9d8643093bc7e9.js`
- lines: 1046-1132
- chunk: 17/45

```
 text.search(/\S|$/));
    }
    /**
    Returns the [simulated line
    break](https://codemirror.net/6/docs/ref/#language.IndentContext.constructor^options.simulateBreak)
    for this context, if any.
    */
    get simulatedBreak() {
        return this.options.simulateBreak || null;
    }
}
/**
A syntax tree node prop used to associate indentation strategies
with node types. Such a strategy is a function from an indentation
context to a column number (see also
[`indentString`](https://codemirror.net/6/docs/ref/#language.indentString)) or null, where null
indicates that no definitive indentation can be determined.
*/
const indentNodeProp = /*@__PURE__*/new _lezer_common__WEBPACK_IMPORTED_MODULE_0__.NodeProp();
// Compute the indentation for a given position from the syntax tree.
function syntaxIndentation(cx, ast, pos) {
    let stack = ast.resolveStack(pos);
    let inner = ast.resolveInner(pos, -1).resolve(pos, 0).enterUnfinishedNodesBefore(pos);
    if (inner != stack.node) {
        let add = [];
        for (let cur = inner; cur && !(cur.from == stack.node.from && cur.type == stack.node.type); cur = cur.parent)
            add.push(cur);
        for (let i = add.length - 1; i >= 0; i--)
            stack = { node: add[i], next: stack };
    }
    return indentFor(stack, cx, pos);
}
function indentFor(stack, cx, pos) {
    for (let cur = stack; cur; cur = cur.next) {
        let strategy = indentStrategy(cur.node);
        if (strategy)
            return strategy(TreeIndentContext.create(cx, pos, cur));
    }
    return 0;
}
function ignoreClosed(cx) {
    return cx.pos == cx.options.simulateBreak && cx.options.simulateDoubleBreak;
}
function indentStrategy(tree) {
    let strategy = tree.type.prop(indentNodeProp);
    if (strategy)
        return strategy;
    let first = tree.firstChild, close;
    if (first && (close = first.type.prop(_lezer_common__WEBPACK_IMPORTED_MODULE_0__.NodeProp.closedBy))) {
        let last = tree.lastChild, closed = last && close.indexOf(last.name) > -1;
        return cx => delimitedStrategy(cx, true, 1, undefined, closed && !ignoreClosed(cx) ? last.from : undefined);
    }
    return tree.parent == null ? topIndent : null;
}
function topIndent() { return 0; }
/**
Objects of this type provide context information and helper
methods to indentation functions registered on syntax nodes.
*/
class TreeIndentContext extends IndentContext {
    constructor(base, 
    /**
    The position at which indentation is being computed.
    */
    pos, 
    /**
    @internal
    */
    context) {
        super(base.state, base.options);
        this.base = base;
        this.pos = pos;
        this.context = context;
    }
    /**
    The syntax tree node to which the indentation strategy
    applies.
    */
    get node() { return this.context.node; }
    /**
    @internal
    */
    static create(base, pos, context) {
        return new TreeIndentContext(base, pos, context);
    }
    /**
```
