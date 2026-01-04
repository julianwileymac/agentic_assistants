/**
 * Data Viewer Command Contribution
 * 
 * Provides commands for data viewing and exploration.
 */

import { injectable, inject } from '@theia/core/shared/inversify';
import { CommandContribution, CommandRegistry, Command } from '@theia/core/lib/common';
import { MessageService, QuickInputService } from '@theia/core';
import { DataService, DataServiceSymbol } from './data-service';

export namespace DataViewerCommands {
    const DATA_CATEGORY = 'Data';

    export const TOGGLE_DATA_EXPLORER: Command = {
        id: 'data.toggleExplorer',
        label: 'Toggle Data Explorer',
        category: DATA_CATEGORY
    };

    export const REFRESH_FILES: Command = {
        id: 'data.refreshFiles',
        label: 'Refresh Files',
        category: DATA_CATEGORY
    };

    export const NAVIGATE_UP: Command = {
        id: 'data.navigateUp',
        label: 'Navigate Up',
        category: DATA_CATEGORY
    };

    export const NAVIGATE_TO: Command = {
        id: 'data.navigateTo',
        label: 'Navigate to Path',
        category: DATA_CATEGORY
    };

    export const PREVIEW_TABLE: Command = {
        id: 'data.previewTable',
        label: 'Preview Table',
        category: DATA_CATEGORY
    };

    export const VIEW_SCHEMA: Command = {
        id: 'data.viewSchema',
        label: 'View Schema',
        category: DATA_CATEGORY
    };

    export const QUERY_TABLE: Command = {
        id: 'data.queryTable',
        label: 'Query Table',
        category: DATA_CATEGORY
    };

    export const CLEAR_CACHE: Command = {
        id: 'data.clearCache',
        label: 'Clear Data Cache',
        category: DATA_CATEGORY
    };

    export const VIEW_CACHE_STATS: Command = {
        id: 'data.viewCacheStats',
        label: 'View Cache Statistics',
        category: DATA_CATEGORY
    };

    export const CONVERT_FILE: Command = {
        id: 'data.convertFile',
        label: 'Convert File Format',
        category: DATA_CATEGORY
    };
}

@injectable()
export class DataViewerCommandContribution implements CommandContribution {

    @inject(DataServiceSymbol)
    protected readonly dataService: DataService;

    @inject(MessageService)
    protected readonly messageService: MessageService;

    @inject(QuickInputService)
    protected readonly quickInputService: QuickInputService;

    registerCommands(registry: CommandRegistry): void {
        registry.registerCommand(DataViewerCommands.REFRESH_FILES, {
            execute: async () => {
                try {
                    await this.dataService.listFiles();
                    this.messageService.info('Files refreshed');
                } catch (error) {
                    this.messageService.error('Failed to refresh files: ' + error);
                }
            }
        });

        registry.registerCommand(DataViewerCommands.NAVIGATE_UP, {
            execute: async () => {
                try {
                    await this.dataService.navigateUp();
                } catch (error) {
                    this.messageService.error('Failed to navigate: ' + error);
                }
            }
        });

        registry.registerCommand(DataViewerCommands.NAVIGATE_TO, {
            execute: async () => {
                const path = await this.quickInputService.input({
                    prompt: 'Enter path to navigate to',
                    placeHolder: './data'
                });

                if (path) {
                    try {
                        await this.dataService.navigateTo(path);
                    } catch (error) {
                        this.messageService.error('Failed to navigate: ' + error);
                    }
                }
            }
        });

        registry.registerCommand(DataViewerCommands.PREVIEW_TABLE, {
            execute: async () => {
                const files = this.dataService.getFiles().filter(f => this.dataService.isTabular(f));
                if (files.length === 0) {
                    this.messageService.info('No tabular files in current directory');
                    return;
                }

                const fileItems = files.map(f => ({
                    label: f.name,
                    description: f.format,
                    file: f
                }));

                const selected = await this.quickInputService.pick(fileItems, {
                    placeHolder: 'Select file to preview'
                });

                if (selected && 'file' in selected) {
                    try {
                        const preview = await this.dataService.previewTable(selected.file.path);
                        if (preview) {
                            console.log('Table Preview:', preview);
                            this.messageService.info(`Previewing ${preview.total_rows} rows. Check console for data.`);
                        }
                    } catch (error) {
                        this.messageService.error('Failed to preview table: ' + error);
                    }
                }
            }
        });

        registry.registerCommand(DataViewerCommands.VIEW_SCHEMA, {
            execute: async () => {
                const files = this.dataService.getFiles().filter(f => this.dataService.isTabular(f));
                if (files.length === 0) {
                    this.messageService.info('No tabular files in current directory');
                    return;
                }

                const fileItems = files.map(f => ({
                    label: f.name,
                    description: f.format,
                    file: f
                }));

                const selected = await this.quickInputService.pick(fileItems, {
                    placeHolder: 'Select file to view schema'
                });

                if (selected && 'file' in selected) {
                    try {
                        const schema = await this.dataService.getSchema(selected.file.path);
                        if (schema) {
                            console.log('Table Schema:', schema);
                            const columnInfo = schema.columns.map(c => `${c.name}: ${c.dtype}`).join(', ');
                            this.messageService.info(`${schema.row_count} rows, ${schema.columns.length} columns: ${columnInfo}`);
                        }
                    } catch (error) {
                        this.messageService.error('Failed to get schema: ' + error);
                    }
                }
            }
        });

        registry.registerCommand(DataViewerCommands.CLEAR_CACHE, {
            execute: async () => {
                try {
                    const success = await this.dataService.clearCache();
                    if (success) {
                        this.messageService.info('Cache cleared');
                    } else {
                        this.messageService.error('Failed to clear cache');
                    }
                } catch (error) {
                    this.messageService.error('Error clearing cache: ' + error);
                }
            }
        });

        registry.registerCommand(DataViewerCommands.VIEW_CACHE_STATS, {
            execute: async () => {
                try {
                    const stats = await this.dataService.getCacheStats();
                    if (stats) {
                        console.log('Cache Stats:', stats);
                        this.messageService.info(
                            `Cache: ${stats.size}/${stats.max_size} items, ` +
                            `${stats.hits} hits, ${stats.misses} misses`
                        );
                    }
                } catch (error) {
                    this.messageService.error('Failed to get cache stats: ' + error);
                }
            }
        });

        registry.registerCommand(DataViewerCommands.CONVERT_FILE, {
            execute: async () => {
                const files = this.dataService.getFiles().filter(f => !f.is_dir);
                if (files.length === 0) {
                    this.messageService.info('No files to convert');
                    return;
                }

                const fileItems = files.map(f => ({
                    label: f.name,
                    description: f.format,
                    file: f
                }));

                const selected = await this.quickInputService.pick(fileItems, {
                    placeHolder: 'Select source file'
                });

                if (selected && 'file' in selected) {
                    const formatItems = [
                        { label: 'parquet', description: 'Apache Parquet' },
                        { label: 'json', description: 'JSON' },
                        { label: 'csv', description: 'CSV' }
                    ];

                    const targetFormat = await this.quickInputService.pick(formatItems, {
                        placeHolder: 'Select target format'
                    });

                    if (targetFormat) {
                        const targetPath = selected.file.path.replace(/\.[^.]+$/, `.${targetFormat.label}`);
                        
                        try {
                            const success = await this.dataService.convertFile(
                                selected.file.path,
                                targetPath,
                                targetFormat.label
                            );
                            if (success) {
                                this.messageService.info(`Converted to ${targetPath}`);
                                await this.dataService.listFiles();
                            } else {
                                this.messageService.error('Conversion failed');
                            }
                        } catch (error) {
                            this.messageService.error('Error converting file: ' + error);
                        }
                    }
                }
            }
        });
    }
}

