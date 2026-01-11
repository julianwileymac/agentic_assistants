# Chunk: dddf3bff4c0b_2

- source: `.venv-lab/Lib/site-packages/nbformat/v4/nbformat.v4.4.schema.json`
- lines: 162-235
- chunk: 3/6

```
              "type": "object",
              "additionalProperties": true,
              "source_hidden": {
                "description": "Whether the source is hidden.",
                "type": "boolean"
              }
            }
          },
          "additionalProperties": true
        },
        "attachments": { "$ref": "#/definitions/misc/attachments" },
        "source": { "$ref": "#/definitions/misc/source" }
      }
    },

    "code_cell": {
      "description": "Notebook code cell.",
      "type": "object",
      "additionalProperties": false,
      "required": [
        "cell_type",
        "metadata",
        "source",
        "outputs",
        "execution_count"
      ],
      "properties": {
        "cell_type": {
          "description": "String identifying the type of cell.",
          "enum": ["code"]
        },
        "metadata": {
          "description": "Cell-level metadata.",
          "type": "object",
          "additionalProperties": true,
          "properties": {
            "jupyter": {
              "description": "Official Jupyter Metadata for Code Cells",
              "type": "object",
              "additionalProperties": true,
              "source_hidden": {
                "description": "Whether the source is hidden.",
                "type": "boolean"
              },
              "outputs_hidden": {
                "description": "Whether the outputs are hidden.",
                "type": "boolean"
              }
            },
            "execution": {
              "description": "Execution time for the code in the cell. This tracks time at which messages are received from iopub or shell channels",
              "type": "object",
              "properties": {
                "iopub.execute_input": {
                  "description": "header.date (in ISO 8601 format) of iopub channel's execute_input message. It indicates the time at which the kernel broadcasts an execute_input message to connected frontends",
                  "type": "string"
                },
                "iopub.status.busy": {
                  "description": "header.date (in ISO 8601 format) of iopub channel's kernel status message when the status is 'busy'",
                  "type": "string"
                },
                "shell.execute_reply": {
                  "description": "header.date (in ISO 8601 format) of the shell channel's execute_reply message. It indicates the time at which the execute_reply message was created",
                  "type": "string"
                },
                "iopub.status.idle": {
                  "description": "header.date (in ISO 8601 format) of iopub channel's kernel status message when the status is 'idle'. It indicates the time at which kernel finished processing the associated request",
                  "type": "string"
                }
              },
              "additionalProperties": true,
              "patternProperties": {
                "^.*$": {
```
