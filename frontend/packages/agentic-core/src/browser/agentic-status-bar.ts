/**
 * Agentic Status Bar Contribution
 * 
 * Provides status bar items showing connection status.
 */

import { injectable, inject, postConstruct } from '@theia/core/shared/inversify';
import { FrontendApplicationContribution, StatusBar, StatusBarAlignment } from '@theia/core/lib/browser';
import { AgenticBackendService, AgenticBackendServiceSymbol } from './agentic-backend-service';
import { AgenticWebSocketClient, AgenticWebSocketClientSymbol } from './agentic-websocket-client';
import { AgenticCommands } from './agentic-commands';

const AGENTIC_STATUS_BAR_ID = 'agentic-connection-status';

@injectable()
export class AgenticStatusBarContribution implements FrontendApplicationContribution {

    @inject(AgenticBackendServiceSymbol)
    protected readonly backendService: AgenticBackendService;

    @inject(AgenticWebSocketClientSymbol)
    protected readonly wsClient: AgenticWebSocketClient;

    @inject(StatusBar)
    protected readonly statusBar: StatusBar;

    @postConstruct()
    protected init(): void {
        // Listen for connection changes
        this.backendService.onConnectionChanged(connected => {
            this.updateStatusBar();
        });

        this.wsClient.onConnected(() => {
            this.updateStatusBar();
        });

        this.wsClient.onDisconnected(() => {
            this.updateStatusBar();
        });
    }

    async onStart(): Promise<void> {
        this.updateStatusBar();
    }

    protected updateStatusBar(): void {
        const backendConnected = this.backendService.isConnected();
        const wsConnected = this.wsClient.isConnected();

        let text: string;
        let tooltip: string;
        let backgroundColor: string | undefined;

        if (backendConnected && wsConnected) {
            text = '$(check) Agentic';
            tooltip = 'Connected to Agentic backend (REST + WebSocket)';
            backgroundColor = undefined;
        } else if (backendConnected) {
            text = '$(warning) Agentic';
            tooltip = 'Connected to Agentic backend (REST only, WebSocket disconnected)';
            backgroundColor = 'var(--theia-statusBarItem-warningBackground)';
        } else {
            text = '$(error) Agentic';
            tooltip = 'Disconnected from Agentic backend';
            backgroundColor = 'var(--theia-statusBarItem-errorBackground)';
        }

        this.statusBar.setElement(AGENTIC_STATUS_BAR_ID, {
            text,
            tooltip,
            alignment: StatusBarAlignment.LEFT,
            priority: 100,
            command: AgenticCommands.CHECK_CONNECTION.id,
            backgroundColor
        });
    }
}

