# Chunk: dfd019daa9b8_0

- source: `.venv-lab/share/jupyter/lab/schemas/@jupyterlab/console-extension/tracker.json`
- lines: 1-114
- chunk: 1/3

```
{
  "title": "Code Console",
  "description": "Code Console settings.",
  "jupyter.lab.setting-icon": "ui-components:console",
  "jupyter.lab.setting-icon-label": "Code Console Settings",
  "jupyter.lab.menus": {
    "main": [
      {
        "id": "jp-mainmenu-file",
        "items": [
          {
            "type": "submenu",
            "submenu": {
              "id": "jp-mainmenu-file-new",
              "items": [
                {
                  "command": "console:create",
                  "rank": 1
                }
              ]
            }
          }
        ]
      },
      {
        "id": "jp-mainmenu-settings",
        "items": [
          {
            "type": "separator",
            "rank": 9
          },
          {
            "type": "submenu",
            "submenu": {
              "id": "jp-mainmenu-settings-consoleexecute",
              "label": "Console Run Keystroke",
              "items": [
                {
                  "command": "console:interaction-mode",
                  "args": {
                    "interactionMode": "terminal"
                  }
                },
                {
                  "command": "console:interaction-mode",
                  "args": {
                    "interactionMode": "notebook"
                  }
                }
              ]
            },
            "rank": 9
          },
          {
            "type": "separator",
            "rank": 9
          }
        ]
      }
    ],
    "context": [
      {
        "command": "console:undo",
        "selector": ".jp-CodeConsole-promptCell",
        "rank": 1
      },
      {
        "command": "console:redo",
        "selector": ".jp-CodeConsole-promptCell",
        "rank": 2
      },
      {
        "command": "console:clear",
        "selector": ".jp-CodeConsole-content",
        "rank": 10
      },
      {
        "command": "console:restart-kernel",
        "selector": ".jp-CodeConsole",
        "rank": 30
      }
    ]
  },
  "jupyter.lab.shortcuts": [
    {
      "command": "console:run-forced",
      "keys": ["Shift Enter"],
      "selector": ".jp-CodeConsole[data-jp-interaction-mode='notebook'] .jp-CodeConsole-promptCell"
    },
    {
      "command": "console:linebreak",
      "keys": ["Accel Enter"],
      "selector": ".jp-CodeConsole[data-jp-interaction-mode='terminal'] .jp-CodeConsole-promptCell"
    },
    {
      "command": "console:run-forced",
      "keys": ["Shift Enter"],
      "selector": ".jp-CodeConsole[data-jp-interaction-mode='terminal'] .jp-CodeConsole-promptCell"
    },
    {
      "command": "console:run-unforced",
      "keys": ["Enter"],
      "selector": ".jp-CodeConsole[data-jp-interaction-mode='terminal'] .jp-CodeConsole-promptCell"
    }
  ],
  "jupyter.lab.toolbars": {
    "ConsolePanel": [
      {
        "name": "run",
        "command": "console:run-forced",
        "rank": 0
      },
      { "name": "restart", "command": "console:restart-kernel", "rank": 10 },
```
