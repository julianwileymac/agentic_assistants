/**
 * Artifacts View Contribution
 * 
 * Registers the artifacts tree view in the left panel.
 */

import { injectable } from '@theia/core/shared/inversify';
import { AbstractViewContribution } from '@theia/core/lib/browser';
import { ArtifactsTreeWidget, ARTIFACTS_TREE_WIDGET_ID } from './artifacts-tree-widget';
import { ArtifactCommands } from './artifact-commands';

@injectable()
export class ArtifactsViewContribution extends AbstractViewContribution<ArtifactsTreeWidget> {

    constructor() {
        super({
            widgetId: ARTIFACTS_TREE_WIDGET_ID,
            widgetName: ArtifactsTreeWidget.LABEL,
            defaultWidgetOptions: {
                area: 'left',
                rank: 300
            },
            toggleCommandId: ArtifactCommands.TOGGLE_ARTIFACTS_VIEW.id
        });
    }

    async initializeLayout(): Promise<void> {
        await this.openView({ activate: false });
    }
}

