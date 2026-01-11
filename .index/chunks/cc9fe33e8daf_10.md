# Chunk: cc9fe33e8daf_10

- source: `frontend/browser-app/lib/frontend/C_Users_Julian_Wiley_Documents_GitHub_agentic_assistants_frontend_packages_agentic-artifacts_-341fb0.js`
- lines: 506-606
- chunk: 11/19

```
imentId;
        if (params === null || params === void 0 ? void 0 : params.sharedOnly)
            queryParams.shared_only = 'true';
        const response = await this.backendService.get('/artifacts', queryParams);
        if (response.data) {
            this.artifacts = response.data.artifacts;
            this.onArtifactsChangedEmitter.fire(this.artifacts);
            return this.artifacts;
        }
        return [];
    }
    /**
     * Refresh artifacts from server
     */
    async refreshArtifacts() {
        await this.listArtifacts();
        await this.refreshGroups();
        await this.refreshTags();
    }
    /**
     * Get a specific artifact
     */
    async getArtifact(artifactId) {
        const response = await this.backendService.get(`/artifacts/${artifactId}`);
        return response.data;
    }
    /**
     * Delete an artifact
     */
    async deleteArtifact(artifactId) {
        const response = await this.backendService.delete(`/artifacts/${artifactId}`);
        if (response.status === 200) {
            await this.refreshArtifacts();
            return true;
        }
        return false;
    }
    /**
     * Update artifact tags
     */
    async updateArtifactTags(artifactId, addTags, removeTags) {
        const response = await this.backendService.post(`/artifacts/${artifactId}/tags`, {
            add_tags: addTags,
            remove_tags: removeTags
        });
        if (response.data) {
            await this.refreshArtifacts();
            return response.data;
        }
        return undefined;
    }
    /**
     * Update artifact groups
     */
    async updateArtifactGroups(artifactId, addGroups, removeGroups) {
        const response = await this.backendService.post(`/artifacts/${artifactId}/groups`, {
            add_groups: addGroups,
            remove_groups: removeGroups
        });
        if (response.data) {
            await this.refreshArtifacts();
            return response.data;
        }
        return undefined;
    }
    /**
     * Share an artifact
     */
    async shareArtifact(artifactId) {
        const response = await this.backendService.post(`/artifacts/${artifactId}/share`);
        if (response.data) {
            await this.refreshArtifacts();
            return response.data;
        }
        return undefined;
    }
    /**
     * List all groups
     */
    async listGroups() {
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
```
