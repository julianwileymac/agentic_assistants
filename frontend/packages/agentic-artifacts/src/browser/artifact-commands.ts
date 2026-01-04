/**
 * Artifact Command Contribution
 * 
 * Provides commands for artifact management.
 */

import { injectable, inject } from '@theia/core/shared/inversify';
import { CommandContribution, CommandRegistry, Command } from '@theia/core/lib/common';
import { MessageService, QuickInputService } from '@theia/core';
import { ArtifactService, ArtifactServiceSymbol } from './artifact-service';

export namespace ArtifactCommands {
    const ARTIFACTS_CATEGORY = 'Artifacts';

    export const TOGGLE_ARTIFACTS_VIEW: Command = {
        id: 'artifacts.toggleView',
        label: 'Toggle Artifacts View',
        category: ARTIFACTS_CATEGORY
    };

    export const REFRESH_ARTIFACTS: Command = {
        id: 'artifacts.refresh',
        label: 'Refresh Artifacts',
        category: ARTIFACTS_CATEGORY
    };

    export const VIEW_ALL: Command = {
        id: 'artifacts.viewAll',
        label: 'View All Artifacts',
        category: ARTIFACTS_CATEGORY
    };

    export const VIEW_BY_GROUP: Command = {
        id: 'artifacts.viewByGroup',
        label: 'View Artifacts by Group',
        category: ARTIFACTS_CATEGORY
    };

    export const VIEW_BY_TAG: Command = {
        id: 'artifacts.viewByTag',
        label: 'View Artifacts by Tag',
        category: ARTIFACTS_CATEGORY
    };

    export const VIEW_SHARED: Command = {
        id: 'artifacts.viewShared',
        label: 'View Shared Artifacts',
        category: ARTIFACTS_CATEGORY
    };

    export const ADD_TAG: Command = {
        id: 'artifacts.addTag',
        label: 'Add Tag to Artifact',
        category: ARTIFACTS_CATEGORY
    };

    export const REMOVE_TAG: Command = {
        id: 'artifacts.removeTag',
        label: 'Remove Tag from Artifact',
        category: ARTIFACTS_CATEGORY
    };

    export const ADD_TO_GROUP: Command = {
        id: 'artifacts.addToGroup',
        label: 'Add Artifact to Group',
        category: ARTIFACTS_CATEGORY
    };

    export const REMOVE_FROM_GROUP: Command = {
        id: 'artifacts.removeFromGroup',
        label: 'Remove Artifact from Group',
        category: ARTIFACTS_CATEGORY
    };

    export const SHARE_ARTIFACT: Command = {
        id: 'artifacts.share',
        label: 'Share Artifact',
        category: ARTIFACTS_CATEGORY
    };

    export const DOWNLOAD_ARTIFACT: Command = {
        id: 'artifacts.download',
        label: 'Download Artifact',
        category: ARTIFACTS_CATEGORY
    };

    export const DELETE_ARTIFACT: Command = {
        id: 'artifacts.delete',
        label: 'Delete Artifact',
        category: ARTIFACTS_CATEGORY
    };
}

@injectable()
export class ArtifactCommandContribution implements CommandContribution {

    @inject(ArtifactServiceSymbol)
    protected readonly artifactService: ArtifactService;

    @inject(MessageService)
    protected readonly messageService: MessageService;

    @inject(QuickInputService)
    protected readonly quickInputService: QuickInputService;

    registerCommands(registry: CommandRegistry): void {
        registry.registerCommand(ArtifactCommands.REFRESH_ARTIFACTS, {
            execute: async () => {
                try {
                    await this.artifactService.refreshArtifacts();
                    this.messageService.info('Artifacts refreshed');
                } catch (error) {
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
                        const result = await this.artifactService.updateArtifactTags(
                            selectedArtifact.artifact.id,
                            [tag],
                            []
                        );
                        if (result) {
                            this.messageService.info(`Added tag "${tag}" to ${selectedArtifact.artifact.name}`);
                        } else {
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
                        const result = await this.artifactService.updateArtifactTags(
                            selectedArtifact.artifact.id,
                            [],
                            [selectedTag.label]
                        );
                        if (result) {
                            this.messageService.info(`Removed tag "${selectedTag.label}"`);
                        } else {
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
                        const result = await this.artifactService.updateArtifactGroups(
                            selectedArtifact.artifact.id,
                            [group],
                            []
                        );
                        if (result) {
                            this.messageService.info(`Added to group "${group}"`);
                        } else {
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
                    } else {
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
                        } else {
                            this.messageService.error('Failed to delete artifact');
                        }
                    }
                }
            }
        });
    }
}

