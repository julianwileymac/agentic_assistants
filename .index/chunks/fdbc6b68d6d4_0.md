# Chunk: fdbc6b68d6d4_0

- source: `frontend/packages/agentic-core/lib/browser/agentic-status-bar.d.ts`
- lines: 1-17
- chunk: 1/1

```
/**
 * Agentic Status Bar Contribution
 *
 * Provides status bar items showing connection status.
 */
import { FrontendApplicationContribution, StatusBar } from '@theia/core/lib/browser';
import { AgenticBackendService } from './agentic-backend-service';
import { AgenticWebSocketClient } from './agentic-websocket-client';
export declare class AgenticStatusBarContribution implements FrontendApplicationContribution {
    protected readonly backendService: AgenticBackendService;
    protected readonly wsClient: AgenticWebSocketClient;
    protected readonly statusBar: StatusBar;
    protected init(): void;
    onStart(): Promise<void>;
    protected updateStatusBar(): void;
}
//# sourceMappingURL=agentic-status-bar.d.ts.map
```
