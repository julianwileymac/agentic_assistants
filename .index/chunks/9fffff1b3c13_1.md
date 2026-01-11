# Chunk: 9fffff1b3c13_1

- source: `frontend/packages/agentic-data-viewer/lib/browser/data-service.d.ts`
- lines: 106-128
- chunk: 2/2

```
rCache(): Promise<boolean>;
    /**
     * Convert a file to another format
     */
    convertFile(sourcePath: string, targetPath: string, targetFormat?: string): Promise<boolean>;
    /**
     * Get supported formats
     */
    getSupportedFormats(): Promise<Record<string, unknown> | undefined>;
    /**
     * Get current path
     */
    getCurrentPath(): string;
    /**
     * Get cached files
     */
    getFiles(): FileInfo[];
    /**
     * Check if a file is tabular (parquet, csv)
     */
    isTabular(file: FileInfo): boolean;
}
//# sourceMappingURL=data-service.d.ts.map
```
