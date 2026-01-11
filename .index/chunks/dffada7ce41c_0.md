# Chunk: dffada7ce41c_0

- source: `frontend/packages/agentic-artifacts/lib/browser/artifact-service.js`
- lines: 1-64
- chunk: 1/3

```
"use strict";
/**
 * Artifact Service
 *
 * Provides artifact management functionality with tagging and grouping.
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
exports.ArtifactService = exports.ArtifactServiceSymbol = void 0;
const inversify_1 = require("@theia/core/shared/inversify");
const common_1 = require("@theia/core/lib/common");
const browser_1 = require("agentic-core/lib/browser");
exports.ArtifactServiceSymbol = Symbol('ArtifactService');
let ArtifactService = class ArtifactService {
    constructor() {
        this.artifacts = [];
        this.groups = [];
        this.tags = [];
        this.onArtifactsChangedEmitter = new common_1.Emitter();
        this.onArtifactsChanged = this.onArtifactsChangedEmitter.event;
        this.onGroupsChangedEmitter = new common_1.Emitter();
        this.onGroupsChanged = this.onGroupsChangedEmitter.event;
        this.onTagsChangedEmitter = new common_1.Emitter();
        this.onTagsChanged = this.onTagsChangedEmitter.event;
        // Will be initialized after injection
    }
    initialize() {
        // Listen for WebSocket events
        this.wsClient.onArtifactEvent(message => {
            this.handleArtifactEvent(message);
        });
    }
    handleArtifactEvent(message) {
        switch (message.type) {
            case 'artifact.created':
            case 'artifact.updated':
            case 'artifact.deleted':
            case 'artifact.shared':
                this.refreshArtifacts();
                break;
        }
    }
    /**
     * List all artifacts with optional filtering
     */
    async listArtifacts(params) {
        const queryParams = {};
        if (params === null || params === void 0 ? void 0 : params.tags)
            queryParams.tags = params.tags.join(',');
        if (params === null || params === void 0 ? void 0 : params.groups)
            queryParams.groups = params.groups.join(',');
        if (params === null || params === void 0 ? void 0 : params.sessionId)
            queryParams.session_id = params.sessionId;
        if (params === null || params === void 0 ? void 0 : params.experimentId)
            queryParams.experiment_id = params.experimentId;
```
