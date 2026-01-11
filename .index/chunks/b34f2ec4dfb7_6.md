# Chunk: b34f2ec4dfb7_6

- source: `frontend/browser-app/lib/frontend/C_Users_Julian_Wiley_Documents_GitHub_agentic_assistants_frontend_packages_agentic-mlflow_lib-255529.js`
- lines: 282-332
- chunk: 7/16

```
****************************************************************************************************************************************/
(__unused_webpack_module, exports, __webpack_require__) {


/**
 * Experiments View Contribution
 *
 * Registers the experiments tree view in the left panel.
 */
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};
Object.defineProperty(exports, "__esModule", ({ value: true }));
exports.ExperimentsViewContribution = void 0;
const inversify_1 = __webpack_require__(/*! @theia/core/shared/inversify */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\core\\shared\\inversify\\index.js");
const browser_1 = __webpack_require__(/*! @theia/core/lib/browser */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\core\\lib\\browser\\index.js");
const experiments_tree_widget_1 = __webpack_require__(/*! ./experiments-tree-widget */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\packages\\agentic-mlflow\\lib\\browser\\experiments-tree-widget.js");
const mlflow_commands_1 = __webpack_require__(/*! ./mlflow-commands */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\packages\\agentic-mlflow\\lib\\browser\\mlflow-commands.js");
let ExperimentsViewContribution = class ExperimentsViewContribution extends browser_1.AbstractViewContribution {
    constructor() {
        super({
            widgetId: experiments_tree_widget_1.EXPERIMENTS_TREE_WIDGET_ID,
            widgetName: experiments_tree_widget_1.ExperimentsTreeWidget.LABEL,
            defaultWidgetOptions: {
                area: 'left',
                rank: 200
            },
            toggleCommandId: mlflow_commands_1.MLFlowCommands.TOGGLE_EXPERIMENTS_VIEW.id
        });
    }
    async initializeLayout() {
        await this.openView({ activate: false });
    }
};
ExperimentsViewContribution = __decorate([
    (0, inversify_1.injectable)(),
    __metadata("design:paramtypes", [])
], ExperimentsViewContribution);
exports.ExperimentsViewContribution = ExperimentsViewContribution;


/***/ },

/***/ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\packages\\agentic-mlflow\\lib\\browser\\mlflow-commands.js"
```
