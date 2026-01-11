# Chunk: cc9fe33e8daf_0

- source: `frontend/browser-app/lib/frontend/C_Users_Julian_Wiley_Documents_GitHub_agentic_assistants_frontend_packages_agentic-artifacts_-341fb0.js`
- lines: 1-28
- chunk: 1/19

```
"use strict";
(self["webpackChunkbrowser_app"] = self["webpackChunkbrowser_app"] || []).push([["C_Users_Julian_Wiley_Documents_GitHub_agentic_assistants_frontend_packages_agentic-artifacts_-341fb0"],{

/***/ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\packages\\agentic-artifacts\\lib\\browser\\agentic-artifacts-frontend-module.js"
/*!******************************************************************************************************************************************************!*\
  !*** C:\Users\Julian Wiley\Documents\GitHub\agentic_assistants\frontend\packages\agentic-artifacts\lib\browser\agentic-artifacts-frontend-module.js ***!
  \******************************************************************************************************************************************************/
(__unused_webpack_module, exports, __webpack_require__) {


/**
 * Agentic Artifacts Frontend Module
 *
 * Provides artifact management with tagging and grouping for the Agentic IDE.
 */
Object.defineProperty(exports, "__esModule", ({ value: true }));
const inversify_1 = __webpack_require__(/*! @theia/core/shared/inversify */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\core\\shared\\inversify\\index.js");
const browser_1 = __webpack_require__(/*! @theia/core/lib/browser */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\core\\lib\\browser\\index.js");
const common_1 = __webpack_require__(/*! @theia/core/lib/common */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\core\\lib\\common\\index.js");
const artifact_service_1 = __webpack_require__(/*! ./artifact-service */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\packages\\agentic-artifacts\\lib\\browser\\artifact-service.js");
const artifacts_tree_widget_1 = __webpack_require__(/*! ./artifacts-tree-widget */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\packages\\agentic-artifacts\\lib\\browser\\artifacts-tree-widget.js");
const artifacts_view_contribution_1 = __webpack_require__(/*! ./artifacts-view-contribution */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\packages\\agentic-artifacts\\lib\\browser\\artifacts-view-contribution.js");
const artifact_commands_1 = __webpack_require__(/*! ./artifact-commands */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\packages\\agentic-artifacts\\lib\\browser\\artifact-commands.js");
const artifact_menu_1 = __webpack_require__(/*! ./artifact-menu */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\packages\\agentic-artifacts\\lib\\browser\\artifact-menu.js");
exports["default"] = new inversify_1.ContainerModule(bind => {
    // Artifact service
    bind(artifact_service_1.ArtifactService).toSelf().inSingletonScope();
```
