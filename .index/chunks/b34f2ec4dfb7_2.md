# Chunk: b34f2ec4dfb7_2

- source: `frontend/browser-app/lib/frontend/C_Users_Julian_Wiley_Documents_GitHub_agentic_assistants_frontend_packages_agentic-mlflow_lib-255529.js`
- lines: 61-108
- chunk: 3/16

```
low-menu */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\packages\\agentic-mlflow\\lib\\browser\\mlflow-menu.js");
exports["default"] = new inversify_1.ContainerModule(bind => {
    // MLFlow service
    bind(mlflow_service_1.MLFlowService).toSelf().inSingletonScope();
    bind(mlflow_service_1.MLFlowServiceSymbol).toService(mlflow_service_1.MLFlowService);
    // Experiments tree widget
    bind(experiments_tree_widget_1.ExperimentsTreeWidget).toSelf();
    bind(browser_1.WidgetFactory).toDynamicValue(ctx => ({
        id: experiments_tree_widget_1.EXPERIMENTS_TREE_WIDGET_ID,
        createWidget: () => ctx.container.get(experiments_tree_widget_1.ExperimentsTreeWidget)
    })).inSingletonScope();
    // View contribution
    (0, browser_1.bindViewContribution)(bind, experiments_view_contribution_1.ExperimentsViewContribution);
    bind(browser_1.FrontendApplicationContribution).toService(experiments_view_contribution_1.ExperimentsViewContribution);
    // Command contribution
    bind(mlflow_commands_1.MLFlowCommandContribution).toSelf().inSingletonScope();
    bind(common_1.CommandContribution).toService(mlflow_commands_1.MLFlowCommandContribution);
    // Menu contribution
    bind(mlflow_menu_1.MLFlowMenuContribution).toSelf().inSingletonScope();
    bind(common_1.MenuContribution).toService(mlflow_menu_1.MLFlowMenuContribution);
});


/***/ },

/***/ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\packages\\agentic-mlflow\\lib\\browser\\experiments-tree-widget.js"
/*!*****************************************************************************************************************************************!*\
  !*** C:\Users\Julian Wiley\Documents\GitHub\agentic_assistants\frontend\packages\agentic-mlflow\lib\browser\experiments-tree-widget.js ***!
  \*****************************************************************************************************************************************/
(__unused_webpack_module, exports, __webpack_require__) {


/**
 * Experiments Tree Widget
 *
 * Provides a tree view for browsing MLFlow experiments and runs.
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
var __param = (this && this.__param) || function (paramIndex, decorator) {
```
