# Chunk: 68a15bdf9abc_2

- source: `frontend/packages/agentic-artifacts/lib/browser/artifact-commands.js`
- lines: 131-194
- chunk: 3/5

```
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
                const artifactItems = artifacts.map(a => ({
                    label: a.name,
                    description: a.tags.join(', '),
                    artifact: a
                }));
                const selectedArtifact = await this.quickInputService.pick(artifactItems, {
                    placeHolder: 'Select artifact'
                });
                if (selectedArtifact && 'artifact' in selectedArtifact) {
                    const tagItems = selectedArtifact.artifact.tags.map(t => ({
                        label: t
                    }));
                    const selectedTag = await this.quickInputService.pick(tagItems, {
                        placeHolder: 'Select tag to remove'
                    });
                    if (selectedTag) {
                        const result = await this.artifactService.updateArtifactTags(selectedArtifact.artifact.id, [], [selectedTag.label]);
                        if (result) {
                            this.messageService.info(`Removed tag "${selectedTag.label}"`);
                        }
                        else {
                            this.messageService.error('Failed to remove tag');
                        }
                    }
                }
            }
        });
        registry.registerCommand(ArtifactCommands.ADD_TO_GROUP, {
            execute: async () => {
                const artifacts = this.artifactService.getArtifacts();
                if (artifacts.length === 0) {
                    this.messageService.info('No artifacts available');
                    return;
                }
                const artifactItems = artifacts.map(a => ({
                    label: a.name,
                    description: a.groups.join(', ') || 'No groups',
                    artifact: a
                }));
                const selectedArtifact = await this.quickInputService.pick(artifactItems, {
                    placeHolder: 'Select artifact'
                });
                if (selectedArtifact && 'artifact' in selectedArtifact) {
                    const group = await this.quickInputService.input({
                        prompt: 'Enter group name',
                        placeHolder: 'my-group'
                    });
                    if (group) {
                        const result = await this.artifactService.updateArtifactGroups(selectedArtifact.artifact.id, [group], []);
                        if (result) {
                            this.messageService.info(`Added to group "${group}"`);
                        }
```
