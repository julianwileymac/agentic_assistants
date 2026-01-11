# Chunk: cc9fe33e8daf_11

- source: `frontend/browser-app/lib/frontend/C_Users_Julian_Wiley_Documents_GitHub_agentic_assistants_frontend_packages_agentic-artifacts_-341fb0.js`
- lines: 592-685
- chunk: 12/19

```
urn [];
    }
    /**
     * Refresh groups from server
     */
    async refreshGroups() {
        await this.listGroups();
    }
    /**
     * List all tags
     */
    async listTags() {
        const response = await this.backendService.get('/artifacts/tags/list');
        if (response.data) {
            this.tags = response.data;
            this.onTagsChangedEmitter.fire(this.tags);
            return this.tags;
        }
        return [];
    }
    /**
     * Refresh tags from server
     */
    async refreshTags() {
        await this.listTags();
    }
    /**
     * List shared artifacts
     */
    async listSharedArtifacts() {
        const response = await this.backendService.get('/artifacts/shared/list');
        if (response.data) {
            return response.data.artifacts;
        }
        return [];
    }
    /**
     * Get cached artifacts
     */
    getArtifacts() {
        return this.artifacts;
    }
    /**
     * Get cached groups
     */
    getGroups() {
        return this.groups;
    }
    /**
     * Get cached tags
     */
    getTags() {
        return this.tags;
    }
    /**
     * Get download URL for an artifact
     */
    getDownloadUrl(artifactId) {
        return `http://localhost:8080/api/v1/artifacts/${artifactId}/download`;
    }
};
__decorate([
    (0, inversify_1.inject)(browser_1.AgenticBackendServiceSymbol),
    __metadata("design:type", browser_1.AgenticBackendService)
], ArtifactService.prototype, "backendService", void 0);
__decorate([
    (0, inversify_1.inject)(browser_1.AgenticWebSocketClientSymbol),
    __metadata("design:type", browser_1.AgenticWebSocketClient)
], ArtifactService.prototype, "wsClient", void 0);
ArtifactService = __decorate([
    (0, inversify_1.injectable)(),
    __metadata("design:paramtypes", [])
], ArtifactService);
exports.ArtifactService = ArtifactService;


/***/ },

/***/ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\packages\\agentic-artifacts\\lib\\browser\\artifacts-tree-widget.js"
/*!******************************************************************************************************************************************!*\
  !*** C:\Users\Julian Wiley\Documents\GitHub\agentic_assistants\frontend\packages\agentic-artifacts\lib\browser\artifacts-tree-widget.js ***!
  \******************************************************************************************************************************************/
(__unused_webpack_module, exports, __webpack_require__) {


/**
 * Artifacts Tree Widget
 *
 * Provides a tree view for browsing artifacts with tag and group filtering.
 */
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
```
