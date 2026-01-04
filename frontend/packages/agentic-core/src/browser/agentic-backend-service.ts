/**
 * Agentic Backend Service
 * 
 * Provides REST API communication with the Python backend.
 */

import { injectable } from '@theia/core/shared/inversify';
import { Emitter, Event } from '@theia/core/lib/common';

export const AgenticBackendServiceSymbol = Symbol('AgenticBackendService');

export interface AgenticConfig {
    backendUrl: string;
    apiVersion: string;
}

export interface ApiResponse<T> {
    data?: T;
    error?: string;
    status: number;
}

@injectable()
export class AgenticBackendService {

    protected readonly onConnectionChangedEmitter = new Emitter<boolean>();
    readonly onConnectionChanged: Event<boolean> = this.onConnectionChangedEmitter.event;

    protected config: AgenticConfig = {
        backendUrl: 'http://localhost:8080',
        apiVersion: 'v1'
    };

    protected connected: boolean = false;

    /**
     * Configure the backend service
     */
    configure(config: Partial<AgenticConfig>): void {
        this.config = { ...this.config, ...config };
    }

    /**
     * Get the full API URL for an endpoint
     */
    protected getApiUrl(endpoint: string): string {
        return `${this.config.backendUrl}/api/${this.config.apiVersion}${endpoint}`;
    }

    /**
     * Check connection to the backend
     */
    async checkConnection(): Promise<boolean> {
        try {
            const response = await fetch(`${this.config.backendUrl}/health`);
            this.connected = response.ok;
            this.onConnectionChangedEmitter.fire(this.connected);
            return this.connected;
        } catch (error) {
            this.connected = false;
            this.onConnectionChangedEmitter.fire(false);
            return false;
        }
    }

    /**
     * Check if connected to backend
     */
    isConnected(): boolean {
        return this.connected;
    }

    /**
     * Make a GET request
     */
    async get<T>(endpoint: string, params?: Record<string, string>): Promise<ApiResponse<T>> {
        const url = new URL(this.getApiUrl(endpoint));
        if (params) {
            Object.entries(params).forEach(([key, value]) => {
                url.searchParams.append(key, value);
            });
        }

        try {
            const response = await fetch(url.toString(), {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
            });

            if (response.ok) {
                const data = await response.json();
                return { data, status: response.status };
            } else {
                const error = await response.text();
                return { error, status: response.status };
            }
        } catch (error) {
            return { error: String(error), status: 0 };
        }
    }

    /**
     * Make a POST request
     */
    async post<T>(endpoint: string, body?: unknown): Promise<ApiResponse<T>> {
        try {
            const response = await fetch(this.getApiUrl(endpoint), {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: body ? JSON.stringify(body) : undefined,
            });

            if (response.ok) {
                const data = await response.json();
                return { data, status: response.status };
            } else {
                const error = await response.text();
                return { error, status: response.status };
            }
        } catch (error) {
            return { error: String(error), status: 0 };
        }
    }

    /**
     * Make a PATCH request
     */
    async patch<T>(endpoint: string, body?: unknown): Promise<ApiResponse<T>> {
        try {
            const response = await fetch(this.getApiUrl(endpoint), {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: body ? JSON.stringify(body) : undefined,
            });

            if (response.ok) {
                const data = await response.json();
                return { data, status: response.status };
            } else {
                const error = await response.text();
                return { error, status: response.status };
            }
        } catch (error) {
            return { error: String(error), status: 0 };
        }
    }

    /**
     * Make a DELETE request
     */
    async delete<T>(endpoint: string): Promise<ApiResponse<T>> {
        try {
            const response = await fetch(this.getApiUrl(endpoint), {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                },
            });

            if (response.ok) {
                const data = await response.json();
                return { data, status: response.status };
            } else {
                const error = await response.text();
                return { error, status: response.status };
            }
        } catch (error) {
            return { error: String(error), status: 0 };
        }
    }

    // === Experiments API ===

    async listExperiments(): Promise<ApiResponse<unknown>> {
        return this.get('/experiments');
    }

    async getExperiment(id: string): Promise<ApiResponse<unknown>> {
        return this.get(`/experiments/${id}`);
    }

    async createExperiment(name: string, description?: string): Promise<ApiResponse<unknown>> {
        return this.post('/experiments', { name, description });
    }

    async listRuns(experimentId: string): Promise<ApiResponse<unknown>> {
        return this.get(`/experiments/${experimentId}/runs`);
    }

    // === Artifacts API ===

    async listArtifacts(params?: Record<string, string>): Promise<ApiResponse<unknown>> {
        return this.get('/artifacts', params);
    }

    async getArtifact(id: string): Promise<ApiResponse<unknown>> {
        return this.get(`/artifacts/${id}`);
    }

    // === Sessions API ===

    async listSessions(): Promise<ApiResponse<unknown>> {
        return this.get('/sessions');
    }

    async getSession(id: string): Promise<ApiResponse<unknown>> {
        return this.get(`/sessions/${id}`);
    }

    async createSession(name: string, description?: string): Promise<ApiResponse<unknown>> {
        return this.post('/sessions', { name, description });
    }

    async activateSession(id: string): Promise<ApiResponse<unknown>> {
        return this.post(`/sessions/${id}/activate`);
    }

    // === Config API ===

    async getConfig(): Promise<ApiResponse<unknown>> {
        return this.get('/config');
    }

    async updateConfig(section: string, updates: unknown): Promise<ApiResponse<unknown>> {
        return this.patch(`/config/${section}`, updates);
    }

    // === Data API ===

    async listFiles(path?: string): Promise<ApiResponse<unknown>> {
        return this.get('/data/files', path ? { path } : undefined);
    }

    async previewTable(path: string, offset?: number, limit?: number): Promise<ApiResponse<unknown>> {
        const params: Record<string, string> = { path };
        if (offset !== undefined) params.offset = String(offset);
        if (limit !== undefined) params.limit = String(limit);
        return this.get('/data/preview', params);
    }

    async getSchema(path: string): Promise<ApiResponse<unknown>> {
        return this.get('/data/schema', { path });
    }
}

