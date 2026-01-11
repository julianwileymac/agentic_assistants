# Chunk: 2cc5aaa31d1c_0

- source: `frontend/packages/agentic-artifacts/lib/browser/agentic-artifacts-frontend-module.js`
- lines: 1-36
- chunk: 1/1

```
"use strict";
/**
 * Agentic Artifacts Frontend Module
 *
 * Provides artifact management with tagging and grouping for the Agentic IDE.
 */
Object.defineProperty(exports, "__esModule", { value: true });
const inversify_1 = require("@theia/core/shared/inversify");
const browser_1 = require("@theia/core/lib/browser");
const common_1 = require("@theia/core/lib/common");
const artifact_service_1 = require("./artifact-service");
const artifacts_tree_widget_1 = require("./artifacts-tree-widget");
const artifacts_view_contribution_1 = require("./artifacts-view-contribution");
const artifact_commands_1 = require("./artifact-commands");
const artifact_menu_1 = require("./artifact-menu");
exports.default = new inversify_1.ContainerModule(bind => {
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
//# sourceMappingURL=agentic-artifacts-frontend-module.js.map
```
