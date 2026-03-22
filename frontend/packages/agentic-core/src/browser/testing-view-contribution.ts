/**
 * Testing view contribution.
 */

import { injectable } from '@theia/core/shared/inversify';
import { AbstractViewContribution } from '@theia/core/lib/browser';

import { TestingWidget, TESTING_WIDGET_ID } from './testing-widget';

@injectable()
export class TestingViewContribution extends AbstractViewContribution<TestingWidget> {
    constructor() {
        super({
            widgetId: TESTING_WIDGET_ID,
            widgetName: TestingWidget.LABEL,
            defaultWidgetOptions: {
                area: 'left',
                rank: 250
            },
            toggleCommandId: 'agentic.openTestingView'
        });
    }

    async initializeLayout(): Promise<void> {
        await this.openView({ activate: false });
    }
}
