# Chunk: cc9fe33e8daf_5

- source: `frontend/browser-app/lib/frontend/C_Users_Julian_Wiley_Documents_GitHub_agentic_assistants_frontend_packages_agentic-artifacts_-341fb0.js`
- lines: 244-309
- chunk: 6/19

```
ectedArtifact.artifact.id, [group], []);
                        if (result) {
                            this.messageService.info(`Added to group "${group}"`);
                        }
                        else {
                            this.messageService.error('Failed to add to group');
                        }
                    }
                }
            }
        });
        registry.registerCommand(ArtifactCommands.SHARE_ARTIFACT, {
            execute: async () => {
                const artifacts = this.artifactService.getArtifacts().filter(a => !a.is_shared);
                if (artifacts.length === 0) {
                    this.messageService.info('No artifacts to share');
                    return;
                }
                const artifactItems = artifacts.map(a => ({
                    label: a.name,
                    description: `Size: ${a.size} bytes`,
                    artifact: a
                }));
                const selectedArtifact = await this.quickInputService.pick(artifactItems, {
                    placeHolder: 'Select artifact to share'
                });
                if (selectedArtifact && 'artifact' in selectedArtifact) {
                    const result = await this.artifactService.shareArtifact(selectedArtifact.artifact.id);
                    if (result) {
                        this.messageService.info(`Shared artifact: ${selectedArtifact.artifact.name}`);
                    }
                    else {
                        this.messageService.error('Failed to share artifact');
                    }
                }
            }
        });
        registry.registerCommand(ArtifactCommands.DOWNLOAD_ARTIFACT, {
            execute: async () => {
                const artifacts = this.artifactService.getArtifacts();
                if (artifacts.length === 0) {
                    this.messageService.info('No artifacts available');
                    return;
                }
                const artifactItems = artifacts.map(a => ({
                    label: a.name,
                    description: `Size: ${a.size} bytes`,
                    artifact: a
                }));
                const selectedArtifact = await this.quickInputService.pick(artifactItems, {
                    placeHolder: 'Select artifact to download'
                });
                if (selectedArtifact && 'artifact' in selectedArtifact) {
                    const url = this.artifactService.getDownloadUrl(selectedArtifact.artifact.id);
                    window.open(url, '_blank');
                }
            }
        });
        registry.registerCommand(ArtifactCommands.DELETE_ARTIFACT, {
            execute: async () => {
                const artifacts = this.artifactService.getArtifacts();
                if (artifacts.length === 0) {
                    this.messageService.info('No artifacts to delete');
                    return;
                }
```
