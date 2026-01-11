# Chunk: dffada7ce41c_2

- source: `frontend/packages/agentic-artifacts/lib/browser/artifact-service.js`
- lines: 142-223
- chunk: 3/3

```
istGroups() {
        const response = await this.backendService.get('/artifacts/groups/list');
        if (response.data) {
            this.groups = response.data;
            this.onGroupsChangedEmitter.fire(this.groups);
            return this.groups;
        }
        return [];
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
//# sourceMappingURL=artifact-service.js.map
```
