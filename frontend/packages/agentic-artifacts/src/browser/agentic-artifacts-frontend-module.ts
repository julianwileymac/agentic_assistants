/**
 * Agentic Artifacts Frontend Module
 * 
 * Provides artifact management with tagging and grouping for the Agentic IDE.
 */

import { ContainerModule } from '@theia/core/shared/inversify';
import { FrontendApplicationContribution, WidgetFactory, bindViewContribution } from '@theia/core/lib/browser';
import { CommandContribution, MenuContribution } from '@theia/core/lib/common';
import { ArtifactService, ArtifactServiceSymbol } from './artifact-service';
import { ArtifactsTreeWidget, ARTIFACTS_TREE_WIDGET_ID } from './artifacts-tree-widget';
import { ArtifactsViewContribution } from './artifacts-view-contribution';
import { ArtifactCommandContribution } from './artifact-commands';
import { ArtifactMenuContribution } from './artifact-menu';

export default new ContainerModule(bind => {
    // Artifact service
    bind(ArtifactService).toSelf().inSingletonScope();
    bind(ArtifactServiceSymbol).toService(ArtifactService);

    // Artifacts tree widget
    bind(ArtifactsTreeWidget).toSelf();
    bind(WidgetFactory).toDynamicValue(ctx => ({
        id: ARTIFACTS_TREE_WIDGET_ID,
        createWidget: () => ctx.container.get(ArtifactsTreeWidget)
    })).inSingletonScope();

    // View contribution
    bindViewContribution(bind, ArtifactsViewContribution);
    bind(FrontendApplicationContribution).toService(ArtifactsViewContribution);

    // Command contribution
    bind(ArtifactCommandContribution).toSelf().inSingletonScope();
    bind(CommandContribution).toService(ArtifactCommandContribution);

    // Menu contribution
    bind(ArtifactMenuContribution).toSelf().inSingletonScope();
    bind(MenuContribution).toService(ArtifactMenuContribution);
});

