# Chunk: f04fda8d54ec_0

- source: `.venv-lab/share/jupyter/lab/schemas/@jupyterlab/tooltip-extension/notebooks.json`
- lines: 1-20
- chunk: 1/1

```
{
  "title": "Notebook Tooltips",
  "description": "Notebook tooltip settings.",
  "jupyter.lab.shortcuts": [
    {
      "command": "tooltip:dismiss",
      "keys": ["Escape"],
      "selector": "body.jp-mod-tooltip .jp-Notebook"
    },
    {
      "command": "tooltip:launch-notebook",
      "keys": ["Shift Tab"],
      "selector": ".jp-Notebook.jp-mod-editMode .jp-InputArea-editor:not(.jp-mod-has-primary-selection):not(.jp-mod-in-leading-whitespace):not(.jp-mod-completer-active)"
    }
  ],
  "properties": {},
  "additionalProperties": false,
  "type": "object"
}
```
