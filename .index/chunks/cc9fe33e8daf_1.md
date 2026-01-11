# Chunk: cc9fe33e8daf_1

- source: `frontend/browser-app/lib/frontend/C_Users_Julian_Wiley_Documents_GitHub_agentic_assistants_frontend_packages_agentic-artifacts_-341fb0.js`
- lines: 24-71
- chunk: 2/19

```
 "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\packages\\agentic-artifacts\\lib\\browser\\artifact-menu.js");
exports["default"] = new inversify_1.ContainerModule(bind => {
    // Artifact service
    bind(artifact_service_1.ArtifactService).toSelf().inSingletonScope();
    bind(artifact_service_1.ArtifactServiceSymbol).toService(artifact_service_1.ArtifactService);
    // Artifacts tree widget
    bind(artifacts_tree_widget_1.ArtifactsTreeWidget).toSelf();
    bind(browser_1.WidgetFactory).toDynamicValue(ctx => ({
        id: artifacts_tree_widget_1.ARTIFACTS_TREE_WIDGET_ID,
        createWidget: () => ctx.container.get(artifacts_tree_widget_1.ArtifactsTreeWidget)
    })).inSingletonScope();
    // View contribution
    (0, browser_1.bindViewContribution)(bind, artifacts_view_contribution_1.ArtifactsViewContribution);
    bind(browser_1.FrontendApplicationContribution).toService(artifacts_view_contribution_1.ArtifactsViewContribution);
    // Command contribution
    bind(artifact_commands_1.ArtifactCommandContribution).toSelf().inSingletonScope();
    bind(common_1.CommandContribution).toService(artifact_commands_1.ArtifactCommandContribution);
    // Menu contribution
    bind(artifact_menu_1.ArtifactMenuContribution).toSelf().inSingletonScope();
    bind(common_1.MenuContribution).toService(artifact_menu_1.ArtifactMenuContribution);
});


/***/ },

/***/ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\packages\\agentic-artifacts\\lib\\browser\\artifact-commands.js"
/*!**************************************************************************************************************************************!*\
  !*** C:\Users\Julian Wiley\Documents\GitHub\agentic_assistants\frontend\packages\agentic-artifacts\lib\browser\artifact-commands.js ***!
  \**************************************************************************************************************************************/
(__unused_webpack_module, exports, __webpack_require__) {


/**
 * Artifact Command Contribution
 *
 * Provides commands for artifact management.
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
```
