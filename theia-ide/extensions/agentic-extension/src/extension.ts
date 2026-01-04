import * as vscode from 'vscode';
import axios from 'axios';

export function activate(context: vscode.ExtensionContext) {
    const apiUrl = vscode.workspace.getConfiguration('agentic').get('apiUrl', 'http://localhost:8000');

    // Command: Start MLFlow Experiment
    let startExperiment = vscode.commands.registerCommand('agentic.startExperiment', async () => {
        const name = await vscode.window.showInputBox({ prompt: 'Experiment Name' });
        if (name) {
            try {
                await axios.post(`${apiUrl}/mlflow/experiment/start?name=${name}`);
                vscode.window.showInformationMessage(`Experiment ${name} started`);
            } catch (error) {
                vscode.window.showErrorMessage(`Failed to start experiment: ${error}`);
            }
        }
    });

    // Command: Run Script with Memory Spec
    let runScript = vscode.commands.registerCommand('agentic.runScript', async () => {
        const memory = await vscode.window.showInputBox({ prompt: 'Memory Limit (MB)', value: '1024' });
        const script = await vscode.window.showInputBox({ prompt: 'Script to run' });
        
        if (script) {
            vscode.window.showInformationMessage(`Running ${script} with ${memory}MB memory`);
            // Here we would call the API to run the script
        }
    });

    // Data Layer Provider
    const dataLayerProvider = new DataLayerProvider(apiUrl);
    vscode.window.registerTreeDataProvider('agenticDataLayer', dataLayerProvider);

    context.subscriptions.push(startExperiment, runScript);
}

class DataLayerProvider implements vscode.TreeDataProvider<DataItem> {
    constructor(private apiUrl: string) {}

    getTreeItem(element: DataItem): vscode.TreeItem {
        return element;
    }

    async getChildren(element?: DataItem): Promise<DataItem[]> {
        if (!element) {
            // Root items: list collections or files
            try {
                const response = await axios.get(`${this.apiUrl}/collections`);
                return response.data.collections.map((c: any) => new DataItem(c.name, vscode.TreeItemCollapsibleState.None));
            } catch (error) {
                return [new DataItem("Error loading data", vscode.TreeItemCollapsibleState.None)];
            }
        }
        return [];
    }
}

class DataItem extends vscode.TreeItem {
    constructor(
        public readonly label: string,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState
    ) {
        super(label, collapsibleState);
    }
}
