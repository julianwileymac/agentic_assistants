/**
 * MLFlow Service
 *
 * Provides MLFlow experiment and run management functionality via REST API.
 */

import { Signal, ISignal } from '@lumino/signaling';
import { Poll } from '@lumino/polling';

/**
 * Experiment interface
 */
export interface IExperiment {
  experiment_id: string;
  name: string;
  description?: string;
  artifact_location?: string;
  lifecycle_stage: string;
  tags: Record<string, string>;
  creation_time?: string;
  last_update_time?: string;
}

/**
 * Run interface
 */
export interface IRun {
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

/**
 * Experiments list response
 */
interface IExperimentsResponse {
  experiments: IExperiment[];
  total: number;
}

/**
 * Runs list response
 */
interface IRunsResponse {
  runs: IRun[];
  total: number;
}

/**
 * MLFlow Service class
 */
export class MLFlowService {
  private _experiments: IExperiment[] = [];
  private _activeExperiment: IExperiment | null = null;
  private _activeRun: IRun | null = null;
  private _experimentRuns: Map<string, IRun[]> = new Map();

  private _experimentsChanged = new Signal<this, IExperiment[]>(this);
  private _activeExperimentChanged = new Signal<this, IExperiment | null>(this);
  private _runsChanged = new Signal<this, { experimentId: string; runs: IRun[] }>(this);
  private _activeRunChanged = new Signal<this, IRun | null>(this);
  private _connectionStatus = new Signal<this, 'connected' | 'disconnected' | 'error'>(this);

  private _baseUrl: string;
  private _mlflowUIUrl: string;
  private _poll: Poll | null = null;
  private _isConnected: boolean = false;

  constructor() {
    // Get backend URL from environment or default
    this._baseUrl = this._getBackendUrl();
    this._mlflowUIUrl = this._getMLFlowUIUrl();

    // Start polling for updates
    this._startPolling();

    // Initial fetch
    this.refreshExperiments();
  }

  /**
   * Get backend API URL
   */
  private _getBackendUrl(): string {
    // Check for environment variable or use default
    const envUrl = (window as any).__AGENTIC_BACKEND_URL__;
    if (envUrl) {
      return envUrl;
    }
    // Default to localhost:8080
    return 'http://localhost:8080';
  }

  /**
   * Get MLFlow UI URL
   */
  private _getMLFlowUIUrl(): string {
    const envUrl = (window as any).__MLFLOW_TRACKING_URI__;
    if (envUrl) {
      return envUrl;
    }
    return 'http://localhost:5000';
  }

  /**
   * Get the MLFlow UI URL
   */
  getMLFlowUIUrl(): string {
    return this._mlflowUIUrl;
  }

  /**
   * Start polling for updates
   */
  private _startPolling(): void {
    this._poll = new Poll({
      auto: true,
      factory: async () => {
        await this.refreshExperiments();
      },
      frequency: {
        interval: 30000, // 30 seconds
        backoff: true,
        max: 60000
      },
      name: 'mlflow-poll'
    });
  }

  /**
   * Stop polling
   */
  dispose(): void {
    if (this._poll) {
      this._poll.dispose();
      this._poll = null;
    }
  }

  /**
   * Signal emitted when experiments list changes
   */
  get experimentsChanged(): ISignal<this, IExperiment[]> {
    return this._experimentsChanged;
  }

  /**
   * Signal emitted when active experiment changes
   */
  get activeExperimentChanged(): ISignal<this, IExperiment | null> {
    return this._activeExperimentChanged;
  }

  /**
   * Signal emitted when runs list changes
   */
  get runsChanged(): ISignal<this, { experimentId: string; runs: IRun[] }> {
    return this._runsChanged;
  }

  /**
   * Signal emitted when active run changes
   */
  get activeRunChanged(): ISignal<this, IRun | null> {
    return this._activeRunChanged;
  }

  /**
   * Signal emitted when connection status changes
   */
  get connectionStatus(): ISignal<this, 'connected' | 'disconnected' | 'error'> {
    return this._connectionStatus;
  }

  /**
   * Get current experiments
   */
  get experiments(): IExperiment[] {
    return this._experiments;
  }

  /**
   * Get active experiment
   */
  getActiveExperiment(): IExperiment | null {
    return this._activeExperiment;
  }

  /**
   * Get active run
   */
  getActiveRun(): IRun | null {
    return this._activeRun;
  }

  /**
   * Check if connected to backend
   */
  get isConnected(): boolean {
    return this._isConnected;
  }

  /**
   * Fetch experiments from API
   */
  async refreshExperiments(): Promise<IExperiment[]> {
    try {
      const response = await fetch(`${this._baseUrl}/experiments`);
      if (!response.ok) {
        throw new Error(`HTTP error: ${response.status}`);
      }
      const data: IExperimentsResponse = await response.json();
      this._experiments = data.experiments;
      this._isConnected = true;
      this._connectionStatus.emit('connected');
      this._experimentsChanged.emit(this._experiments);
      return this._experiments;
    } catch (error) {
      console.error('Failed to fetch experiments:', error);
      this._isConnected = false;
      this._connectionStatus.emit('error');
      return [];
    }
  }

  /**
   * Get experiment by ID
   */
  async getExperiment(experimentId: string): Promise<IExperiment | null> {
    try {
      const response = await fetch(`${this._baseUrl}/experiments/${experimentId}`);
      if (!response.ok) {
        throw new Error(`HTTP error: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Failed to get experiment:', error);
      return null;
    }
  }

  /**
   * Create a new experiment
   */
  async createExperiment(name: string, description?: string): Promise<IExperiment | null> {
    try {
      const response = await fetch(`${this._baseUrl}/experiments`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ name, description })
      });
      if (!response.ok) {
        throw new Error(`HTTP error: ${response.status}`);
      }
      const experiment = await response.json();
      await this.refreshExperiments();
      return experiment;
    } catch (error) {
      console.error('Failed to create experiment:', error);
      return null;
    }
  }

  /**
   * Delete an experiment
   */
  async deleteExperiment(experimentId: string): Promise<boolean> {
    try {
      const response = await fetch(`${this._baseUrl}/experiments/${experimentId}`, {
        method: 'DELETE'
      });
      if (!response.ok) {
        throw new Error(`HTTP error: ${response.status}`);
      }
      await this.refreshExperiments();
      return true;
    } catch (error) {
      console.error('Failed to delete experiment:', error);
      return false;
    }
  }

  /**
   * Set active experiment
   */
  setActiveExperiment(experiment: IExperiment | null): void {
    this._activeExperiment = experiment;
    this._activeExperimentChanged.emit(experiment);
    if (experiment) {
      this.refreshRuns(experiment.experiment_id);
    }
  }

  /**
   * Fetch runs for an experiment
   */
  async refreshRuns(experimentId: string): Promise<IRun[]> {
    try {
      const response = await fetch(`${this._baseUrl}/experiments/${experimentId}/runs`);
      if (!response.ok) {
        throw new Error(`HTTP error: ${response.status}`);
      }
      const data: IRunsResponse = await response.json();
      this._experimentRuns.set(experimentId, data.runs);
      this._runsChanged.emit({ experimentId, runs: data.runs });
      return data.runs;
    } catch (error) {
      console.error('Failed to fetch runs:', error);
      return [];
    }
  }

  /**
   * Get runs for an experiment
   */
  getRuns(experimentId: string): IRun[] {
    return this._experimentRuns.get(experimentId) || [];
  }

  /**
   * Create a new run
   */
  async createRun(experimentId: string, runName?: string): Promise<IRun | null> {
    try {
      const response = await fetch(`${this._baseUrl}/experiments/${experimentId}/runs`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ run_name: runName })
      });
      if (!response.ok) {
        throw new Error(`HTTP error: ${response.status}`);
      }
      const run = await response.json();
      this._activeRun = run;
      this._activeRunChanged.emit(run);
      await this.refreshRuns(experimentId);
      return run;
    } catch (error) {
      console.error('Failed to create run:', error);
      return null;
    }
  }

  /**
   * End a run
   */
  async endRun(runId: string, status: string = 'FINISHED'): Promise<boolean> {
    try {
      const response = await fetch(`${this._baseUrl}/experiments/runs/${runId}/end`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ status })
      });
      if (!response.ok) {
        throw new Error(`HTTP error: ${response.status}`);
      }
      if (this._activeRun?.run_id === runId) {
        this._activeRun = null;
        this._activeRunChanged.emit(null);
      }
      if (this._activeExperiment) {
        await this.refreshRuns(this._activeExperiment.experiment_id);
      }
      return true;
    } catch (error) {
      console.error('Failed to end run:', error);
      return false;
    }
  }

  /**
   * Log metrics to a run
   */
  async logMetrics(
    runId: string,
    metrics: Record<string, number>,
    step?: number
  ): Promise<boolean> {
    try {
      const response = await fetch(`${this._baseUrl}/experiments/runs/${runId}/metrics`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ metrics, step })
      });
      return response.ok;
    } catch (error) {
      console.error('Failed to log metrics:', error);
      return false;
    }
  }

  /**
   * Log parameters to a run
   */
  async logParams(runId: string, params: Record<string, string>): Promise<boolean> {
    try {
      const response = await fetch(`${this._baseUrl}/experiments/runs/${runId}/params`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ params })
      });
      return response.ok;
    } catch (error) {
      console.error('Failed to log params:', error);
      return false;
    }
  }

  /**
   * Delete a run
   */
  async deleteRun(runId: string): Promise<boolean> {
    try {
      const response = await fetch(`${this._baseUrl}/experiments/runs/${runId}`, {
        method: 'DELETE'
      });
      if (this._activeExperiment) {
        await this.refreshRuns(this._activeExperiment.experiment_id);
      }
      return response.ok;
    } catch (error) {
      console.error('Failed to delete run:', error);
      return false;
    }
  }
}

