/**
 * Agentic Command Contribution
 * 
 * Provides command palette integration for Agentic functionality.
 */

import { injectable, inject } from '@theia/core/shared/inversify';
import { CommandContribution, CommandRegistry, Command } from '@theia/core/lib/common';
import { MessageService } from '@theia/core';
import { AgenticBackendService, AgenticBackendServiceSymbol } from './agentic-backend-service';
import { AgenticWebSocketClient, AgenticWebSocketClientSymbol } from './agentic-websocket-client';
import { TestingViewContribution } from './testing-view-contribution';

export namespace AgenticCommands {
    const AGENTIC_CATEGORY = 'Agentic';

    export const CHECK_CONNECTION: Command = {
        id: 'agentic.checkConnection',
        label: 'Check Backend Connection',
        category: AGENTIC_CATEGORY
    };

    export const SHOW_CONFIG: Command = {
        id: 'agentic.showConfig',
        label: 'Show Configuration',
        category: AGENTIC_CATEGORY
    };

    export const LIST_EXPERIMENTS: Command = {
        id: 'agentic.listExperiments',
        label: 'List Experiments',
        category: AGENTIC_CATEGORY
    };

    export const CREATE_EXPERIMENT: Command = {
        id: 'agentic.createExperiment',
        label: 'Create New Experiment',
        category: AGENTIC_CATEGORY
    };

    export const LIST_SESSIONS: Command = {
        id: 'agentic.listSessions',
        label: 'List Sessions',
        category: AGENTIC_CATEGORY
    };

    export const CREATE_SESSION: Command = {
        id: 'agentic.createSession',
        label: 'Create New Session',
        category: AGENTIC_CATEGORY
    };

    export const RECONNECT_WEBSOCKET: Command = {
        id: 'agentic.reconnectWebSocket',
        label: 'Reconnect WebSocket',
        category: AGENTIC_CATEGORY
    };

    export const OPEN_TESTING_VIEW: Command = {
        id: 'agentic.openTestingView',
        label: 'Open Testing Panel',
        category: AGENTIC_CATEGORY
    };

    export const RUN_TEST: Command = {
        id: 'agentic.runTest',
        label: 'Run Free-form Test',
        category: AGENTIC_CATEGORY
    };

    export const OPEN_TERMINAL: Command = {
        id: 'agentic.openTerminal',
        label: 'Open Terminal',
        category: AGENTIC_CATEGORY
    };

    export const OPEN_ASSISTANT_UI: Command = {
        id: 'agentic.openAssistantUi',
        label: 'Open Assistant UI',
        category: AGENTIC_CATEGORY
    };

    export const OPEN_AGENT_UI: Command = {
        id: 'agentic.openAgentUi',
        label: 'Open Agent UI',
        category: AGENTIC_CATEGORY
    };
}

@injectable()
export class AgenticCommandContribution implements CommandContribution {

    @inject(AgenticBackendServiceSymbol)
    protected readonly backendService: AgenticBackendService;

    @inject(AgenticWebSocketClientSymbol)
    protected readonly wsClient: AgenticWebSocketClient;

    @inject(MessageService)
    protected readonly messageService: MessageService;

    @inject(TestingViewContribution)
    protected readonly testingView: TestingViewContribution;

    protected commandRegistry?: CommandRegistry;

    registerCommands(registry: CommandRegistry): void {
        this.commandRegistry = registry;
        registry.registerCommand(AgenticCommands.CHECK_CONNECTION, {
            execute: async () => {
                const connected = await this.backendService.checkConnection();
                if (connected) {
                    this.messageService.info('Successfully connected to Agentic backend');
                } else {
                    this.messageService.error('Failed to connect to Agentic backend');
                }
            }
        });

        registry.registerCommand(AgenticCommands.SHOW_CONFIG, {
            execute: async () => {
                const response = await this.backendService.getConfig();
                if (response.data) {
                    console.log('Agentic Configuration:', response.data);
                    this.messageService.info('Configuration logged to console');
                } else {
                    this.messageService.error('Failed to fetch configuration: ' + response.error);
                }
            }
        });

        registry.registerCommand(AgenticCommands.LIST_EXPERIMENTS, {
            execute: async () => {
                const response = await this.backendService.listExperiments();
                if (response.data) {
                    console.log('Experiments:', response.data);
                    this.messageService.info('Experiments logged to console');
                } else {
                    this.messageService.error('Failed to list experiments: ' + response.error);
                }
            }
        });

        registry.registerCommand(AgenticCommands.CREATE_EXPERIMENT, {
            execute: async () => {
                const name = 'New Experiment ' + new Date().toISOString();
                const response = await this.backendService.createExperiment(name);
                if (response.data) {
                    this.messageService.info('Created experiment: ' + name);
                } else {
                    this.messageService.error('Failed to create experiment: ' + response.error);
                }
            }
        });

        registry.registerCommand(AgenticCommands.LIST_SESSIONS, {
            execute: async () => {
                const response = await this.backendService.listSessions();
                if (response.data) {
                    console.log('Sessions:', response.data);
                    this.messageService.info('Sessions logged to console');
                } else {
                    this.messageService.error('Failed to list sessions: ' + response.error);
                }
            }
        });

        registry.registerCommand(AgenticCommands.CREATE_SESSION, {
            execute: async () => {
                const name = 'New Session ' + new Date().toISOString();
                const response = await this.backendService.createSession(name);
                if (response.data) {
                    this.messageService.info('Created session: ' + name);
                } else {
                    this.messageService.error('Failed to create session: ' + response.error);
                }
            }
        });

        registry.registerCommand(AgenticCommands.RECONNECT_WEBSOCKET, {
            execute: async () => {
                try {
                    this.wsClient.disconnect();
                    await this.wsClient.connect();
                    this.messageService.info('WebSocket reconnected');
                } catch (error) {
                    this.messageService.error('Failed to reconnect WebSocket: ' + error);
                }
            }
        });

        registry.registerCommand(AgenticCommands.OPEN_TESTING_VIEW, {
            execute: async () => {
                await this.testingView.openView({ activate: true });
            }
        });

        registry.registerCommand(AgenticCommands.RUN_TEST, {
            execute: async () => {
                const code = window.prompt('Python code to run', 'result = 2 + 2');
                if (!code) {
                    return;
                }
                const response = await this.backendService.runTest({
                    code,
                    language: 'python'
                });
                if (response.data) {
                    this.messageService.info('Test run completed');
                } else {
                    this.messageService.error('Test run failed: ' + response.error);
                }
            }
        });

        registry.registerCommand(AgenticCommands.OPEN_TERMINAL, {
            execute: async () => {
                if (this.commandRegistry) {
                    this.commandRegistry.executeCommand('terminal:new');
                }
            }
        });

        registry.registerCommand(AgenticCommands.OPEN_ASSISTANT_UI, {
            execute: async () => {
                window.open('http://localhost:3000/assistant/chat', '_blank');
            }
        });

        registry.registerCommand(AgenticCommands.OPEN_AGENT_UI, {
            execute: async () => {
                window.open('http://localhost:3000/agents', '_blank');
            }
        });
    }
}

