# Chunk: b34f2ec4dfb7_3

- source: `frontend/browser-app/lib/frontend/C_Users_Julian_Wiley_Documents_GitHub_agentic_assistants_frontend_packages_agentic-mlflow_lib-255529.js`
- lines: 102-152
- chunk: 4/16

```
&& Object.defineProperty(target, key, r), r;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};
var __param = (this && this.__param) || function (paramIndex, decorator) {
    return function (target, key) { decorator(target, key, paramIndex); }
};
var ExperimentsTreeWidget_1;
Object.defineProperty(exports, "__esModule", ({ value: true }));
exports.ExperimentsTreeWidget = exports.RunNode = exports.ExperimentNode = exports.EXPERIMENTS_TREE_WIDGET_ID = void 0;
const inversify_1 = __webpack_require__(/*! @theia/core/shared/inversify */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\core\\shared\\inversify\\index.js");
const tree_1 = __webpack_require__(/*! @theia/core/lib/browser/tree */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\core\\lib\\browser\\tree\\index.js");
const browser_1 = __webpack_require__(/*! @theia/core/lib/browser */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\core\\lib\\browser\\index.js");
const core_1 = __webpack_require__(/*! @theia/core */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\core\\lib\\common\\index.js");
const mlflow_service_1 = __webpack_require__(/*! ./mlflow-service */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\packages\\agentic-mlflow\\lib\\browser\\mlflow-service.js");
exports.EXPERIMENTS_TREE_WIDGET_ID = 'experiments-tree-widget';
var ExperimentNode;
(function (ExperimentNode) {
    function is(node) {
        return !!node && 'experiment' in node;
    }
    ExperimentNode.is = is;
})(ExperimentNode = exports.ExperimentNode || (exports.ExperimentNode = {}));
var RunNode;
(function (RunNode) {
    function is(node) {
        return !!node && 'run' in node;
    }
    RunNode.is = is;
})(RunNode = exports.RunNode || (exports.RunNode = {}));
let ExperimentsTreeWidget = ExperimentsTreeWidget_1 = class ExperimentsTreeWidget extends tree_1.TreeWidget {
    constructor(props, model, contextMenuRenderer) {
        super(props, model, contextMenuRenderer);
        this.props = props;
        this.model = model;
        this.contextMenuRenderer = contextMenuRenderer;
        this.id = ExperimentsTreeWidget_1.ID;
        this.title.label = ExperimentsTreeWidget_1.LABEL;
        this.title.caption = ExperimentsTreeWidget_1.LABEL;
        this.title.closable = true;
        this.title.iconClass = 'fa fa-flask';
    }
    init() {
        super.init();
        this.toDispose.push(this.model.onExpansionChanged(async (node) => this.handleNodeExpansion(node)));
        // Listen for experiment changes
        this.mlflowService.onExperimentsChanged(experiments => {
            this.refreshTree();
        });
```
