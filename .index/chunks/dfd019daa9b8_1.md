# Chunk: dfd019daa9b8_1

- source: `.venv-lab/share/jupyter/lab/schemas/@jupyterlab/console-extension/tracker.json`
- lines: 103-183
- chunk: 2/3

```
a-jp-interaction-mode='terminal'] .jp-CodeConsole-promptCell"
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
      { "name": "clear", "command": "console:clear", "rank": 20 },
      { "name": "spacer", "type": "spacer", "rank": 100 },
      { "name": "kernelName", "rank": 1000 },
      { "name": "kernelStatus", "rank": 1010 },
      { "name": "promptPosition", "rank": 1020 }
    ]
  },
  "jupyter.lab.transform": true,
  "properties": {
    "clearCellsOnExecute": {
      "title": "Clear Cells on Execute",
      "description": "Whether to clear the console when code is executed.",
      "type": "boolean",
      "default": false
    },
    "clearCodeContentOnExecute": {
      "title": "Clear Code Content on Execute",
      "description": "Whether to clear the code content of the console when code is executed.",
      "type": "boolean",
      "default": true
    },
    "hideCodeInput": {
      "title": "Hide Code Input",
      "description": "Whether to hide the code input after a cell is executed.",
      "type": "boolean",
      "default": false
    },
    "interactionMode": {
      "title": "Interaction mode",
      "description": "Whether the console interaction mimics the notebook\nor terminal keyboard shortcuts.",
      "type": "string",
      "enum": ["notebook", "terminal"],
      "default": "notebook"
    },
    "showAllKernelActivity": {
      "title": "Show All Kernel Activity",
      "description": "Whether the console defaults to showing all\nkernel activity or just kernel activity originating from itself.",
      "type": "boolean",
      "default": false
    },
    "promptCellConfig": {
      "title": "Prompt Cell Configuration",
      "description": "The configuration for all prompt cells; it will override the CodeMirror default configuration.",
      "type": "object",
      "default": {
        "codeFolding": false,
        "lineNumbers": false
      }
    },
    "promptCellPosition": {
      "title": "Prompt Cell Position",
      "description": "Where to place the prompt cell of the console.",
      "type": "string",
      "oneOf": [
        { "const": "bottom", "title": "Bottom" },
        { "const": "top", "title": "Top" },
        { "const": "left", "title": "Left" },
        { "const": "right", "title": "Right" }
      ],
      "default": "bottom"
    },
    "showBanner": {
      "title": "Show Banner",
      "description": "Whether to show the kernel banner.",
      "type": "boolean",
      "default": true
    },
    "toolbar": {
      "title": "Console panel toolbar items",
```
