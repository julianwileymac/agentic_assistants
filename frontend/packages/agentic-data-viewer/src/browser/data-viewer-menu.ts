/**
 * Data Viewer Menu Contribution
 * 
 * Provides menu items for data viewer commands.
 */

import { injectable } from '@theia/core/shared/inversify';
import { MenuContribution, MenuModelRegistry, MenuPath, MAIN_MENU_BAR } from '@theia/core/lib/common';
import { DataViewerCommands } from './data-viewer-commands';

export namespace DataViewerMenus {
    export const AGENTIC: MenuPath = [...MAIN_MENU_BAR, '7_agentic'];
    export const DATA: MenuPath = [...AGENTIC, '4_data'];
}

@injectable()
export class DataViewerMenuContribution implements MenuContribution {

    registerMenus(menus: MenuModelRegistry): void {
        // Register data submenu
        menus.registerSubmenu(DataViewerMenus.DATA, 'Data');

        menus.registerMenuAction(DataViewerMenus.DATA, {
            commandId: DataViewerCommands.REFRESH_FILES.id,
            order: '1'
        });

        menus.registerMenuAction(DataViewerMenus.DATA, {
            commandId: DataViewerCommands.NAVIGATE_TO.id,
            order: '2'
        });

        menus.registerMenuAction(DataViewerMenus.DATA, {
            commandId: DataViewerCommands.NAVIGATE_UP.id,
            order: '3'
        });

        menus.registerMenuAction(DataViewerMenus.DATA, {
            commandId: DataViewerCommands.PREVIEW_TABLE.id,
            order: '10'
        });

        menus.registerMenuAction(DataViewerMenus.DATA, {
            commandId: DataViewerCommands.VIEW_SCHEMA.id,
            order: '11'
        });

        menus.registerMenuAction(DataViewerMenus.DATA, {
            commandId: DataViewerCommands.QUERY_TABLE.id,
            order: '12'
        });

        menus.registerMenuAction(DataViewerMenus.DATA, {
            commandId: DataViewerCommands.CONVERT_FILE.id,
            order: '20'
        });

        menus.registerMenuAction(DataViewerMenus.DATA, {
            commandId: DataViewerCommands.VIEW_CACHE_STATS.id,
            order: '30'
        });

        menus.registerMenuAction(DataViewerMenus.DATA, {
            commandId: DataViewerCommands.CLEAR_CACHE.id,
            order: '31'
        });
    }
}

