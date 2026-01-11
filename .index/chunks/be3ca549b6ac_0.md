# Chunk: be3ca549b6ac_0

- source: `frontend/packages/agentic-core/lib/browser/agentic-websocket-client.js`
- lines: 1-61
- chunk: 1/4

```
"use strict";
/**
 * Agentic WebSocket Client
 *
 * Provides real-time event streaming from the Python backend.
 */
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.AgenticWebSocketClient = exports.EventType = exports.AgenticWebSocketClientSymbol = void 0;
const inversify_1 = require("@theia/core/shared/inversify");
const common_1 = require("@theia/core/lib/common");
exports.AgenticWebSocketClientSymbol = Symbol('AgenticWebSocketClient');
var EventType;
(function (EventType) {
    // Connection events
    EventType["CONNECTED"] = "connected";
    EventType["DISCONNECTED"] = "disconnected";
    EventType["PING"] = "ping";
    EventType["PONG"] = "pong";
    // Experiment events
    EventType["EXPERIMENT_CREATED"] = "experiment.created";
    EventType["EXPERIMENT_UPDATED"] = "experiment.updated";
    EventType["EXPERIMENT_DELETED"] = "experiment.deleted";
    EventType["RUN_STARTED"] = "run.started";
    EventType["RUN_ENDED"] = "run.ended";
    EventType["RUN_LOG"] = "run.log";
    EventType["METRICS_LOGGED"] = "metrics.logged";
    // Artifact events
    EventType["ARTIFACT_CREATED"] = "artifact.created";
    EventType["ARTIFACT_UPDATED"] = "artifact.updated";
    EventType["ARTIFACT_DELETED"] = "artifact.deleted";
    EventType["ARTIFACT_SHARED"] = "artifact.shared";
    // Session events
    EventType["SESSION_CREATED"] = "session.created";
    EventType["SESSION_ACTIVATED"] = "session.activated";
    EventType["SESSION_DELETED"] = "session.deleted";
    // System events
    EventType["CONFIG_CHANGED"] = "config.changed";
    EventType["ERROR"] = "error";
    EventType["NOTIFICATION"] = "notification";
})(EventType = exports.EventType || (exports.EventType = {}));
let AgenticWebSocketClient = class AgenticWebSocketClient {
    constructor() {
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        this.subscriptions = new Set();
        this.wsUrl = 'ws://localhost:8080/ws';
        this.onConnectedEmitter = new common_1.Emitter();
        this.onConnected = this.onConnectedEmitter.event;
        this.onDisconnectedEmitter = new common_1.Emitter();
        this.onDisconnected = this.onDisconnectedEmitter.event;
        this.onMessageEmitter = new common_1.Emitter();
        this.onMessage = this.onMessageEmitter.event;
        this.onErrorEmitter = new common_1.Emitter();
```
