/**
 * Data Explorer Widget
 * 
 * Provides a file tree view for browsing data files with preview capabilities.
 */

import { injectable, inject, postConstruct } from '@theia/core/shared/inversify';
import { TreeWidget, TreeNode, CompositeTreeNode, SelectableTreeNode, ExpandableTreeNode, TreeModel, TreeProps } from '@theia/core/lib/browser/tree';
import { ContextMenuRenderer } from '@theia/core/lib/browser';
import { MessageService } from '@theia/core';
import { DataService, DataServiceSymbol, FileInfo } from './data-service';

export const DATA_EXPLORER_WIDGET_ID = 'data-explorer-widget';

export interface DirectoryNode extends CompositeTreeNode, SelectableTreeNode, ExpandableTreeNode {
    file: FileInfo;
}

export interface FileNode extends SelectableTreeNode {
    file: FileInfo;
}

export namespace DirectoryNode {
    export function is(node: TreeNode | undefined): node is DirectoryNode {
        return !!node && 'file' in node && (node as FileNode).file.is_dir;
    }
}

export namespace FileNode {
    export function is(node: TreeNode | undefined): node is FileNode {
        return !!node && 'file' in node && !(node as FileNode).file.is_dir;
    }
}

@injectable()
export class DataExplorerWidget extends TreeWidget {

    static readonly ID = DATA_EXPLORER_WIDGET_ID;
    static readonly LABEL = 'Data Explorer';

    @inject(DataServiceSymbol)
    protected readonly dataService: DataService;

    @inject(MessageService)
    protected readonly messageService: MessageService;

    constructor(
        @inject(TreeProps) readonly props: TreeProps,
        @inject(TreeModel) readonly model: TreeModel,
        @inject(ContextMenuRenderer) readonly contextMenuRenderer: ContextMenuRenderer
    ) {
        super(props, model, contextMenuRenderer);

        this.id = DataExplorerWidget.ID;
        this.title.label = DataExplorerWidget.LABEL;
        this.title.caption = DataExplorerWidget.LABEL;
        this.title.closable = true;
        this.title.iconClass = 'fa fa-database';
    }

    @postConstruct()
    protected init(): void {
        super.init();
        
        this.toDispose.push(this.model.onExpansionChanged(async node => this.handleNodeExpansion(node)));

        // Listen for file changes
        this.dataService.onFilesChanged(() => {
            this.refreshTree();
        });

        this.dataService.onPathChanged(path => {
            this.title.caption = `Data Explorer - ${path}`;
        });

        // Initial load
        this.refresh();
    }

    async refresh(): Promise<void> {
        try {
            await this.dataService.listFiles();
            this.refreshTree();
        } catch (error) {
            this.messageService.error('Failed to load files: ' + error);
        }
    }

    protected refreshTree(): void {
        const files = this.dataService.getFiles();
        const currentPath = this.dataService.getCurrentPath();
        const root = this.createRootNode(files, currentPath);
        this.model.root = root;
    }

    protected createRootNode(files: FileInfo[], currentPath: string): CompositeTreeNode {
        const root: CompositeTreeNode = {
            id: 'data-root',
            name: currentPath,
            parent: undefined,
            children: [],
            visible: false
        };

        // Sort: directories first, then by name
        const sortedFiles = [...files].sort((a, b) => {
            if (a.is_dir && !b.is_dir) return -1;
            if (!a.is_dir && b.is_dir) return 1;
            return a.name.localeCompare(b.name);
        });

        root.children = sortedFiles.map(file => this.createFileNode(file, root));

        return root;
    }

    protected createFileNode(file: FileInfo, parent: CompositeTreeNode): DirectoryNode | FileNode {
        if (file.is_dir) {
            return {
                id: `dir-${file.path}`,
                name: file.name,
                parent,
                children: [],
                selected: false,
                expanded: false,
                file
            } as DirectoryNode;
        } else {
            const sizeStr = this.formatSize(file.size);
            return {
                id: `file-${file.path}`,
                name: `${file.name} (${sizeStr})`,
                parent,
                selected: false,
                file
            } as FileNode;
        }
    }

    protected formatSize(bytes: number): string {
        if (bytes < 1024) return `${bytes} B`;
        if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
        if (bytes < 1024 * 1024 * 1024) return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
        return `${(bytes / 1024 / 1024 / 1024).toFixed(1)} GB`;
    }

    protected async handleNodeExpansion(node: ExpandableTreeNode): Promise<void> {
        if (!node.expanded) {
            return;
        }

        if (DirectoryNode.is(node)) {
            // Load directory contents when expanded
            try {
                const files = await this.dataService.listFiles(node.file.path);
                (node as CompositeTreeNode).children = files.map(file => this.createFileNode(file, node as CompositeTreeNode));
                await this.model.refresh(node);
            } catch (error) {
                this.messageService.error('Failed to load directory: ' + error);
            }
        }
    }

    protected override toNodeIcon(node: TreeNode): string {
        if (DirectoryNode.is(node)) {
            return 'fa fa-folder';
        }
        if (FileNode.is(node)) {
            const format = node.file.format || '';
            switch (format) {
                case 'parquet':
                    return 'fa fa-table';
                case 'csv':
                    return 'fa fa-file-csv';
                case 'json':
                case 'jsonl':
                    return 'fa fa-file-code';
                case 'yaml':
                    return 'fa fa-file-alt';
                case 'text':
                    return 'fa fa-file-text';
                default:
                    return 'fa fa-file';
            }
        }
        return '';
    }

    /**
     * Get the currently selected file
     */
    getSelectedFile(): FileInfo | undefined {
        const selected = this.model.selectedNodes[0];
        if (FileNode.is(selected) || DirectoryNode.is(selected)) {
            return selected.file;
        }
        return undefined;
    }
}

