# Chunk: a58fbb8d5ef2_0

- source: `.venv-lab/share/jupyter/lab/schemas/@jupyterlab/workspaces-extension/sidebar.json`
- lines: 1-52
- chunk: 1/1

```
{
  "title": "Workspaces Sidebar",
  "description": "Workspaces Sidebar",
  "jupyter.lab.menus": {
    "context": [
      {
        "command": "workspace-ui:clone",
        "selector": ".jp-RunningSessions-item.jp-mod-workspace",
        "rank": 0
      },
      {
        "command": "workspace-ui:rename",
        "selector": ".jp-RunningSessions-item.jp-mod-workspace",
        "rank": 1
      },
      {
        "command": "workspace-ui:reset",
        "selector": ".jp-RunningSessions-item.jp-mod-workspace",
        "rank": 2
      },
      {
        "command": "workspace-ui:delete",
        "selector": ".jp-RunningSessions-item.jp-mod-workspace",
        "rank": 3
      },
      {
        "command": "workspace-ui:export",
        "selector": ".jp-RunningSessions-item.jp-mod-workspace",
        "rank": 4
      },
      {
        "type": "separator",
        "selector": ".jp-RunningSessions-item.jp-mod-workspace",
        "rank": 5
      },
      {
        "command": "workspace-ui:import",
        "selector": ".jp-RunningSessions-section:has(.jp-mod-workspace)",
        "rank": 6
      },
      {
        "command": "workspace-ui:create-new",
        "selector": ".jp-RunningSessions-section:has(.jp-mod-workspace)",
        "rank": 7
      }
    ]
  },
  "properties": {},
  "additionalProperties": false,
  "type": "object"
}
```
