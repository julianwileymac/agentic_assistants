# Chunk: eea4f3b35fae_3

- source: `.venv-lab/Lib/site-packages/nbformat/v4/nbformat.v4.1.schema.json`
- lines: 245-341
- chunk: 4/5

```
ct",
      "additionalProperties": false,
      "required": ["output_type", "data", "metadata"],
      "properties": {
        "output_type": {
          "description": "Type of cell output.",
          "enum": ["display_data"]
        },
        "data": { "$ref": "#/definitions/misc/mimebundle" },
        "metadata": { "$ref": "#/definitions/misc/output_metadata" }
      }
    },

    "stream": {
      "description": "Stream output from a code cell.",
      "type": "object",
      "additionalProperties": false,
      "required": ["output_type", "name", "text"],
      "properties": {
        "output_type": {
          "description": "Type of cell output.",
          "enum": ["stream"]
        },
        "name": {
          "description": "The name of the stream (stdout, stderr).",
          "type": "string"
        },
        "text": {
          "description": "The stream's text output, represented as an array of strings.",
          "$ref": "#/definitions/misc/multiline_string"
        }
      }
    },

    "error": {
      "description": "Output of an error that occurred during code cell execution.",
      "type": "object",
      "additionalProperties": false,
      "required": ["output_type", "ename", "evalue", "traceback"],
      "properties": {
        "output_type": {
          "description": "Type of cell output.",
          "enum": ["error"]
        },
        "ename": {
          "description": "The name of the error.",
          "type": "string"
        },
        "evalue": {
          "description": "The value, or message, of the error.",
          "type": "string"
        },
        "traceback": {
          "description": "The error's traceback, represented as an array of strings.",
          "type": "array",
          "items": { "type": "string" }
        }
      }
    },

    "unrecognized_output": {
      "description": "Unrecognized output from a future minor-revision to the notebook format.",
      "type": "object",
      "additionalProperties": true,
      "required": ["output_type"],
      "properties": {
        "output_type": {
          "description": "Type of cell output.",
          "not": {
            "enum": ["execute_result", "display_data", "stream", "error"]
          }
        }
      }
    },

    "misc": {
      "metadata_name": {
        "description": "The cell's name. If present, must be a non-empty string.",
        "type": "string",
        "pattern": "^.+$"
      },
      "metadata_tags": {
        "description": "The cell's tags. Tags must be unique, and must not contain commas.",
        "type": "array",
        "uniqueItems": true,
        "items": {
          "type": "string",
          "pattern": "^[^,]+$"
        }
      },
      "attachments": {
        "description": "Media attachments (e.g. inline images), stored as mimebundle keyed by filename.",
        "type": "object",
        "patternProperties": {
          ".*": {
            "description": "The attachment's data stored as a mimebundle.",
```
