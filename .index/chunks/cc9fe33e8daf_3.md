# Chunk: cc9fe33e8daf_3

- source: `frontend/browser-app/lib/frontend/C_Users_Julian_Wiley_Documents_GitHub_agentic_assistants_frontend_packages_agentic-artifacts_-341fb0.js`
- lines: 128-196
- chunk: 4/19

```
rtifactCommands.SHARE_ARTIFACT = {
        id: 'artifacts.share',
        label: 'Share Artifact',
        category: ARTIFACTS_CATEGORY
    };
    ArtifactCommands.DOWNLOAD_ARTIFACT = {
        id: 'artifacts.download',
        label: 'Download Artifact',
        category: ARTIFACTS_CATEGORY
    };
    ArtifactCommands.DELETE_ARTIFACT = {
        id: 'artifacts.delete',
        label: 'Delete Artifact',
        category: ARTIFACTS_CATEGORY
    };
})(ArtifactCommands = exports.ArtifactCommands || (exports.ArtifactCommands = {}));
let ArtifactCommandContribution = class ArtifactCommandContribution {
    registerCommands(registry) {
        registry.registerCommand(ArtifactCommands.REFRESH_ARTIFACTS, {
            execute: async () => {
                try {
                    await this.artifactService.refreshArtifacts();
                    this.messageService.info('Artifacts refreshed');
                }
                catch (error) {
                    this.messageService.error('Failed to refresh artifacts: ' + error);
                }
            }
        });
        registry.registerCommand(ArtifactCommands.ADD_TAG, {
            execute: async () => {
                const artifacts = this.artifactService.getArtifacts();
                if (artifacts.length === 0) {
                    this.messageService.info('No artifacts available');
                    return;
                }
                const artifactItems = artifacts.map(a => ({
                    label: a.name,
                    description: a.tags.join(', ') || 'No tags',
                    artifact: a
                }));
                const selectedArtifact = await this.quickInputService.pick(artifactItems, {
                    placeHolder: 'Select artifact to tag'
                });
                if (selectedArtifact && 'artifact' in selectedArtifact) {
                    const tag = await this.quickInputService.input({
                        prompt: 'Enter tag name',
                        placeHolder: 'my-tag'
                    });
                    if (tag) {
                        const result = await this.artifactService.updateArtifactTags(selectedArtifact.artifact.id, [tag], []);
                        if (result) {
                            this.messageService.info(`Added tag "${tag}" to ${selectedArtifact.artifact.name}`);
                        }
                        else {
                            this.messageService.error('Failed to add tag');
                        }
                    }
                }
            }
        });
        registry.registerCommand(ArtifactCommands.REMOVE_TAG, {
            execute: async () => {
                const artifacts = this.artifactService.getArtifacts().filter(a => a.tags.length > 0);
                if (artifacts.length === 0) {
                    this.messageService.info('No tagged artifacts');
                    return;
                }
```
