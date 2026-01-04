/**
 * Agentic MLFlow Frontend Module
 * 
 * Provides MLFlow experiment tracking integration for the Agentic IDE.
 */

import { ContainerModule } from '@theia/core/shared/inversify';
import { FrontendApplicationContribution, WidgetFactory, bindViewContribution } from '@theia/core/lib/browser';
import { CommandContribution, MenuContribution } from '@theia/core/lib/common';
import { MLFlowService, MLFlowServiceSymbol } from './mlflow-service';
import { ExperimentsTreeWidget, EXPERIMENTS_TREE_WIDGET_ID } from './experiments-tree-widget';
import { ExperimentsViewContribution } from './experiments-view-contribution';
import { MLFlowCommandContribution } from './mlflow-commands';
import { MLFlowMenuContribution } from './mlflow-menu';

export default new ContainerModule(bind => {
    // MLFlow service
    bind(MLFlowService).toSelf().inSingletonScope();
    bind(MLFlowServiceSymbol).toService(MLFlowService);

    // Experiments tree widget
    bind(ExperimentsTreeWidget).toSelf();
    bind(WidgetFactory).toDynamicValue(ctx => ({
        id: EXPERIMENTS_TREE_WIDGET_ID,
        createWidget: () => ctx.container.get(ExperimentsTreeWidget)
    })).inSingletonScope();

    // View contribution
    bindViewContribution(bind, ExperimentsViewContribution);
    bind(FrontendApplicationContribution).toService(ExperimentsViewContribution);

    // Command contribution
    bind(MLFlowCommandContribution).toSelf().inSingletonScope();
    bind(CommandContribution).toService(MLFlowCommandContribution);

    // Menu contribution
    bind(MLFlowMenuContribution).toSelf().inSingletonScope();
    bind(MenuContribution).toService(MLFlowMenuContribution);
});

