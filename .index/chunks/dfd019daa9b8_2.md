# Chunk: dfd019daa9b8_2

- source: `.venv-lab/share/jupyter/lab/schemas/@jupyterlab/console-extension/tracker.json`
- lines: 171-247
- chunk: 3/3

```
t": "right", "title": "Right" }
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
      "description": "Note: To disable a toolbar item,\ncopy it to User Preferences and add the\n\"disabled\" key. The following example will disable the Interrupt button item:\n{\n  \"toolbar\": [\n    {\n      \"name\": \"interrupt\",\n      \"disabled\": true\n    }\n  ]\n}\n\nToolbar description:",
      "items": {
        "$ref": "#/definitions/toolbarItem"
      },
      "type": "array",
      "default": []
    }
  },
  "additionalProperties": false,
  "type": "object",
  "definitions": {
    "toolbarItem": {
      "properties": {
        "name": {
          "title": "Unique name",
          "type": "string"
        },
        "args": {
          "title": "Command arguments",
          "type": "object"
        },
        "command": {
          "title": "Command id",
          "type": "string",
          "default": ""
        },
        "disabled": {
          "title": "Whether the item is ignored or not",
          "type": "boolean",
          "default": false
        },
        "icon": {
          "title": "Item icon id",
          "description": "If defined, it will override the command icon",
          "type": "string"
        },
        "label": {
          "title": "Item label",
          "description": "If defined, it will override the command label",
          "type": "string"
        },
        "caption": {
          "title": "Item caption",
          "description": "If defined, it will override the command caption",
          "type": "string"
        },
        "type": {
          "title": "Item type",
          "type": "string",
          "enum": ["command", "spacer"]
        },
        "rank": {
          "title": "Item rank",
          "type": "number",
          "minimum": 0,
          "default": 50
        }
      },
      "required": ["name"],
      "additionalProperties": false,
      "type": "object"
    }
  }
}
```
