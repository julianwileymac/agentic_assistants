# Chunk: d1d7dedc8ab5_0

- source: `.venv-lab/share/jupyter/lab/schemas/@jupyter-notebook/application-extension/top.json`
- lines: 1-31
- chunk: 1/1

```
{
  "jupyter.lab.setting-icon": "notebook-ui-components:jupyter",
  "jupyter.lab.setting-icon-label": "Jupyter Notebook Top Area",
  "title": "Jupyter Notebook Top Area",
  "description": "Jupyter Notebook Top Area settings",
  "jupyter.lab.menus": {
    "main": [
      {
        "id": "jp-mainmenu-view",
        "items": [
          {
            "command": "application:toggle-top",
            "rank": 2
          }
        ]
      }
    ]
  },
  "properties": {
    "visible": {
      "type": "string",
      "enum": ["yes", "no", "automatic"],
      "title": "Top Bar Visibility",
      "description": "Whether to show the top bar or not, yes for always showing, no for always not showing, automatic for adjusting to screen size",
      "default": "automatic"
    }
  },
  "additionalProperties": false,
  "type": "object"
}
```
