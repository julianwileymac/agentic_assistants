/**
 * Data Explorer View Contribution
 * 
 * Registers the data explorer widget in the bottom panel.
 */

import { injectable } from '@theia/core/shared/inversify';
import { AbstractViewContribution } from '@theia/core/lib/browser';
import { DataExplorerWidget, DATA_EXPLORER_WIDGET_ID } from './data-explorer-widget';
import { DataViewerCommands } from './data-viewer-commands';

@injectable()
export class DataExplorerViewContribution extends AbstractViewContribution<DataExplorerWidget> {

    constructor() {
        super({
            widgetId: DATA_EXPLORER_WIDGET_ID,
            widgetName: DataExplorerWidget.LABEL,
            defaultWidgetOptions: {
                area: 'bottom',
                rank: 100
            },
            toggleCommandId: DataViewerCommands.TOGGLE_DATA_EXPLORER.id
        });
    }

    async initializeLayout(): Promise<void> {
        await this.openView({ activate: false });
    }
}

