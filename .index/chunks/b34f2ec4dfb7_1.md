# Chunk: b34f2ec4dfb7_1

- source: `frontend/browser-app/lib/frontend/C_Users_Julian_Wiley_Documents_GitHub_agentic_assistants_frontend_packages_agentic-mlflow_lib-255529.js`
- lines: 35-65
- chunk: 2/16

```
\\frontend\\packages\\agentic-core\\lib\\browser\\agentic-menu.js"), exports);
__exportStar(__webpack_require__(/*! ./agentic-status-bar */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\packages\\agentic-core\\lib\\browser\\agentic-status-bar.js"), exports);


/***/ },

/***/ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\packages\\agentic-mlflow\\lib\\browser\\agentic-mlflow-frontend-module.js"
/*!************************************************************************************************************************************************!*\
  !*** C:\Users\Julian Wiley\Documents\GitHub\agentic_assistants\frontend\packages\agentic-mlflow\lib\browser\agentic-mlflow-frontend-module.js ***!
  \************************************************************************************************************************************************/
(__unused_webpack_module, exports, __webpack_require__) {


/**
 * Agentic MLFlow Frontend Module
 *
 * Provides MLFlow experiment tracking integration for the Agentic IDE.
 */
Object.defineProperty(exports, "__esModule", ({ value: true }));
const inversify_1 = __webpack_require__(/*! @theia/core/shared/inversify */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\core\\shared\\inversify\\index.js");
const browser_1 = __webpack_require__(/*! @theia/core/lib/browser */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\core\\lib\\browser\\index.js");
const common_1 = __webpack_require__(/*! @theia/core/lib/common */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\core\\lib\\common\\index.js");
const mlflow_service_1 = __webpack_require__(/*! ./mlflow-service */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\packages\\agentic-mlflow\\lib\\browser\\mlflow-service.js");
const experiments_tree_widget_1 = __webpack_require__(/*! ./experiments-tree-widget */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\packages\\agentic-mlflow\\lib\\browser\\experiments-tree-widget.js");
const experiments_view_contribution_1 = __webpack_require__(/*! ./experiments-view-contribution */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\packages\\agentic-mlflow\\lib\\browser\\experiments-view-contribution.js");
const mlflow_commands_1 = __webpack_require__(/*! ./mlflow-commands */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\packages\\agentic-mlflow\\lib\\browser\\mlflow-commands.js");
const mlflow_menu_1 = __webpack_require__(/*! ./mlflow-menu */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\packages\\agentic-mlflow\\lib\\browser\\mlflow-menu.js");
exports["default"] = new inversify_1.ContainerModule(bind => {
    // MLFlow service
    bind(mlflow_service_1.MLFlowService).toSelf().inSingletonScope();
```
