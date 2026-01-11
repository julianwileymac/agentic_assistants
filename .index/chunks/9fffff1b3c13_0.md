# Chunk: 9fffff1b3c13_0

- source: `frontend/packages/agentic-data-viewer/lib/browser/data-service.d.ts`
- lines: 1-115
- chunk: 1/2

```
/**
 * Data Service
 *
 * Provides data layer operations for file browsing, table preview, and schema inspection.
 */
import { Emitter, Event } from '@theia/core/lib/common';
import { AgenticBackendService } from 'agentic-core/lib/browser';
export declare const DataServiceSymbol: unique symbol;
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
export declare class DataService {
    protected readonly backendService: AgenticBackendService;
    protected currentPath: string;
    protected files: FileInfo[];
    protected readonly onFilesChangedEmitter: Emitter<FileInfo[]>;
    readonly onFilesChanged: Event<FileInfo[]>;
    protected readonly onPathChangedEmitter: Emitter<string>;
    readonly onPathChanged: Event<string>;
    /**
     * List files in a directory
     */
    listFiles(path?: string): Promise<FileInfo[]>;
    /**
     * Navigate to a directory
     */
    navigateTo(path: string): Promise<void>;
    /**
     * Navigate up one directory level
     */
    navigateUp(): Promise<void>;
    /**
     * Get file information
     */
    getFileInfo(path: string): Promise<FileInfo | undefined>;
    /**
     * Get table schema
     */
    getSchema(path: string): Promise<TableSchema | undefined>;
    /**
     * Preview a table
     */
    previewTable(path: string, offset?: number, limit?: number): Promise<TablePreview | undefined>;
    /**
     * Read file content
     */
    readFile(path: string, format?: string): Promise<unknown>;
    /**
     * Query a table
     */
    queryTable(path: string, options?: {
        columns?: string[];
        filterExpr?: string;
        sortBy?: string;
        ascending?: boolean;
        limit?: number;
    }): Promise<unknown>;
    /**
     * Get cache statistics
     */
    getCacheStats(): Promise<CacheStats | undefined>;
    /**
     * Clear the data cache
     */
    clearCache(): Promise<boolean>;
    /**
     * Convert a file to another format
     */
    convertFile(sourcePath: string, targetPath: string, targetFormat?: string): Promise<boolean>;
    /**
     * Get supported formats
     */
    getSupportedFormats(): Promise<Record<string, unknown> | undefined>;
```
