# Chunk: dddf3bff4c0b_3

- source: `.venv-lab/Lib/site-packages/nbformat/v4/nbformat.v4.4.schema.json`
- lines: 228-315
- chunk: 4/6

```
atus message when the status is 'idle'. It indicates the time at which kernel finished processing the associated request",
                  "type": "string"
                }
              },
              "additionalProperties": true,
              "patternProperties": {
                "^.*$": {
                  "type": "string"
                }
              }
            },
            "collapsed": {
              "description": "Whether the cell's output is collapsed/expanded.",
              "type": "boolean"
            },
            "scrolled": {
              "description": "Whether the cell's output is scrolled, unscrolled, or autoscrolled.",
              "enum": [true, false, "auto"]
            },
            "name": { "$ref": "#/definitions/misc/metadata_name" },
            "tags": { "$ref": "#/definitions/misc/metadata_tags" }
          }
        },
        "source": { "$ref": "#/definitions/misc/source" },
        "outputs": {
          "description": "Execution, display, or stream outputs.",
          "type": "array",
          "items": { "$ref": "#/definitions/output" }
        },
        "execution_count": {
          "description": "The code cell's prompt number. Will be null if the cell has not been run.",
          "type": ["integer", "null"],
          "minimum": 0
        }
      }
    },

    "unrecognized_cell": {
      "description": "Unrecognized cell from a future minor-revision to the notebook format.",
      "type": "object",
      "additionalProperties": true,
      "required": ["cell_type", "metadata"],
      "properties": {
        "cell_type": {
          "description": "String identifying the type of cell.",
          "not": {
            "enum": ["markdown", "code", "raw"]
          }
        },
        "metadata": {
          "description": "Cell-level metadata.",
          "type": "object",
          "properties": {
            "name": { "$ref": "#/definitions/misc/metadata_name" },
            "tags": { "$ref": "#/definitions/misc/metadata_tags" }
          },
          "additionalProperties": true
        }
      }
    },

    "output": {
      "type": "object",
      "oneOf": [
        { "$ref": "#/definitions/execute_result" },
        { "$ref": "#/definitions/display_data" },
        { "$ref": "#/definitions/stream" },
        { "$ref": "#/definitions/error" }
      ]
    },

    "execute_result": {
      "description": "Result of executing a code cell.",
      "type": "object",
      "additionalProperties": false,
      "required": ["output_type", "data", "metadata", "execution_count"],
      "properties": {
        "output_type": {
          "description": "Type of cell output.",
          "enum": ["execute_result"]
        },
        "execution_count": {
          "description": "A result's prompt number.",
          "type": ["integer", "null"],
          "minimum": 0
        },
        "data": { "$ref": "#/definitions/misc/mimebundle" },
```
