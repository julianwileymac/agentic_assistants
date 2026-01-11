# Chunk: be3ca549b6ac_2

- source: `frontend/packages/agentic-core/lib/browser/agentic-websocket-client.js`
- lines: 131-220
- chunk: 3/4

```
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
        this.socket.send(JSON.stringify(command));
    }
    /**
     * Subscribe to a topic
     */
    subscribe(topic) {
        this.subscriptions.add(topic);
        if (this.isConnected()) {
            this.send({
                command: 'subscribe',
                params: { topic }
            });
        }
    }
    /**
     * Unsubscribe from a topic
     */
    unsubscribe(topic) {
        this.subscriptions.delete(topic);
        if (this.isConnected()) {
            this.send({
                command: 'unsubscribe',
                params: { topic }
            });
        }
    }
    /**
     * Handle incoming messages
     */
    handleMessage(data) {
        try {
            const message = JSON.parse(data);
            this.onMessageEmitter.fire(message);
            // Route to specific emitters based on event type
            switch (message.type) {
                case EventType.CONNECTED:
                    this.connectionId = message.data.connection_id;
                    this.onConnectedEmitter.fire(this.connectionId);
                    // Re-subscribe to topics after reconnect
                    this.resubscribe();
                    break;
                case EventType.EXPERIMENT_CREATED:
                case EventType.EXPERIMENT_UPDATED:
                case EventType.EXPERIMENT_DELETED:
                case EventType.RUN_STARTED:
                case EventType.RUN_ENDED:
                case EventType.METRICS_LOGGED:
                    this.onExperimentEventEmitter.fire(message);
                    break;
                case EventType.RUN_LOG:
                    this.onRunLogEmitter.fire(message);
                    break;
                case EventType.ARTIFACT_CREATED:
                case EventType.ARTIFACT_UPDATED:
                case EventType.ARTIFACT_DELETED:
                case EventType.ARTIFACT_SHARED:
                    this.onArtifactEventEmitter.fire(message);
                    break;
                case EventType.SESSION_CREATED:
                case EventType.SESSION_ACTIVATED:
                case EventType.SESSION_DELETED:
                    this.onSessionEventEmitter.fire(message);
                    break;
                case EventType.NOTIFICATION:
                case EventType.ERROR:
                    this.onNotificationEmitter.fire(message);
                    break;
            }
        }
        catch (error) {
            console.error('Failed to parse WebSocket message:', error);
        }
    }
    /**
     * Re-subscribe to all topics after reconnect
     */
    resubscribe() {
        for (const topic of this.subscriptions) {
            this.send({
```
