# Chunk: f05f3a8ab3ef_2

- source: `frontend/packages/agentic-core/lib/browser/agentic-commands.js`
- lines: 123-164
- chunk: 3/3

```
ute: async () => {
                const name = 'New Session ' + new Date().toISOString();
                const response = await this.backendService.createSession(name);
                if (response.data) {
                    this.messageService.info('Created session: ' + name);
                }
                else {
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
                }
                catch (error) {
                    this.messageService.error('Failed to reconnect WebSocket: ' + error);
                }
            }
        });
    }
};
__decorate([
    (0, inversify_1.inject)(agentic_backend_service_1.AgenticBackendServiceSymbol),
    __metadata("design:type", agentic_backend_service_1.AgenticBackendService)
], AgenticCommandContribution.prototype, "backendService", void 0);
__decorate([
    (0, inversify_1.inject)(agentic_websocket_client_1.AgenticWebSocketClientSymbol),
    __metadata("design:type", agentic_websocket_client_1.AgenticWebSocketClient)
], AgenticCommandContribution.prototype, "wsClient", void 0);
__decorate([
    (0, inversify_1.inject)(core_1.MessageService),
    __metadata("design:type", core_1.MessageService)
], AgenticCommandContribution.prototype, "messageService", void 0);
AgenticCommandContribution = __decorate([
    (0, inversify_1.injectable)()
], AgenticCommandContribution);
exports.AgenticCommandContribution = AgenticCommandContribution;
//# sourceMappingURL=agentic-commands.js.map
```
