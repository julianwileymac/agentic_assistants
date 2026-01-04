/**
 * Agentic Menu Contribution
 * 
 * Provides menu items for Agentic functionality.
 */

import { injectable } from '@theia/core/shared/inversify';
import { MenuContribution, MenuModelRegistry, MenuPath, MAIN_MENU_BAR } from '@theia/core/lib/common';
import { AgenticCommands } from './agentic-commands';

export namespace AgenticMenus {
    export const AGENTIC: MenuPath = [...MAIN_MENU_BAR, '7_agentic'];
    export const AGENTIC_EXPERIMENTS: MenuPath = [...AGENTIC, '1_experiments'];
    export const AGENTIC_SESSIONS: MenuPath = [...AGENTIC, '2_sessions'];
    export const AGENTIC_SYSTEM: MenuPath = [...AGENTIC, '3_system'];
}

@injectable()
export class AgenticMenuContribution implements MenuContribution {

    registerMenus(menus: MenuModelRegistry): void {
        // Register the main Agentic menu
        menus.registerSubmenu(AgenticMenus.AGENTIC, 'Agentic', {
            order: '7'
        });

        // Experiments submenu
        menus.registerSubmenu(AgenticMenus.AGENTIC_EXPERIMENTS, 'Experiments');
        
        menus.registerMenuAction(AgenticMenus.AGENTIC_EXPERIMENTS, {
            commandId: AgenticCommands.LIST_EXPERIMENTS.id,
            order: '1'
        });

        menus.registerMenuAction(AgenticMenus.AGENTIC_EXPERIMENTS, {
            commandId: AgenticCommands.CREATE_EXPERIMENT.id,
            order: '2'
        });

        // Sessions submenu
        menus.registerSubmenu(AgenticMenus.AGENTIC_SESSIONS, 'Sessions');

        menus.registerMenuAction(AgenticMenus.AGENTIC_SESSIONS, {
            commandId: AgenticCommands.LIST_SESSIONS.id,
            order: '1'
        });

        menus.registerMenuAction(AgenticMenus.AGENTIC_SESSIONS, {
            commandId: AgenticCommands.CREATE_SESSION.id,
            order: '2'
        });

        // System submenu
        menus.registerSubmenu(AgenticMenus.AGENTIC_SYSTEM, 'System');

        menus.registerMenuAction(AgenticMenus.AGENTIC_SYSTEM, {
            commandId: AgenticCommands.CHECK_CONNECTION.id,
            order: '1'
        });

        menus.registerMenuAction(AgenticMenus.AGENTIC_SYSTEM, {
            commandId: AgenticCommands.SHOW_CONFIG.id,
            order: '2'
        });

        menus.registerMenuAction(AgenticMenus.AGENTIC_SYSTEM, {
            commandId: AgenticCommands.RECONNECT_WEBSOCKET.id,
            order: '3'
        });
    }
}

