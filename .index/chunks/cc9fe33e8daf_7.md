# Chunk: cc9fe33e8daf_7

- source: `frontend/browser-app/lib/frontend/C_Users_Julian_Wiley_Documents_GitHub_agentic_assistants_frontend_packages_agentic-artifacts_-341fb0.js`
- lines: 358-408
- chunk: 8/19

```
ontend\packages\agentic-artifacts\lib\browser\artifact-menu.js ***!
  \**********************************************************************************************************************************/
(__unused_webpack_module, exports, __webpack_require__) {


/**
 * Artifact Menu Contribution
 *
 * Provides menu items for artifact commands.
 */
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
Object.defineProperty(exports, "__esModule", ({ value: true }));
exports.ArtifactMenuContribution = exports.ArtifactMenus = void 0;
const inversify_1 = __webpack_require__(/*! @theia/core/shared/inversify */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\core\\shared\\inversify\\index.js");
const common_1 = __webpack_require__(/*! @theia/core/lib/common */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\core\\lib\\common\\index.js");
const artifact_commands_1 = __webpack_require__(/*! ./artifact-commands */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\packages\\agentic-artifacts\\lib\\browser\\artifact-commands.js");
var ArtifactMenus;
(function (ArtifactMenus) {
    ArtifactMenus.AGENTIC = [...common_1.MAIN_MENU_BAR, '7_agentic'];
    ArtifactMenus.ARTIFACTS = [...ArtifactMenus.AGENTIC, '2_artifacts'];
})(ArtifactMenus = exports.ArtifactMenus || (exports.ArtifactMenus = {}));
let ArtifactMenuContribution = class ArtifactMenuContribution {
    registerMenus(menus) {
        // Register artifacts submenu
        menus.registerSubmenu(ArtifactMenus.ARTIFACTS, 'Artifacts');
        menus.registerMenuAction(ArtifactMenus.ARTIFACTS, {
            commandId: artifact_commands_1.ArtifactCommands.REFRESH_ARTIFACTS.id,
            order: '1'
        });
        menus.registerMenuAction(ArtifactMenus.ARTIFACTS, {
            commandId: artifact_commands_1.ArtifactCommands.VIEW_ALL.id,
            order: '2'
        });
        menus.registerMenuAction(ArtifactMenus.ARTIFACTS, {
            commandId: artifact_commands_1.ArtifactCommands.VIEW_BY_GROUP.id,
            order: '3'
        });
        menus.registerMenuAction(ArtifactMenus.ARTIFACTS, {
            commandId: artifact_commands_1.ArtifactCommands.VIEW_BY_TAG.id,
            order: '4'
        });
        menus.registerMenuAction(ArtifactMenus.ARTIFACTS, {
            commandId: artifact_commands_1.ArtifactCommands.VIEW_SHARED.id,
            order: '5'
        });
```
