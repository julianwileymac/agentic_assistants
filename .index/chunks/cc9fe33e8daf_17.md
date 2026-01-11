# Chunk: cc9fe33e8daf_17

- source: `frontend/browser-app/lib/frontend/C_Users_Julian_Wiley_Documents_GitHub_agentic_assistants_frontend_packages_agentic-artifacts_-341fb0.js`
- lines: 994-1050
- chunk: 18/19

```
tants\\frontend\\node_modules\\@theia\\core\\lib\\browser\\index.js");
const artifacts_tree_widget_1 = __webpack_require__(/*! ./artifacts-tree-widget */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\packages\\agentic-artifacts\\lib\\browser\\artifacts-tree-widget.js");
const artifact_commands_1 = __webpack_require__(/*! ./artifact-commands */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\packages\\agentic-artifacts\\lib\\browser\\artifact-commands.js");
let ArtifactsViewContribution = class ArtifactsViewContribution extends browser_1.AbstractViewContribution {
    constructor() {
        super({
            widgetId: artifacts_tree_widget_1.ARTIFACTS_TREE_WIDGET_ID,
            widgetName: artifacts_tree_widget_1.ArtifactsTreeWidget.LABEL,
            defaultWidgetOptions: {
                area: 'left',
                rank: 300
            },
            toggleCommandId: artifact_commands_1.ArtifactCommands.TOGGLE_ARTIFACTS_VIEW.id
        });
    }
    async initializeLayout() {
        await this.openView({ activate: false });
    }
};
ArtifactsViewContribution = __decorate([
    (0, inversify_1.injectable)(),
    __metadata("design:paramtypes", [])
], ArtifactsViewContribution);
exports.ArtifactsViewContribution = ArtifactsViewContribution;


/***/ },

/***/ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\packages\\agentic-core\\lib\\browser\\index.js"
/*!*********************************************************************************************************************!*\
  !*** C:\Users\Julian Wiley\Documents\GitHub\agentic_assistants\frontend\packages\agentic-core\lib\browser\index.js ***!
  \*********************************************************************************************************************/
(__unused_webpack_module, exports, __webpack_require__) {


/**
 * Agentic Core Extension - Browser Entry Point
 *
 * Re-exports all public APIs from the core extension.
 */
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __exportStar = (this && this.__exportStar) || function(m, exports) {
    for (var p in m) if (p !== "default" && !Object.prototype.hasOwnProperty.call(exports, p)) __createBinding(exports, m, p);
};
Object.defineProperty(exports, "__esModule", ({ value: true }));
__exportStar(__webpack_require__(/*! ./agentic-backend-service */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\packages\\agentic-core\\lib\\browser\\agentic-backend-service.js"), exports);
```
