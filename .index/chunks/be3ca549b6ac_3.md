# Chunk: be3ca549b6ac_3

- source: `frontend/packages/agentic-core/lib/browser/agentic-websocket-client.js`
- lines: 207-281
- chunk: 4/4

```
ak;
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
                command: 'subscribe',
                params: { topic }
            });
        }
    }
    /**
     * Start ping interval
     */
    startPing() {
        this.pingInterval = setInterval(() => {
            if (this.isConnected()) {
                this.send({ command: 'ping', params: {} });
            }
        }, 30000); // Ping every 30 seconds
    }
    /**
     * Stop ping interval
     */
    stopPing() {
        if (this.pingInterval) {
            clearInterval(this.pingInterval);
            this.pingInterval = undefined;
        }
    }
    /**
     * Attempt to reconnect after disconnect
     */
    attemptReconnect() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.error('Max reconnect attempts reached');
            return;
        }
        this.reconnectAttempts++;
        const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
        setTimeout(() => {
            console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
            this.connect(this.connectionId).catch(() => {
                // Will trigger another reconnect attempt via onclose
            });
        }, delay);
    }
    /**
     * Dispose resources
     */
    dispose() {
        this.disconnect();
        this.onConnectedEmitter.dispose();
        this.onDisconnectedEmitter.dispose();
        this.onMessageEmitter.dispose();
        this.onErrorEmitter.dispose();
        this.onExperimentEventEmitter.dispose();
        this.onArtifactEventEmitter.dispose();
        this.onSessionEventEmitter.dispose();
        this.onRunLogEmitter.dispose();
        this.onNotificationEmitter.dispose();
    }
};
AgenticWebSocketClient = __decorate([
    (0, inversify_1.injectable)()
], AgenticWebSocketClient);
exports.AgenticWebSocketClient = AgenticWebSocketClient;
//# sourceMappingURL=agentic-websocket-client.js.map
```
