/**
 * MLFlow Service
 * 
 * Provides MLFlow experiment and run management functionality.
 */

import { injectable, inject } from '@theia/core/shared/inversify';
import { Emitter, Event } from '@theia/core/lib/common';
import { AgenticBackendService, AgenticBackendServiceSymbol, AgenticWebSocketClient, AgenticWebSocketClientSymbol } from 'agentic-core/lib/browser';

export const MLFlowServiceSymbol = Symbol('MLFlowService');

export interface Experiment {
    experiment_id: string;
    name: string;
    description?: string;
    artifact_location?: string;
    lifecycle_stage: string;
    tags: Record<string, string>;
    creation_time?: string;
    last_update_time?: string;
}

export interface Run {
    run_id: string;
    experiment_id: string;
    run_name?: string;
    status: string;
    start_time?: string;
    end_time?: string;
    artifact_uri?: string;
    metrics: Record<string, number>;
    params: Record<string, string>;
    tags: Record<string, string>;
}

export interface ExperimentsListResponse {
    experiments: Experiment[];
    total: number;
}

export interface RunsListResponse {
    runs: Run[];
    total: number;
}

@injectable()
export class MLFlowService {

    @inject(AgenticBackendServiceSymbol)
    protected readonly backendService: AgenticBackendService;

    @inject(AgenticWebSocketClientSymbol)
    protected readonly wsClient: AgenticWebSocketClient;

    protected experiments: Experiment[] = [];
    protected activeExperiment: Experiment | undefined;
    protected experimentRuns: Map<string, Run[]> = new Map();

    protected readonly onExperimentsChangedEmitter = new Emitter<Experiment[]>();
    readonly onExperimentsChanged: Event<Experiment[]> = this.onExperimentsChangedEmitter.event;

    protected readonly onActiveExperimentChangedEmitter = new Emitter<Experiment | undefined>();
    readonly onActiveExperimentChanged: Event<Experiment | undefined> = this.onActiveExperimentChangedEmitter.event;

    protected readonly onRunsChangedEmitter = new Emitter<{ experimentId: string; runs: Run[] }>();
    readonly onRunsChanged: Event<{ experimentId: string; runs: Run[] }> = this.onRunsChangedEmitter.event;

    constructor() {
        // Will be initialized after injection
    }

    protected initialize(): void {
        // Listen for WebSocket events
        this.wsClient.onExperimentEvent(message => {
            this.handleExperimentEvent(message);
        });
    }

    protected handleExperimentEvent(message: { type: string; data: Record<string, unknown> }): void {
        switch (message.type) {
            case 'experiment.created':
            case 'experiment.updated':
            case 'experiment.deleted':
                this.refreshExperiments();
                break;
            case 'run.started':
            case 'run.ended':
                const experimentId = message.data.experiment_id as string;
                if (experimentId) {
                    this.refreshRuns(experimentId);
                }
                break;
        }
    }

    /**
     * List all experiments
     */
    async listExperiments(): Promise<Experiment[]> {
        const response = await this.backendService.get<ExperimentsListResponse>('/experiments');
        if (response.data) {
            this.experiments = response.data.experiments;
            this.onExperimentsChangedEmitter.fire(this.experiments);
            return this.experiments;
        }
        return [];
    }

    /**
     * Refresh experiments from server
     */
    async refreshExperiments(): Promise<void> {
        await this.listExperiments();
    }

    /**
     * Get a specific experiment
     */
    async getExperiment(experimentId: string): Promise<Experiment | undefined> {
        const response = await this.backendService.get<Experiment>(`/experiments/${experimentId}`);
        return response.data;
    }

    /**
     * Create a new experiment
     */
    async createExperiment(name: string, description?: string): Promise<Experiment | undefined> {
        const response = await this.backendService.post<Experiment>('/experiments', {
            name,
            description
        });
        if (response.data) {
            await this.refreshExperiments();
            return response.data;
        }
        return undefined;
    }

    /**
     * Delete an experiment
     */
    async deleteExperiment(experimentId: string): Promise<boolean> {
        const response = await this.backendService.delete(`/experiments/${experimentId}`);
        if (response.status === 200) {
            await this.refreshExperiments();
            return true;
        }
        return false;
    }

    /**
     * Set the active experiment
     */
    setActiveExperiment(experiment: Experiment | undefined): void {
        this.activeExperiment = experiment;
        this.onActiveExperimentChangedEmitter.fire(experiment);
    }

    /**
     * Get the active experiment
     */
    getActiveExperiment(): Experiment | undefined {
        return this.activeExperiment;
    }

    /**
     * List runs for an experiment
     */
    async listRuns(experimentId: string): Promise<Run[]> {
        const response = await this.backendService.get<RunsListResponse>(`/experiments/${experimentId}/runs`);
        if (response.data) {
            const runs = response.data.runs;
            this.experimentRuns.set(experimentId, runs);
            this.onRunsChangedEmitter.fire({ experimentId, runs });
            return runs;
        }
        return [];
    }

    /**
     * Refresh runs for an experiment
     */
    async refreshRuns(experimentId: string): Promise<void> {
        await this.listRuns(experimentId);
    }

    /**
     * Get a specific run
     */
    async getRun(runId: string): Promise<Run | undefined> {
        const response = await this.backendService.get<Run>(`/experiments/runs/${runId}`);
        return response.data;
    }

    /**
     * Create a new run in an experiment
     */
    async createRun(experimentId: string, runName?: string): Promise<Run | undefined> {
        const response = await this.backendService.post<Run>(`/experiments/${experimentId}/runs`, {
            run_name: runName
        });
        if (response.data) {
            await this.refreshRuns(experimentId);
            return response.data;
        }
        return undefined;
    }

    /**
     * End a run
     */
    async endRun(runId: string, status: string = 'FINISHED'): Promise<boolean> {
        const response = await this.backendService.post(`/experiments/runs/${runId}/end`, { status });
        return response.status === 200;
    }

    /**
     * Log metrics to a run
     */
    async logMetrics(runId: string, metrics: Record<string, number>, step?: number): Promise<boolean> {
        const response = await this.backendService.post(`/experiments/runs/${runId}/metrics`, {
            metrics,
            step
        });
        return response.status === 200;
    }

    /**
     * Log parameters to a run
     */
    async logParams(runId: string, params: Record<string, string>): Promise<boolean> {
        const response = await this.backendService.post(`/experiments/runs/${runId}/params`, {
            params
        });
        return response.status === 200;
    }

    /**
     * Get cached experiments
     */
    getExperiments(): Experiment[] {
        return this.experiments;
    }

    /**
     * Get cached runs for an experiment
     */
    getRuns(experimentId: string): Run[] {
        return this.experimentRuns.get(experimentId) || [];
    }
}

