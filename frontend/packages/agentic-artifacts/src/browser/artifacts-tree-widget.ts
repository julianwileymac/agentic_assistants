/**
 * Artifacts Tree Widget
 * 
 * Provides a tree view for browsing artifacts with tag and group filtering.
 */

import { injectable, inject, postConstruct } from '@theia/core/shared/inversify';
import { TreeWidget, TreeNode, CompositeTreeNode, SelectableTreeNode, ExpandableTreeNode, TreeModel, TreeProps } from '@theia/core/lib/browser/tree';
import { ContextMenuRenderer } from '@theia/core/lib/browser';
import { MessageService } from '@theia/core';
import { ArtifactService, ArtifactServiceSymbol, Artifact, GroupInfo, TagInfo } from './artifact-service';

export const ARTIFACTS_TREE_WIDGET_ID = 'artifacts-tree-widget';

export interface GroupNode extends CompositeTreeNode, SelectableTreeNode, ExpandableTreeNode {
    group: GroupInfo;
}

export interface TagNode extends CompositeTreeNode, SelectableTreeNode, ExpandableTreeNode {
    tag: TagInfo;
}

export interface ArtifactNode extends SelectableTreeNode {
    artifact: Artifact;
}

export namespace GroupNode {
    export function is(node: TreeNode | undefined): node is GroupNode {
        return !!node && 'group' in node;
    }
}

export namespace TagNode {
    export function is(node: TreeNode | undefined): node is TagNode {
        return !!node && 'tag' in node;
    }
}

export namespace ArtifactNode {
    export function is(node: TreeNode | undefined): node is ArtifactNode {
        return !!node && 'artifact' in node;
    }
}

export type ViewMode = 'all' | 'by-group' | 'by-tag' | 'shared';

@injectable()
export class ArtifactsTreeWidget extends TreeWidget {

    static readonly ID = ARTIFACTS_TREE_WIDGET_ID;
    static readonly LABEL = 'Artifacts';

    @inject(ArtifactServiceSymbol)
    protected readonly artifactService: ArtifactService;

    @inject(MessageService)
    protected readonly messageService: MessageService;

    protected viewMode: ViewMode = 'all';

    constructor(
        @inject(TreeProps) readonly props: TreeProps,
        @inject(TreeModel) readonly model: TreeModel,
        @inject(ContextMenuRenderer) readonly contextMenuRenderer: ContextMenuRenderer
    ) {
        super(props, model, contextMenuRenderer);

        this.id = ArtifactsTreeWidget.ID;
        this.title.label = ArtifactsTreeWidget.LABEL;
        this.title.caption = ArtifactsTreeWidget.LABEL;
        this.title.closable = true;
        this.title.iconClass = 'fa fa-archive';
    }

    @postConstruct()
    protected init(): void {
        super.init();
        
        // Listen for artifact changes
        this.artifactService.onArtifactsChanged(() => {
            this.refreshTree();
        });

        this.artifactService.onGroupsChanged(() => {
            if (this.viewMode === 'by-group') {
                this.refreshTree();
            }
        });

        this.artifactService.onTagsChanged(() => {
            if (this.viewMode === 'by-tag') {
                this.refreshTree();
            }
        });

        // Initial load
        this.refresh();
    }

    async refresh(): Promise<void> {
        try {
            await this.artifactService.refreshArtifacts();
            this.refreshTree();
        } catch (error) {
            this.messageService.error('Failed to load artifacts: ' + error);
        }
    }

    setViewMode(mode: ViewMode): void {
        this.viewMode = mode;
        this.refreshTree();
    }

    protected refreshTree(): void {
        let root: CompositeTreeNode;

        switch (this.viewMode) {
            case 'by-group':
                root = this.createGroupedRoot();
                break;
            case 'by-tag':
                root = this.createTaggedRoot();
                break;
            case 'shared':
                root = this.createSharedRoot();
                break;
            default:
                root = this.createAllArtifactsRoot();
        }

        this.model.root = root;
    }

    protected createAllArtifactsRoot(): CompositeTreeNode {
        const artifacts = this.artifactService.getArtifacts();
        
        const root: CompositeTreeNode = {
            id: 'artifacts-root',
            name: 'All Artifacts',
            parent: undefined,
            children: [],
            visible: false
        };

        root.children = artifacts.map(artifact => this.createArtifactNode(artifact, root));

        return root;
    }

    protected createGroupedRoot(): CompositeTreeNode {
        const groups = this.artifactService.getGroups();
        const artifacts = this.artifactService.getArtifacts();
        
        const root: CompositeTreeNode = {
            id: 'artifacts-root',
            name: 'Artifacts by Group',
            parent: undefined,
            children: [],
            visible: false
        };

        // Group nodes
        const groupNodes = groups.map(group => {
            const groupArtifacts = artifacts.filter(a => a.groups.includes(group.name));
            return this.createGroupNode(group, groupArtifacts, root);
        });

        // Ungrouped artifacts
        const ungrouped = artifacts.filter(a => a.groups.length === 0);
        if (ungrouped.length > 0) {
            const ungroupedNode: CompositeTreeNode & SelectableTreeNode & ExpandableTreeNode = {
                id: 'group-ungrouped',
                name: 'Ungrouped',
                parent: root,
                children: ungrouped.map(a => this.createArtifactNode(a, root)),
                selected: false,
                expanded: false
            };
            groupNodes.push(ungroupedNode as GroupNode);
        }

        root.children = groupNodes;

        return root;
    }

    protected createTaggedRoot(): CompositeTreeNode {
        const tags = this.artifactService.getTags();
        const artifacts = this.artifactService.getArtifacts();
        
        const root: CompositeTreeNode = {
            id: 'artifacts-root',
            name: 'Artifacts by Tag',
            parent: undefined,
            children: [],
            visible: false
        };

        // Tag nodes
        const tagNodes = tags.map(tag => {
            const tagArtifacts = artifacts.filter(a => a.tags.includes(tag.name));
            return this.createTagNode(tag, tagArtifacts, root);
        });

        // Untagged artifacts
        const untagged = artifacts.filter(a => a.tags.length === 0);
        if (untagged.length > 0) {
            const untaggedNode: CompositeTreeNode & SelectableTreeNode & ExpandableTreeNode = {
                id: 'tag-untagged',
                name: 'Untagged',
                parent: root,
                children: untagged.map(a => this.createArtifactNode(a, root)),
                selected: false,
                expanded: false
            };
            tagNodes.push(untaggedNode as TagNode);
        }

        root.children = tagNodes;

        return root;
    }

    protected createSharedRoot(): CompositeTreeNode {
        const artifacts = this.artifactService.getArtifacts().filter(a => a.is_shared);
        
        const root: CompositeTreeNode = {
            id: 'artifacts-root',
            name: 'Shared Artifacts',
            parent: undefined,
            children: [],
            visible: false
        };

        root.children = artifacts.map(artifact => this.createArtifactNode(artifact, root));

        return root;
    }

    protected createGroupNode(group: GroupInfo, artifacts: Artifact[], parent: CompositeTreeNode): GroupNode {
        const node: GroupNode = {
            id: `group-${group.name}`,
            name: `${group.name} (${group.artifact_count})`,
            parent,
            children: [],
            selected: false,
            expanded: false,
            group
        };

        node.children = artifacts.map(artifact => this.createArtifactNode(artifact, node));

        return node;
    }

    protected createTagNode(tag: TagInfo, artifacts: Artifact[], parent: CompositeTreeNode): TagNode {
        const node: TagNode = {
            id: `tag-${tag.name}`,
            name: `${tag.name} (${tag.artifact_count})`,
            parent,
            children: [],
            selected: false,
            expanded: false,
            tag
        };

        node.children = artifacts.map(artifact => this.createArtifactNode(artifact, node));

        return node;
    }

    protected createArtifactNode(artifact: Artifact, parent: CompositeTreeNode): ArtifactNode {
        const sizeStr = this.formatSize(artifact.size);
        return {
            id: `artifact-${artifact.id}`,
            name: `${artifact.name} (${sizeStr})`,
            parent,
            selected: false,
            artifact
        };
    }

    protected formatSize(bytes: number): string {
        if (bytes < 1024) return `${bytes} B`;
        if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
        if (bytes < 1024 * 1024 * 1024) return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
        return `${(bytes / 1024 / 1024 / 1024).toFixed(1)} GB`;
    }

    protected override toNodeIcon(node: TreeNode): string {
        if (GroupNode.is(node)) {
            return 'fa fa-folder';
        }
        if (TagNode.is(node)) {
            return 'fa fa-tag';
        }
        if (ArtifactNode.is(node)) {
            if (node.artifact.is_shared) {
                return 'fa fa-share-alt';
            }
            const mimeType = node.artifact.mime_type || '';
            if (mimeType.startsWith('image/')) return 'fa fa-image';
            if (mimeType.startsWith('text/')) return 'fa fa-file-text';
            if (mimeType.includes('json')) return 'fa fa-file-code';
            if (mimeType.includes('parquet')) return 'fa fa-table';
            return 'fa fa-file';
        }
        return '';
    }
}

