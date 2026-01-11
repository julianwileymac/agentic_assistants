# Chunk: be3ca549b6ac_1

- source: `frontend/packages/agentic-core/lib/browser/agentic-websocket-client.js`
- lines: 55-141
- chunk: 2/4

```
ter.event;
        this.onDisconnectedEmitter = new common_1.Emitter();
        this.onDisconnected = this.onDisconnectedEmitter.event;
        this.onMessageEmitter = new common_1.Emitter();
        this.onMessage = this.onMessageEmitter.event;
        this.onErrorEmitter = new common_1.Emitter();
        this.onError = this.onErrorEmitter.event;
        // Event-specific emitters
        this.onExperimentEventEmitter = new common_1.Emitter();
        this.onExperimentEvent = this.onExperimentEventEmitter.event;
        this.onArtifactEventEmitter = new common_1.Emitter();
        this.onArtifactEvent = this.onArtifactEventEmitter.event;
        this.onSessionEventEmitter = new common_1.Emitter();
        this.onSessionEvent = this.onSessionEventEmitter.event;
        this.onRunLogEmitter = new common_1.Emitter();
        this.onRunLog = this.onRunLogEmitter.event;
        this.onNotificationEmitter = new common_1.Emitter();
        this.onNotification = this.onNotificationEmitter.event;
    }
    /**
     * Configure the WebSocket URL
     */
    configure(url) {
        this.wsUrl = url;
    }
    /**
     * Connect to the WebSocket server
     */
    async connect(clientId) {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            return;
        }
        const url = clientId ? `${this.wsUrl}/${clientId}` : this.wsUrl;
        return new Promise((resolve, reject) => {
            try {
                this.socket = new WebSocket(url);
                this.socket.onopen = () => {
                    this.reconnectAttempts = 0;
                    this.startPing();
                    resolve();
                };
                this.socket.onmessage = (event) => {
                    this.handleMessage(event.data);
                };
                this.socket.onerror = (event) => {
                    const error = new Error('WebSocket error');
                    this.onErrorEmitter.fire(error);
                    reject(error);
                };
                this.socket.onclose = () => {
                    this.stopPing();
                    this.onDisconnectedEmitter.fire();
                    this.attemptReconnect();
                };
            }
            catch (error) {
                reject(error);
            }
        });
    }
    /**
     * Disconnect from the WebSocket server
     */
    disconnect() {
        this.stopPing();
        if (this.socket) {
            this.socket.close();
            this.socket = undefined;
        }
        this.connectionId = undefined;
        this.subscriptions.clear();
    }
    /**
     * Check if connected
     */
    isConnected() {
        var _a;
        return ((_a = this.socket) === null || _a === void 0 ? void 0 : _a.readyState) === WebSocket.OPEN;
    }
    /**
     * Send a command to the server
     */
    send(command) {
        if (!this.isConnected()) {
            throw new Error('WebSocket is not connected');
        }
```
