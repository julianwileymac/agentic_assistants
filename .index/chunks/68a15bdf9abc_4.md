# Chunk: 68a15bdf9abc_4

- source: `frontend/packages/agentic-artifacts/lib/browser/artifact-commands.js`
- lines: 244-298
- chunk: 5/5

```
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
                const artifactItems = artifacts.map(a => ({
                    label: a.name,
                    description: a.id,
                    artifact: a
                }));
                const selectedArtifact = await this.quickInputService.pick(artifactItems, {
                    placeHolder: 'Select artifact to delete'
                });
                if (selectedArtifact && 'artifact' in selectedArtifact) {
                    const confirm = await this.quickInputService.input({
                        prompt: `Type "${selectedArtifact.artifact.name}" to confirm deletion`,
                        placeHolder: selectedArtifact.artifact.name
                    });
                    if (confirm === selectedArtifact.artifact.name) {
                        const success = await this.artifactService.deleteArtifact(selectedArtifact.artifact.id);
                        if (success) {
                            this.messageService.info('Deleted artifact: ' + selectedArtifact.artifact.name);
                        }
                        else {
                            this.messageService.error('Failed to delete artifact');
                        }
                    }
                }
            }
        });
    }
};
__decorate([
    (0, inversify_1.inject)(artifact_service_1.ArtifactServiceSymbol),
    __metadata("design:type", artifact_service_1.ArtifactService)
], ArtifactCommandContribution.prototype, "artifactService", void 0);
__decorate([
    (0, inversify_1.inject)(core_1.MessageService),
    __metadata("design:type", core_1.MessageService)
], ArtifactCommandContribution.prototype, "messageService", void 0);
__decorate([
    (0, inversify_1.inject)(core_1.QuickInputService),
    __metadata("design:type", Object)
], ArtifactCommandContribution.prototype, "quickInputService", void 0);
ArtifactCommandContribution = __decorate([
    (0, inversify_1.injectable)()
], ArtifactCommandContribution);
exports.ArtifactCommandContribution = ArtifactCommandContribution;
//# sourceMappingURL=artifact-commands.js.map
```
