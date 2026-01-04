/**
 * Data Service
 * 
 * Provides data layer operations for file browsing, table preview, and schema inspection.
 */

import { injectable, inject } from '@theia/core/shared/inversify';
import { Emitter, Event } from '@theia/core/lib/common';
import { AgenticBackendService, AgenticBackendServiceSymbol } from 'agentic-core/lib/browser';

export const DataServiceSymbol = Symbol('DataService');

export interface FileInfo {
    path: string;
    name: string;
    extension: string;
    size: number;
    format?: string;
    is_dir: boolean;
    modified_at?: string;
}

export interface ColumnInfo {
    name: string;
    dtype: string;
    nullable: boolean;
    num_unique?: number;
    null_count?: number;
    sample_values: unknown[];
}

export interface TableSchema {
    path: string;
    format: string;
    columns: ColumnInfo[];
    row_count: number;
    size_bytes: number;
}

export interface TablePreview {
    path: string;
    columns: string[];
    rows: Record<string, unknown>[];
    total_rows: number;
    offset: number;
    limit: number;
}

export interface DirectoryListing {
    path: string;
    files: FileInfo[];
    total: number;
}

export interface CacheStats {
    enabled: boolean;
    hits: number;
    misses: number;
    size: number;
    max_size: number;
}

@injectable()
export class DataService {

    @inject(AgenticBackendServiceSymbol)
    protected readonly backendService: AgenticBackendService;

    protected currentPath: string = '.';
    protected files: FileInfo[] = [];

    protected readonly onFilesChangedEmitter = new Emitter<FileInfo[]>();
    readonly onFilesChanged: Event<FileInfo[]> = this.onFilesChangedEmitter.event;

    protected readonly onPathChangedEmitter = new Emitter<string>();
    readonly onPathChanged: Event<string> = this.onPathChangedEmitter.event;

    /**
     * List files in a directory
     */
    async listFiles(path?: string): Promise<FileInfo[]> {
        const targetPath = path || this.currentPath;
        const response = await this.backendService.get<DirectoryListing>('/data/files', { path: targetPath });
        
        if (response.data) {
            this.files = response.data.files;
            this.currentPath = targetPath;
            this.onFilesChangedEmitter.fire(this.files);
            this.onPathChangedEmitter.fire(this.currentPath);
            return this.files;
        }
        return [];
    }

    /**
     * Navigate to a directory
     */
    async navigateTo(path: string): Promise<void> {
        await this.listFiles(path);
    }

    /**
     * Navigate up one directory level
     */
    async navigateUp(): Promise<void> {
        const parts = this.currentPath.split('/').filter(p => p);
        if (parts.length > 0) {
            parts.pop();
            const newPath = parts.length > 0 ? parts.join('/') : '.';
            await this.navigateTo(newPath);
        }
    }

    /**
     * Get file information
     */
    async getFileInfo(path: string): Promise<FileInfo | undefined> {
        const response = await this.backendService.get<FileInfo>('/data/file', { path });
        return response.data;
    }

    /**
     * Get table schema
     */
    async getSchema(path: string): Promise<TableSchema | undefined> {
        const response = await this.backendService.get<TableSchema>('/data/schema', { path });
        return response.data;
    }

    /**
     * Preview a table
     */
    async previewTable(path: string, offset: number = 0, limit: number = 100): Promise<TablePreview | undefined> {
        const response = await this.backendService.get<TablePreview>('/data/preview', {
            path,
            offset: String(offset),
            limit: String(limit)
        });
        return response.data;
    }

    /**
     * Read file content
     */
    async readFile(path: string, format?: string): Promise<unknown> {
        const params: Record<string, string> = { path };
        if (format) params.format = format;
        
        const response = await this.backendService.get<unknown>('/data/read', params);
        return response.data;
    }

    /**
     * Query a table
     */
    async queryTable(
        path: string,
        options?: {
            columns?: string[];
            filterExpr?: string;
            sortBy?: string;
            ascending?: boolean;
            limit?: number;
        }
    ): Promise<unknown> {
        const params: Record<string, string> = { path };
        if (options?.columns) params.columns = options.columns.join(',');
        if (options?.filterExpr) params.filter_expr = options.filterExpr;
        if (options?.sortBy) params.sort_by = options.sortBy;
        if (options?.ascending !== undefined) params.ascending = String(options.ascending);
        if (options?.limit) params.limit = String(options.limit);
        
        const response = await this.backendService.get<unknown>('/data/query', params);
        return response.data;
    }

    /**
     * Get cache statistics
     */
    async getCacheStats(): Promise<CacheStats | undefined> {
        const response = await this.backendService.get<CacheStats>('/data/cache/stats');
        return response.data;
    }

    /**
     * Clear the data cache
     */
    async clearCache(): Promise<boolean> {
        const response = await this.backendService.post('/data/cache/clear');
        return response.status === 200;
    }

    /**
     * Convert a file to another format
     */
    async convertFile(sourcePath: string, targetPath: string, targetFormat?: string): Promise<boolean> {
        const params: Record<string, string> = {
            source_path: sourcePath,
            target_path: targetPath
        };
        if (targetFormat) params.target_format = targetFormat;
        
        const response = await this.backendService.post('/data/convert', params);
        return response.status === 200;
    }

    /**
     * Get supported formats
     */
    async getSupportedFormats(): Promise<Record<string, unknown> | undefined> {
        const response = await this.backendService.get<Record<string, unknown>>('/data/supported-formats');
        return response.data;
    }

    /**
     * Get current path
     */
    getCurrentPath(): string {
        return this.currentPath;
    }

    /**
     * Get cached files
     */
    getFiles(): FileInfo[] {
        return this.files;
    }

    /**
     * Check if a file is tabular (parquet, csv)
     */
    isTabular(file: FileInfo): boolean {
        const tabularFormats = ['parquet', 'csv'];
        return !!file.format && tabularFormats.includes(file.format);
    }
}

