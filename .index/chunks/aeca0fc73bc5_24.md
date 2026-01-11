# Chunk: aeca0fc73bc5_24

- source: `.venv-lab/Lib/site-packages/notebook/static/1584.5e136a9d8643093bc7e9.js`
- lines: 1588-1662
- chunk: 25/45

```
foldState, baseTheme$1];
    if (config)
        result.push(foldConfig.of(config));
    return result;
}
function widgetToDOM(view, prepared) {
    let { state } = view, conf = state.facet(foldConfig);
    let onclick = (event) => {
        let line = view.lineBlockAt(view.posAtDOM(event.target));
        let folded = findFold(view.state, line.from, line.to);
        if (folded)
            view.dispatch({ effects: unfoldEffect.of(folded) });
        event.preventDefault();
    };
    if (conf.placeholderDOM)
        return conf.placeholderDOM(view, onclick, prepared);
    let element = document.createElement("span");
    element.textContent = conf.placeholderText;
    element.setAttribute("aria-label", state.phrase("folded code"));
    element.title = state.phrase("unfold");
    element.className = "cm-foldPlaceholder";
    element.onclick = onclick;
    return element;
}
const foldWidget = /*@__PURE__*/_codemirror_view__WEBPACK_IMPORTED_MODULE_2__.Decoration.replace({ widget: /*@__PURE__*/new class extends _codemirror_view__WEBPACK_IMPORTED_MODULE_2__.WidgetType {
        toDOM(view) { return widgetToDOM(view, null); }
    } });
class PreparedFoldWidget extends _codemirror_view__WEBPACK_IMPORTED_MODULE_2__.WidgetType {
    constructor(value) {
        super();
        this.value = value;
    }
    eq(other) { return this.value == other.value; }
    toDOM(view) { return widgetToDOM(view, this.value); }
}
const foldGutterDefaults = {
    openText: "⌄",
    closedText: "›",
    markerDOM: null,
    domEventHandlers: {},
    foldingChanged: () => false
};
class FoldMarker extends _codemirror_view__WEBPACK_IMPORTED_MODULE_2__.GutterMarker {
    constructor(config, open) {
        super();
        this.config = config;
        this.open = open;
    }
    eq(other) { return this.config == other.config && this.open == other.open; }
    toDOM(view) {
        if (this.config.markerDOM)
            return this.config.markerDOM(this.open);
        let span = document.createElement("span");
        span.textContent = this.open ? this.config.openText : this.config.closedText;
        span.title = view.state.phrase(this.open ? "Fold line" : "Unfold line");
        return span;
    }
}
/**
Create an extension that registers a fold gutter, which shows a
fold status indicator before foldable lines (which can be clicked
to fold or unfold the line).
*/
function foldGutter(config = {}) {
    let fullConfig = Object.assign(Object.assign({}, foldGutterDefaults), config);
    let canFold = new FoldMarker(fullConfig, true), canUnfold = new FoldMarker(fullConfig, false);
    let markers = _codemirror_view__WEBPACK_IMPORTED_MODULE_2__.ViewPlugin.fromClass(class {
        constructor(view) {
            this.from = view.viewport.from;
            this.markers = this.buildMarkers(view);
        }
        update(update) {
            if (update.docChanged || update.viewportChanged ||
                update.startState.facet(language) != update.state.facet(language) ||
```
