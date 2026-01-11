# Chunk: cc9fe33e8daf_6

- source: `frontend/browser-app/lib/frontend/C_Users_Julian_Wiley_Documents_GitHub_agentic_assistants_frontend_packages_agentic-artifacts_-341fb0.js`
- lines: 302-366
- chunk: 7/19

```
ctCommands.DELETE_ARTIFACT, {
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


/***/ },

/***/ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\packages\\agentic-artifacts\\lib\\browser\\artifact-menu.js"
/*!**********************************************************************************************************************************!*\
  !*** C:\Users\Julian Wiley\Documents\GitHub\agentic_assistants\frontend\packages\agentic-artifacts\lib\browser\artifact-menu.js ***!
  \**********************************************************************************************************************************/
(__unused_webpack_module, exports, __webpack_require__) {


/**
 * Artifact Menu Contribution
 *
```
