/**
 * MLFlow Command Contribution
 * 
 * Provides commands for MLFlow experiment management.
 */

import { injectable, inject } from '@theia/core/shared/inversify';
import { CommandContribution, CommandRegistry, Command } from '@theia/core/lib/common';
import { MessageService, QuickInputService } from '@theia/core';
import { MLFlowService, MLFlowServiceSymbol } from './mlflow-service';

export namespace MLFlowCommands {
    const MLFLOW_CATEGORY = 'MLFlow';

    export const TOGGLE_EXPERIMENTS_VIEW: Command = {
        id: 'mlflow.toggleExperimentsView',
        label: 'Toggle Experiments View',
        category: MLFLOW_CATEGORY
    };

    export const REFRESH_EXPERIMENTS: Command = {
        id: 'mlflow.refreshExperiments',
        label: 'Refresh Experiments',
        category: MLFLOW_CATEGORY
    };

    export const CREATE_EXPERIMENT: Command = {
        id: 'mlflow.createExperiment',
        label: 'Create Experiment',
        category: MLFLOW_CATEGORY
    };

    export const DELETE_EXPERIMENT: Command = {
        id: 'mlflow.deleteExperiment',
        label: 'Delete Experiment',
        category: MLFLOW_CATEGORY
    };

    export const START_RUN: Command = {
        id: 'mlflow.startRun',
        label: 'Start New Run',
        category: MLFLOW_CATEGORY
    };

    export const END_RUN: Command = {
        id: 'mlflow.endRun',
        label: 'End Run',
        category: MLFLOW_CATEGORY
    };

    export const VIEW_RUN_DETAILS: Command = {
        id: 'mlflow.viewRunDetails',
        label: 'View Run Details',
        category: MLFLOW_CATEGORY
    };

    export const COMPARE_RUNS: Command = {
        id: 'mlflow.compareRuns',
        label: 'Compare Runs',
        category: MLFLOW_CATEGORY
    };

    export const OPEN_MLFLOW_UI: Command = {
        id: 'mlflow.openUI',
        label: 'Open MLFlow UI',
        category: MLFLOW_CATEGORY
    };
}

@injectable()
export class MLFlowCommandContribution implements CommandContribution {

    @inject(MLFlowServiceSymbol)
    protected readonly mlflowService: MLFlowService;

    @inject(MessageService)
    protected readonly messageService: MessageService;

    @inject(QuickInputService)
    protected readonly quickInputService: QuickInputService;

    registerCommands(registry: CommandRegistry): void {
        registry.registerCommand(MLFlowCommands.REFRESH_EXPERIMENTS, {
            execute: async () => {
                try {
                    await this.mlflowService.refreshExperiments();
                    this.messageService.info('Experiments refreshed');
                } catch (error) {
                    this.messageService.error('Failed to refresh experiments: ' + error);
                }
            }
        });

        registry.registerCommand(MLFlowCommands.CREATE_EXPERIMENT, {
            execute: async () => {
                const name = await this.quickInputService.input({
                    prompt: 'Enter experiment name',
                    placeHolder: 'My Experiment'
                });

                if (name) {
                    try {
                        const experiment = await this.mlflowService.createExperiment(name);
                        if (experiment) {
                            this.messageService.info('Created experiment: ' + experiment.name);
                        } else {
                            this.messageService.error('Failed to create experiment');
                        }
                    } catch (error) {
                        this.messageService.error('Error creating experiment: ' + error);
                    }
                }
            }
        });

        registry.registerCommand(MLFlowCommands.DELETE_EXPERIMENT, {
            execute: async () => {
                const experiments = this.mlflowService.getExperiments();
                if (experiments.length === 0) {
                    this.messageService.info('No experiments to delete');
                    return;
                }

                const items = experiments.map(exp => ({
                    label: exp.name,
                    description: exp.experiment_id,
                    experiment: exp
                }));

                const selected = await this.quickInputService.pick(items, {
                    placeHolder: 'Select experiment to delete'
                });

                if (selected && 'experiment' in selected) {
                    const confirm = await this.quickInputService.input({
                        prompt: `Type "${selected.experiment.name}" to confirm deletion`,
                        placeHolder: selected.experiment.name
                    });

                    if (confirm === selected.experiment.name) {
                        const success = await this.mlflowService.deleteExperiment(selected.experiment.experiment_id);
                        if (success) {
                            this.messageService.info('Deleted experiment: ' + selected.experiment.name);
                        } else {
                            this.messageService.error('Failed to delete experiment');
                        }
                    }
                }
            }
        });

        registry.registerCommand(MLFlowCommands.START_RUN, {
            execute: async () => {
                const activeExperiment = this.mlflowService.getActiveExperiment();
                if (!activeExperiment) {
                    this.messageService.warn('Please select an experiment first');
                    return;
                }

                const runName = await this.quickInputService.input({
                    prompt: 'Enter run name (optional)',
                    placeHolder: 'My Run'
                });

                try {
                    const run = await this.mlflowService.createRun(activeExperiment.experiment_id, runName || undefined);
                    if (run) {
                        this.messageService.info('Started run: ' + (run.run_name || run.run_id));
                    } else {
                        this.messageService.error('Failed to start run');
                    }
                } catch (error) {
                    this.messageService.error('Error starting run: ' + error);
                }
            }
        });

        registry.registerCommand(MLFlowCommands.END_RUN, {
            execute: async () => {
                const activeExperiment = this.mlflowService.getActiveExperiment();
                if (!activeExperiment) {
                    this.messageService.warn('Please select an experiment first');
                    return;
                }

                const runs = this.mlflowService.getRuns(activeExperiment.experiment_id)
                    .filter(run => run.status === 'RUNNING');

                if (runs.length === 0) {
                    this.messageService.info('No running runs to end');
                    return;
                }

                const items = runs.map(run => ({
                    label: run.run_name || run.run_id,
                    description: `Started: ${run.start_time}`,
                    run
                }));

                const selected = await this.quickInputService.pick(items, {
                    placeHolder: 'Select run to end'
                });

                if (selected && 'run' in selected) {
                    const statusItems = [
                        { label: 'FINISHED', description: 'Run completed successfully' },
                        { label: 'FAILED', description: 'Run failed with an error' },
                        { label: 'KILLED', description: 'Run was terminated' }
                    ];

                    const status = await this.quickInputService.pick(statusItems, {
                        placeHolder: 'Select final status'
                    });

                    if (status) {
                        const success = await this.mlflowService.endRun(selected.run.run_id, status.label);
                        if (success) {
                            this.messageService.info('Ended run with status: ' + status.label);
                        } else {
                            this.messageService.error('Failed to end run');
                        }
                    }
                }
            }
        });

        registry.registerCommand(MLFlowCommands.OPEN_MLFLOW_UI, {
            execute: () => {
                // Open MLFlow UI in a new browser tab
                window.open('http://localhost:5000', '_blank');
            }
        });
    }
}

