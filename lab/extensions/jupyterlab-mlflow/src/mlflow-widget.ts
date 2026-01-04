/**
 * MLFlow Widget
 *
 * Sidebar widget for viewing and managing MLFlow experiments and runs.
 */

import { Widget } from '@lumino/widgets';
import { Message } from '@lumino/messaging';
import { MLFlowService, IExperiment, IRun } from './mlflow-service';

/**
 * CSS class names
 */
const CLASSES = {
  container: 'jp-MLFlow-container',
  header: 'jp-MLFlow-header',
  headerTitle: 'jp-MLFlow-header-title',
  toolbar: 'jp-MLFlow-toolbar',
  toolbarButton: 'jp-MLFlow-toolbar-button',
  content: 'jp-MLFlow-content',
  status: 'jp-MLFlow-status',
  statusConnected: 'jp-MLFlow-status-connected',
  statusDisconnected: 'jp-MLFlow-status-disconnected',
  experimentList: 'jp-MLFlow-experiment-list',
  experimentItem: 'jp-MLFlow-experiment-item',
  experimentItemActive: 'jp-MLFlow-experiment-item-active',
  experimentName: 'jp-MLFlow-experiment-name',
  experimentMeta: 'jp-MLFlow-experiment-meta',
  runList: 'jp-MLFlow-run-list',
  runItem: 'jp-MLFlow-run-item',
  runItemActive: 'jp-MLFlow-run-item-active',
  runName: 'jp-MLFlow-run-name',
  runStatus: 'jp-MLFlow-run-status',
  runStatusRunning: 'jp-MLFlow-run-status-running',
  runStatusFinished: 'jp-MLFlow-run-status-finished',
  runStatusFailed: 'jp-MLFlow-run-status-failed',
  metricsContainer: 'jp-MLFlow-metrics-container',
  metric: 'jp-MLFlow-metric',
  emptyMessage: 'jp-MLFlow-empty-message',
  section: 'jp-MLFlow-section',
  sectionTitle: 'jp-MLFlow-section-title'
};

/**
 * MLFlow Widget class
 */
export class MLFlowWidget extends Widget {
  private _service: MLFlowService;
  private _statusEl: HTMLElement | null = null;
  private _experimentListEl: HTMLElement | null = null;
  private _runListEl: HTMLElement | null = null;
  private _metricsEl: HTMLElement | null = null;

  constructor(service: MLFlowService) {
    super();
    this._service = service;
    this.addClass(CLASSES.container);
    this.id = 'mlflow-widget';
    this.title.label = 'MLFlow';
    this.title.closable = true;

    // Create the UI
    this._createUI();

    // Connect to signals
    this._service.experimentsChanged.connect(this._onExperimentsChanged, this);
    this._service.activeExperimentChanged.connect(this._onActiveExperimentChanged, this);
    this._service.runsChanged.connect(this._onRunsChanged, this);
    this._service.connectionStatus.connect(this._onConnectionStatusChanged, this);
  }

  /**
   * Create the widget UI
   */
  private _createUI(): void {
    // Header
    const header = document.createElement('div');
    header.className = CLASSES.header;

    const title = document.createElement('h2');
    title.className = CLASSES.headerTitle;
    title.textContent = 'MLFlow Experiments';
    header.appendChild(title);

    // Status indicator
    this._statusEl = document.createElement('span');
    this._statusEl.className = `${CLASSES.status} ${CLASSES.statusDisconnected}`;
    this._statusEl.textContent = 'Disconnected';
    header.appendChild(this._statusEl);

    this.node.appendChild(header);

    // Toolbar
    const toolbar = document.createElement('div');
    toolbar.className = CLASSES.toolbar;

    const refreshBtn = this._createToolbarButton('↻', 'Refresh', async () => {
      await this._service.refreshExperiments();
    });
    toolbar.appendChild(refreshBtn);

    const newExpBtn = this._createToolbarButton('+', 'New Experiment', async () => {
      const name = prompt('Enter experiment name:');
      if (name) {
        await this._service.createExperiment(name);
      }
    });
    toolbar.appendChild(newExpBtn);

    const openUIBtn = this._createToolbarButton('↗', 'Open MLFlow UI', () => {
      window.open(this._service.getMLFlowUIUrl(), '_blank');
    });
    toolbar.appendChild(openUIBtn);

    this.node.appendChild(toolbar);

    // Content
    const content = document.createElement('div');
    content.className = CLASSES.content;

    // Experiments section
    const expSection = document.createElement('div');
    expSection.className = CLASSES.section;

    const expTitle = document.createElement('h3');
    expTitle.className = CLASSES.sectionTitle;
    expTitle.textContent = 'Experiments';
    expSection.appendChild(expTitle);

    this._experimentListEl = document.createElement('div');
    this._experimentListEl.className = CLASSES.experimentList;
    expSection.appendChild(this._experimentListEl);

    content.appendChild(expSection);

    // Runs section
    const runSection = document.createElement('div');
    runSection.className = CLASSES.section;

    const runTitle = document.createElement('h3');
    runTitle.className = CLASSES.sectionTitle;
    runTitle.textContent = 'Runs';
    runSection.appendChild(runTitle);

    this._runListEl = document.createElement('div');
    this._runListEl.className = CLASSES.runList;
    runSection.appendChild(this._runListEl);

    content.appendChild(runSection);

    // Metrics section
    const metricsSection = document.createElement('div');
    metricsSection.className = CLASSES.section;

    const metricsTitle = document.createElement('h3');
    metricsTitle.className = CLASSES.sectionTitle;
    metricsTitle.textContent = 'Metrics';
    metricsSection.appendChild(metricsTitle);

    this._metricsEl = document.createElement('div');
    this._metricsEl.className = CLASSES.metricsContainer;
    metricsSection.appendChild(this._metricsEl);

    content.appendChild(metricsSection);

    this.node.appendChild(content);

    // Initial render
    this._renderExperiments();
    this._renderRuns();
    this._renderMetrics();
  }

  /**
   * Create a toolbar button
   */
  private _createToolbarButton(
    icon: string,
    title: string,
    onClick: () => void
  ): HTMLButtonElement {
    const button = document.createElement('button');
    button.className = CLASSES.toolbarButton;
    button.textContent = icon;
    button.title = title;
    button.addEventListener('click', onClick);
    return button;
  }

  /**
   * Render experiments list
   */
  private _renderExperiments(): void {
    if (!this._experimentListEl) return;

    const experiments = this._service.experiments;
    const activeExp = this._service.getActiveExperiment();

    this._experimentListEl.innerHTML = '';

    if (experiments.length === 0) {
      const empty = document.createElement('div');
      empty.className = CLASSES.emptyMessage;
      empty.textContent = 'No experiments found';
      this._experimentListEl.appendChild(empty);
      return;
    }

    experiments.forEach(exp => {
      const item = document.createElement('div');
      item.className = CLASSES.experimentItem;
      if (activeExp && activeExp.experiment_id === exp.experiment_id) {
        item.classList.add(CLASSES.experimentItemActive);
      }

      const name = document.createElement('div');
      name.className = CLASSES.experimentName;
      name.textContent = exp.name;
      item.appendChild(name);

      const meta = document.createElement('div');
      meta.className = CLASSES.experimentMeta;
      meta.textContent = `ID: ${exp.experiment_id} • ${exp.lifecycle_stage}`;
      item.appendChild(meta);

      item.addEventListener('click', () => {
        this._service.setActiveExperiment(exp);
      });

      // Context menu for delete
      item.addEventListener('contextmenu', async e => {
        e.preventDefault();
        if (confirm(`Delete experiment "${exp.name}"?`)) {
          await this._service.deleteExperiment(exp.experiment_id);
        }
      });

      this._experimentListEl!.appendChild(item);
    });
  }

  /**
   * Render runs list
   */
  private _renderRuns(): void {
    if (!this._runListEl) return;

    const activeExp = this._service.getActiveExperiment();
    const activeRun = this._service.getActiveRun();

    this._runListEl.innerHTML = '';

    if (!activeExp) {
      const empty = document.createElement('div');
      empty.className = CLASSES.emptyMessage;
      empty.textContent = 'Select an experiment';
      this._runListEl.appendChild(empty);
      return;
    }

    const runs = this._service.getRuns(activeExp.experiment_id);

    if (runs.length === 0) {
      const empty = document.createElement('div');
      empty.className = CLASSES.emptyMessage;
      empty.textContent = 'No runs found';

      const newRunBtn = document.createElement('button');
      newRunBtn.className = CLASSES.toolbarButton;
      newRunBtn.textContent = '+ New Run';
      newRunBtn.addEventListener('click', async () => {
        const name = prompt('Enter run name (optional):') || undefined;
        await this._service.createRun(activeExp.experiment_id, name);
      });
      empty.appendChild(document.createElement('br'));
      empty.appendChild(newRunBtn);

      this._runListEl.appendChild(empty);
      return;
    }

    runs.forEach(run => {
      const item = document.createElement('div');
      item.className = CLASSES.runItem;
      if (activeRun && activeRun.run_id === run.run_id) {
        item.classList.add(CLASSES.runItemActive);
      }

      const name = document.createElement('div');
      name.className = CLASSES.runName;
      name.textContent = run.run_name || run.run_id.substring(0, 8);
      item.appendChild(name);

      const status = document.createElement('span');
      status.className = CLASSES.runStatus;
      status.textContent = run.status;
      if (run.status === 'RUNNING') {
        status.classList.add(CLASSES.runStatusRunning);
      } else if (run.status === 'FINISHED') {
        status.classList.add(CLASSES.runStatusFinished);
      } else if (run.status === 'FAILED') {
        status.classList.add(CLASSES.runStatusFailed);
      }
      item.appendChild(status);

      item.addEventListener('click', () => {
        this._renderMetrics(run);
      });

      // Context menu for run actions
      item.addEventListener('contextmenu', async e => {
        e.preventDefault();
        const action = prompt('Action: end, delete');
        if (action === 'end') {
          await this._service.endRun(run.run_id);
        } else if (action === 'delete') {
          if (confirm(`Delete run "${run.run_name || run.run_id}"?`)) {
            await this._service.deleteRun(run.run_id);
          }
        }
      });

      this._runListEl!.appendChild(item);
    });
  }

  /**
   * Render metrics for a run
   */
  private _renderMetrics(run?: IRun): void {
    if (!this._metricsEl) return;

    this._metricsEl.innerHTML = '';

    if (!run) {
      const empty = document.createElement('div');
      empty.className = CLASSES.emptyMessage;
      empty.textContent = 'Select a run to view metrics';
      this._metricsEl.appendChild(empty);
      return;
    }

    const metrics = run.metrics;
    const params = run.params;

    if (Object.keys(metrics).length === 0 && Object.keys(params).length === 0) {
      const empty = document.createElement('div');
      empty.className = CLASSES.emptyMessage;
      empty.textContent = 'No metrics or params logged';
      this._metricsEl.appendChild(empty);
      return;
    }

    // Params
    if (Object.keys(params).length > 0) {
      const paramsTitle = document.createElement('div');
      paramsTitle.style.fontWeight = 'bold';
      paramsTitle.style.marginBottom = '4px';
      paramsTitle.textContent = 'Parameters:';
      this._metricsEl.appendChild(paramsTitle);

      Object.entries(params).forEach(([key, value]) => {
        const metric = document.createElement('div');
        metric.className = CLASSES.metric;
        metric.textContent = `${key}: ${value}`;
        this._metricsEl!.appendChild(metric);
      });
    }

    // Metrics
    if (Object.keys(metrics).length > 0) {
      const metricsTitle = document.createElement('div');
      metricsTitle.style.fontWeight = 'bold';
      metricsTitle.style.marginBottom = '4px';
      metricsTitle.style.marginTop = '8px';
      metricsTitle.textContent = 'Metrics:';
      this._metricsEl.appendChild(metricsTitle);

      Object.entries(metrics).forEach(([key, value]) => {
        const metric = document.createElement('div');
        metric.className = CLASSES.metric;
        metric.textContent = `${key}: ${typeof value === 'number' ? value.toFixed(4) : value}`;
        this._metricsEl!.appendChild(metric);
      });
    }
  }

  /**
   * Handle experiments changed
   */
  private _onExperimentsChanged(): void {
    this._renderExperiments();
  }

  /**
   * Handle active experiment changed
   */
  private _onActiveExperimentChanged(): void {
    this._renderExperiments();
    this._renderRuns();
    this._renderMetrics();
  }

  /**
   * Handle runs changed
   */
  private _onRunsChanged(): void {
    this._renderRuns();
  }

  /**
   * Handle connection status changed
   */
  private _onConnectionStatusChanged(
    _sender: MLFlowService,
    status: 'connected' | 'disconnected' | 'error'
  ): void {
    if (!this._statusEl) return;

    this._statusEl.classList.remove(CLASSES.statusConnected, CLASSES.statusDisconnected);

    switch (status) {
      case 'connected':
        this._statusEl.classList.add(CLASSES.statusConnected);
        this._statusEl.textContent = 'Connected';
        break;
      case 'disconnected':
      case 'error':
        this._statusEl.classList.add(CLASSES.statusDisconnected);
        this._statusEl.textContent = status === 'error' ? 'Error' : 'Disconnected';
        break;
    }
  }

  /**
   * Handle widget activation
   */
  protected onActivateRequest(msg: Message): void {
    this.node.focus();
  }

  /**
   * Dispose of the widget
   */
  dispose(): void {
    this._service.experimentsChanged.disconnect(this._onExperimentsChanged, this);
    this._service.activeExperimentChanged.disconnect(this._onActiveExperimentChanged, this);
    this._service.runsChanged.disconnect(this._onRunsChanged, this);
    this._service.connectionStatus.disconnect(this._onConnectionStatusChanged, this);
    super.dispose();
  }
}

