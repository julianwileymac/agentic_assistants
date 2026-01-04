/**
 * Artifact Service
 * 
 * Provides artifact management functionality with tagging and grouping.
 */

import { injectable, inject } from '@theia/core/shared/inversify';
import { Emitter, Event } from '@theia/core/lib/common';
import { AgenticBackendService, AgenticBackendServiceSymbol, AgenticWebSocketClient, AgenticWebSocketClientSymbol } from 'agentic-core/lib/browser';

export const ArtifactServiceSymbol = Symbol('ArtifactService');

export interface Artifact {
    id: string;
    name: string;
    path: string;
    size: number;
    mime_type?: string;
    tags: string[];
    groups: string[];
    session_id?: string;
    experiment_id?: string;
    run_id?: string;
    created_at: string;
    updated_at: string;
    description?: string;
    is_shared: boolean;
}

export interface ArtifactsListResponse {
    artifacts: Artifact[];
    total: number;
}

export interface GroupInfo {
    name: string;
    artifact_count: number;
    total_size: number;
}

export interface TagInfo {
    name: string;
    artifact_count: number;
}

@injectable()
export class ArtifactService {

    @inject(AgenticBackendServiceSymbol)
    protected readonly backendService: AgenticBackendService;

    @inject(AgenticWebSocketClientSymbol)
    protected readonly wsClient: AgenticWebSocketClient;

    protected artifacts: Artifact[] = [];
    protected groups: GroupInfo[] = [];
    protected tags: TagInfo[] = [];

    protected readonly onArtifactsChangedEmitter = new Emitter<Artifact[]>();
    readonly onArtifactsChanged: Event<Artifact[]> = this.onArtifactsChangedEmitter.event;

    protected readonly onGroupsChangedEmitter = new Emitter<GroupInfo[]>();
    readonly onGroupsChanged: Event<GroupInfo[]> = this.onGroupsChangedEmitter.event;

    protected readonly onTagsChangedEmitter = new Emitter<TagInfo[]>();
    readonly onTagsChanged: Event<TagInfo[]> = this.onTagsChangedEmitter.event;

    constructor() {
        // Will be initialized after injection
    }

    protected initialize(): void {
        // Listen for WebSocket events
        this.wsClient.onArtifactEvent(message => {
            this.handleArtifactEvent(message);
        });
    }

    protected handleArtifactEvent(message: { type: string; data: Record<string, unknown> }): void {
        switch (message.type) {
            case 'artifact.created':
            case 'artifact.updated':
            case 'artifact.deleted':
            case 'artifact.shared':
                this.refreshArtifacts();
                break;
        }
    }

    /**
     * List all artifacts with optional filtering
     */
    async listArtifacts(params?: {
        tags?: string[];
        groups?: string[];
        sessionId?: string;
        experimentId?: string;
        sharedOnly?: boolean;
    }): Promise<Artifact[]> {
        const queryParams: Record<string, string> = {};
        if (params?.tags) queryParams.tags = params.tags.join(',');
        if (params?.groups) queryParams.groups = params.groups.join(',');
        if (params?.sessionId) queryParams.session_id = params.sessionId;
        if (params?.experimentId) queryParams.experiment_id = params.experimentId;
        if (params?.sharedOnly) queryParams.shared_only = 'true';

        const response = await this.backendService.get<ArtifactsListResponse>('/artifacts', queryParams);
        if (response.data) {
            this.artifacts = response.data.artifacts;
            this.onArtifactsChangedEmitter.fire(this.artifacts);
            return this.artifacts;
        }
        return [];
    }

    /**
     * Refresh artifacts from server
     */
    async refreshArtifacts(): Promise<void> {
        await this.listArtifacts();
        await this.refreshGroups();
        await this.refreshTags();
    }

    /**
     * Get a specific artifact
     */
    async getArtifact(artifactId: string): Promise<Artifact | undefined> {
        const response = await this.backendService.get<Artifact>(`/artifacts/${artifactId}`);
        return response.data;
    }

    /**
     * Delete an artifact
     */
    async deleteArtifact(artifactId: string): Promise<boolean> {
        const response = await this.backendService.delete(`/artifacts/${artifactId}`);
        if (response.status === 200) {
            await this.refreshArtifacts();
            return true;
        }
        return false;
    }

    /**
     * Update artifact tags
     */
    async updateArtifactTags(artifactId: string, addTags: string[], removeTags: string[]): Promise<Artifact | undefined> {
        const response = await this.backendService.post<Artifact>(`/artifacts/${artifactId}/tags`, {
            add_tags: addTags,
            remove_tags: removeTags
        });
        if (response.data) {
            await this.refreshArtifacts();
            return response.data;
        }
        return undefined;
    }

    /**
     * Update artifact groups
     */
    async updateArtifactGroups(artifactId: string, addGroups: string[], removeGroups: string[]): Promise<Artifact | undefined> {
        const response = await this.backendService.post<Artifact>(`/artifacts/${artifactId}/groups`, {
            add_groups: addGroups,
            remove_groups: removeGroups
        });
        if (response.data) {
            await this.refreshArtifacts();
            return response.data;
        }
        return undefined;
    }

    /**
     * Share an artifact
     */
    async shareArtifact(artifactId: string): Promise<Artifact | undefined> {
        const response = await this.backendService.post<Artifact>(`/artifacts/${artifactId}/share`);
        if (response.data) {
            await this.refreshArtifacts();
            return response.data;
        }
        return undefined;
    }

    /**
     * List all groups
     */
    async listGroups(): Promise<GroupInfo[]> {
        const response = await this.backendService.get<GroupInfo[]>('/artifacts/groups/list');
        if (response.data) {
            this.groups = response.data;
            this.onGroupsChangedEmitter.fire(this.groups);
            return this.groups;
        }
        return [];
    }

    /**
     * Refresh groups from server
     */
    async refreshGroups(): Promise<void> {
        await this.listGroups();
    }

    /**
     * List all tags
     */
    async listTags(): Promise<TagInfo[]> {
        const response = await this.backendService.get<TagInfo[]>('/artifacts/tags/list');
        if (response.data) {
            this.tags = response.data;
            this.onTagsChangedEmitter.fire(this.tags);
            return this.tags;
        }
        return [];
    }

    /**
     * Refresh tags from server
     */
    async refreshTags(): Promise<void> {
        await this.listTags();
    }

    /**
     * List shared artifacts
     */
    async listSharedArtifacts(): Promise<Artifact[]> {
        const response = await this.backendService.get<ArtifactsListResponse>('/artifacts/shared/list');
        if (response.data) {
            return response.data.artifacts;
        }
        return [];
    }

    /**
     * Get cached artifacts
     */
    getArtifacts(): Artifact[] {
        return this.artifacts;
    }

    /**
     * Get cached groups
     */
    getGroups(): GroupInfo[] {
        return this.groups;
    }

    /**
     * Get cached tags
     */
    getTags(): TagInfo[] {
        return this.tags;
    }

    /**
     * Get download URL for an artifact
     */
    getDownloadUrl(artifactId: string): string {
        return `http://localhost:8080/api/v1/artifacts/${artifactId}/download`;
    }
}

