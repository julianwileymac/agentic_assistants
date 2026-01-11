# Chunk: cc9fe33e8daf_9

- source: `frontend/browser-app/lib/frontend/C_Users_Julian_Wiley_Documents_GitHub_agentic_assistants_frontend_packages_agentic-artifacts_-341fb0.js`
- lines: 456-512
- chunk: 10/19

```
tadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};
Object.defineProperty(exports, "__esModule", ({ value: true }));
exports.ArtifactService = exports.ArtifactServiceSymbol = void 0;
const inversify_1 = __webpack_require__(/*! @theia/core/shared/inversify */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\core\\shared\\inversify\\index.js");
const common_1 = __webpack_require__(/*! @theia/core/lib/common */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\core\\lib\\common\\index.js");
const browser_1 = __webpack_require__(/*! agentic-core/lib/browser */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\packages\\agentic-core\\lib\\browser\\index.js");
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
        if (params === null || params === void 0 ? void 0 : params.sharedOnly)
            queryParams.shared_only = 'true';
        const response = await this.backendService.get('/artifacts', queryParams);
        if (response.data) {
            this.artifacts = response.data.artifacts;
```
