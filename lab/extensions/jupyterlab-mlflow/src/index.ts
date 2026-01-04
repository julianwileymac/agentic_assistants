/**
 * JupyterLab MLFlow Extension
 *
 * Provides sidebar integration for MLFlow experiment management including:
 * - Experiments and runs tree view
 * - Toolbar buttons to start/stop experiments
 * - Context menus for run management
 * - Real-time status updates
 */

import {
  ILayoutRestorer,
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { ICommandPalette, MainAreaWidget } from '@jupyterlab/apputils';

import { ILauncher } from '@jupyterlab/launcher';

import { IMainMenu } from '@jupyterlab/mainmenu';

import { mlflowIcon } from './icons';
import { MLFlowWidget } from './mlflow-widget';
import { MLFlowService } from './mlflow-service';

/**
 * Extension namespace
 */
const NAMESPACE = 'jupyterlab-mlflow';

/**
 * Command IDs
 */
namespace CommandIDs {
  export const open = `${NAMESPACE}:open`;
  export const refresh = `${NAMESPACE}:refresh`;
  export const createExperiment = `${NAMESPACE}:create-experiment`;
  export const startRun = `${NAMESPACE}:start-run`;
  export const endRun = `${NAMESPACE}:end-run`;
  export const openMLFlowUI = `${NAMESPACE}:open-mlflow-ui`;
}

/**
 * The MLFlow extension plugin
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: '@agentic/jupyterlab-mlflow:plugin',
  autoStart: true,
  requires: [ICommandPalette],
  optional: [ILayoutRestorer, ILauncher, IMainMenu],
  activate: (
    app: JupyterFrontEnd,
    palette: ICommandPalette,
    restorer: ILayoutRestorer | null,
    launcher: ILauncher | null,
    mainMenu: IMainMenu | null
  ) => {
    console.log('JupyterLab MLFlow extension is activated!');

    // Create the MLFlow service
    const mlflowService = new MLFlowService();

    // Create the widget
    let widget: MainAreaWidget<MLFlowWidget>;

    const createWidget = (): MainAreaWidget<MLFlowWidget> => {
      const content = new MLFlowWidget(mlflowService);
      const main = new MainAreaWidget({ content });
      main.id = 'mlflow-main';
      main.title.label = 'MLFlow Experiments';
      main.title.icon = mlflowIcon;
      main.title.closable = true;
      return main;
    };

    // Add commands
    app.commands.addCommand(CommandIDs.open, {
      label: 'MLFlow Experiments',
      caption: 'Open MLFlow Experiments Panel',
      icon: mlflowIcon,
      execute: () => {
        if (!widget || widget.isDisposed) {
          widget = createWidget();
        }
        if (!widget.isAttached) {
          app.shell.add(widget, 'left', { rank: 200 });
        }
        app.shell.activateById(widget.id);
      }
    });

    app.commands.addCommand(CommandIDs.refresh, {
      label: 'Refresh Experiments',
      caption: 'Refresh experiments list from MLFlow',
      execute: async () => {
        await mlflowService.refreshExperiments();
      }
    });

    app.commands.addCommand(CommandIDs.createExperiment, {
      label: 'Create New Experiment',
      caption: 'Create a new MLFlow experiment',
      execute: async () => {
        const name = prompt('Enter experiment name:');
        if (name) {
          await mlflowService.createExperiment(name);
        }
      }
    });

    app.commands.addCommand(CommandIDs.startRun, {
      label: 'Start New Run',
      caption: 'Start a new run in the active experiment',
      execute: async () => {
        const activeExperiment = mlflowService.getActiveExperiment();
        if (!activeExperiment) {
          alert('Please select an experiment first');
          return;
        }
        const runName = prompt('Enter run name (optional):') || undefined;
        await mlflowService.createRun(activeExperiment.experiment_id, runName);
      }
    });

    app.commands.addCommand(CommandIDs.endRun, {
      label: 'End Active Run',
      caption: 'End the currently active run',
      execute: async () => {
        const activeRun = mlflowService.getActiveRun();
        if (!activeRun) {
          alert('No active run to end');
          return;
        }
        await mlflowService.endRun(activeRun.run_id);
      }
    });

    app.commands.addCommand(CommandIDs.openMLFlowUI, {
      label: 'Open MLFlow UI',
      caption: 'Open the MLFlow tracking UI in a new tab',
      execute: () => {
        window.open(mlflowService.getMLFlowUIUrl(), '_blank');
      }
    });

    // Add to command palette
    palette.addItem({ command: CommandIDs.open, category: 'MLFlow' });
    palette.addItem({ command: CommandIDs.refresh, category: 'MLFlow' });
    palette.addItem({ command: CommandIDs.createExperiment, category: 'MLFlow' });
    palette.addItem({ command: CommandIDs.startRun, category: 'MLFlow' });
    palette.addItem({ command: CommandIDs.endRun, category: 'MLFlow' });
    palette.addItem({ command: CommandIDs.openMLFlowUI, category: 'MLFlow' });

    // Add to launcher
    if (launcher) {
      launcher.add({
        command: CommandIDs.open,
        category: 'MLOps',
        rank: 1
      });
    }

    // Add to main menu
    if (mainMenu) {
      const mlflowMenu = mainMenu.viewMenu;
      mlflowMenu.addGroup(
        [
          { command: CommandIDs.open },
          { command: CommandIDs.refresh },
          { command: CommandIDs.openMLFlowUI }
        ],
        100
      );
    }

    // Restore widget state
    if (restorer) {
      restorer.restore(app.shell, {
        command: CommandIDs.open,
        name: () => 'mlflow'
      });
    }

    // Auto-open in sidebar
    app.restored.then(() => {
      app.commands.execute(CommandIDs.open);
    });
  }
};

export default plugin;

