# Chunk: b34f2ec4dfb7_9

- source: `frontend/browser-app/lib/frontend/C_Users_Julian_Wiley_Documents_GitHub_agentic_assistants_frontend_packages_agentic-mlflow_lib-255529.js`
- lines: 436-502
- chunk: 10/16

```
 error);
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
                        }
                        else {
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
                    }
                    else {
                        this.messageService.error('Failed to start run');
                    }
                }
                catch (error) {
                    this.messageService.error('Error starting run: ' + error);
                }
            }
        });
        registry.registerCommand(MLFlowCommands.END_RUN, {
            execute: async () => {
                const activeExperiment = this.mlflowService.getActiveExperiment();
                if (!activeExperiment) {
```
