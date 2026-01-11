# Chunk: f05f3a8ab3ef_0

- source: `frontend/packages/agentic-core/lib/browser/agentic-commands.js`
- lines: 1-70
- chunk: 1/3

```
"use strict";
/**
 * Agentic Command Contribution
 *
 * Provides command palette integration for Agentic functionality.
 */
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.AgenticCommandContribution = exports.AgenticCommands = void 0;
const inversify_1 = require("@theia/core/shared/inversify");
const core_1 = require("@theia/core");
const agentic_backend_service_1 = require("./agentic-backend-service");
const agentic_websocket_client_1 = require("./agentic-websocket-client");
var AgenticCommands;
(function (AgenticCommands) {
    const AGENTIC_CATEGORY = 'Agentic';
    AgenticCommands.CHECK_CONNECTION = {
        id: 'agentic.checkConnection',
        label: 'Check Backend Connection',
        category: AGENTIC_CATEGORY
    };
    AgenticCommands.SHOW_CONFIG = {
        id: 'agentic.showConfig',
        label: 'Show Configuration',
        category: AGENTIC_CATEGORY
    };
    AgenticCommands.LIST_EXPERIMENTS = {
        id: 'agentic.listExperiments',
        label: 'List Experiments',
        category: AGENTIC_CATEGORY
    };
    AgenticCommands.CREATE_EXPERIMENT = {
        id: 'agentic.createExperiment',
        label: 'Create New Experiment',
        category: AGENTIC_CATEGORY
    };
    AgenticCommands.LIST_SESSIONS = {
        id: 'agentic.listSessions',
        label: 'List Sessions',
        category: AGENTIC_CATEGORY
    };
    AgenticCommands.CREATE_SESSION = {
        id: 'agentic.createSession',
        label: 'Create New Session',
        category: AGENTIC_CATEGORY
    };
    AgenticCommands.RECONNECT_WEBSOCKET = {
        id: 'agentic.reconnectWebSocket',
        label: 'Reconnect WebSocket',
        category: AGENTIC_CATEGORY
    };
})(AgenticCommands = exports.AgenticCommands || (exports.AgenticCommands = {}));
let AgenticCommandContribution = class AgenticCommandContribution {
    registerCommands(registry) {
        registry.registerCommand(AgenticCommands.CHECK_CONNECTION, {
            execute: async () => {
                const connected = await this.backendService.checkConnection();
                if (connected) {
                    this.messageService.info('Successfully connected to Agentic backend');
                }
                else {
```
