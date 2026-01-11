# Chunk: dffada7ce41c_1

- source: `frontend/packages/agentic-artifacts/lib/browser/artifact-service.js`
- lines: 59-152
- chunk: 2/3

```
params.groups.join(',');
        if (params === null || params === void 0 ? void 0 : params.sessionId)
            queryParams.session_id = params.sessionId;
        if (params === null || params === void 0 ? void 0 : params.experimentId)
            queryParams.experiment_id = params.experimentId;
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
```
