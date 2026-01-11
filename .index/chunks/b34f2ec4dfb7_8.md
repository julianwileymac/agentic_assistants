# Chunk: b34f2ec4dfb7_8

- source: `frontend/browser-app/lib/frontend/C_Users_Julian_Wiley_Documents_GitHub_agentic_assistants_frontend_packages_agentic-mlflow_lib-255529.js`
- lines: 366-445
- chunk: 9/16

```
w.refreshExperiments',
        label: 'Refresh Experiments',
        category: MLFLOW_CATEGORY
    };
    MLFlowCommands.CREATE_EXPERIMENT = {
        id: 'mlflow.createExperiment',
        label: 'Create Experiment',
        category: MLFLOW_CATEGORY
    };
    MLFlowCommands.DELETE_EXPERIMENT = {
        id: 'mlflow.deleteExperiment',
        label: 'Delete Experiment',
        category: MLFLOW_CATEGORY
    };
    MLFlowCommands.START_RUN = {
        id: 'mlflow.startRun',
        label: 'Start New Run',
        category: MLFLOW_CATEGORY
    };
    MLFlowCommands.END_RUN = {
        id: 'mlflow.endRun',
        label: 'End Run',
        category: MLFLOW_CATEGORY
    };
    MLFlowCommands.VIEW_RUN_DETAILS = {
        id: 'mlflow.viewRunDetails',
        label: 'View Run Details',
        category: MLFLOW_CATEGORY
    };
    MLFlowCommands.COMPARE_RUNS = {
        id: 'mlflow.compareRuns',
        label: 'Compare Runs',
        category: MLFLOW_CATEGORY
    };
    MLFlowCommands.OPEN_MLFLOW_UI = {
        id: 'mlflow.openUI',
        label: 'Open MLFlow UI',
        category: MLFLOW_CATEGORY
    };
})(MLFlowCommands = exports.MLFlowCommands || (exports.MLFlowCommands = {}));
let MLFlowCommandContribution = class MLFlowCommandContribution {
    registerCommands(registry) {
        registry.registerCommand(MLFlowCommands.REFRESH_EXPERIMENTS, {
            execute: async () => {
                try {
                    await this.mlflowService.refreshExperiments();
                    this.messageService.info('Experiments refreshed');
                }
                catch (error) {
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
                        }
                        else {
                            this.messageService.error('Failed to create experiment');
                        }
                    }
                    catch (error) {
                        this.messageService.error('Error creating experiment: ' + error);
                    }
                }
            }
        });
        registry.registerCommand(MLFlowCommands.DELETE_EXPERIMENT, {
            execute: async () => {
                const experiments = this.mlflowService.getExperiments();
                if (experiments.length === 0) {
```
