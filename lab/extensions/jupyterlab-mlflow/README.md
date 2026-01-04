# @agentic/jupyterlab-mlflow

JupyterLab extension for MLFlow experiment management.

## Features

- **Sidebar Widget**: View and manage experiments and runs directly in JupyterLab
- **Experiment Management**: Create, delete, and activate experiments
- **Run Management**: Start, end, and monitor runs
- **Metrics Viewer**: View logged metrics and parameters for runs
- **Real-time Updates**: Auto-refresh with configurable polling interval

## Requirements

- JupyterLab >= 4.0.0
- Agentic backend API running (default: http://localhost:8080)
- MLFlow tracking server running (default: http://localhost:5000)

## Installation

```bash
cd lab/extensions/jupyterlab-mlflow
pip install -e .
```

## Development

```bash
# Install development dependencies
jlpm install

# Build the extension
jlpm build

# Link for development
jupyter labextension develop . --overwrite

# Watch for changes
jlpm watch
```

## Configuration

Settings can be configured in JupyterLab's Settings Editor under "MLFlow":

- **Backend URL**: URL of the Agentic backend API server
- **MLFlow UI URL**: URL of the MLFlow tracking UI
- **Poll Interval**: Interval in milliseconds to poll for updates
- **Auto Refresh**: Automatically refresh experiments list

## Usage

1. Click the MLFlow icon in the sidebar to open the panel
2. View and select experiments
3. Click on a run to view its metrics and parameters
4. Use the toolbar buttons to:
   - Refresh the experiments list
   - Create a new experiment
   - Open the MLFlow UI in a new tab

