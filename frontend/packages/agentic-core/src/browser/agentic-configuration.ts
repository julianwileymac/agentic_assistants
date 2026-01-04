/**
 * Agentic Configuration Contribution
 * 
 * Provides preference bindings for IDE settings.
 */

import { injectable, inject } from '@theia/core/shared/inversify';
import { FrontendApplicationContribution, FrontendApplication } from '@theia/core/lib/browser';
import { AgenticBackendService, AgenticBackendServiceSymbol } from './agentic-backend-service';
import { AgenticWebSocketClient, AgenticWebSocketClientSymbol } from './agentic-websocket-client';

@injectable()
export class AgenticConfigurationContribution implements FrontendApplicationContribution {

    @inject(AgenticBackendServiceSymbol)
    protected readonly backendService: AgenticBackendService;

    @inject(AgenticWebSocketClientSymbol)
    protected readonly wsClient: AgenticWebSocketClient;

    protected initializationPromise: Promise<void> | undefined;

    async onStart(_app: FrontendApplication): Promise<void> {
        this.initializationPromise = this.doInitialize();
        await this.initializationPromise;
    }

    protected async doInitialize(): Promise<void> {
        // Load configuration from environment or defaults
        const backendUrl = this.getBackendUrl();
        const wsUrl = this.getWebSocketUrl();

        // Configure services
        this.backendService.configure({ backendUrl });
        this.wsClient.configure(wsUrl);

        // Check backend connection
        const connected = await this.backendService.checkConnection();
        if (connected) {
            console.log('Connected to Agentic backend at', backendUrl);
            
            // Connect WebSocket
            try {
                await this.wsClient.connect();
                console.log('WebSocket connected');
                
                // Subscribe to default topics
                this.wsClient.subscribe('experiments');
                this.wsClient.subscribe('artifacts');
                this.wsClient.subscribe('sessions');
            } catch (error) {
                console.warn('WebSocket connection failed:', error);
            }
        } else {
            console.warn('Failed to connect to Agentic backend at', backendUrl);
        }
    }

    protected getBackendUrl(): string {
        // Check for environment variable or use default
        if (typeof window !== 'undefined') {
            const urlParams = new URLSearchParams(window.location.search);
            const backendUrl = urlParams.get('backendUrl');
            if (backendUrl) {
                return backendUrl;
            }
        }
        return 'http://localhost:8080';
    }

    protected getWebSocketUrl(): string {
        const backendUrl = this.getBackendUrl();
        return backendUrl.replace(/^http/, 'ws') + '/ws';
    }

    /**
     * Wait for initialization to complete
     */
    async waitForInitialization(): Promise<void> {
        if (this.initializationPromise) {
            await this.initializationPromise;
        }
    }
}

