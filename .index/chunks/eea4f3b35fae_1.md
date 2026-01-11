# Chunk: eea4f3b35fae_1

- source: `.venv-lab/Lib/site-packages/nbformat/v4/nbformat.v4.1.schema.json`
- lines: 76-172
- chunk: 2/5

```
s": { "$ref": "#/definitions/cell" }
    }
  },

  "definitions": {
    "cell": {
      "type": "object",
      "oneOf": [
        { "$ref": "#/definitions/raw_cell" },
        { "$ref": "#/definitions/markdown_cell" },
        { "$ref": "#/definitions/code_cell" }
      ]
    },

    "raw_cell": {
      "description": "Notebook raw nbconvert cell.",
      "type": "object",
      "additionalProperties": false,
      "required": ["cell_type", "metadata", "source"],
      "properties": {
        "cell_type": {
          "description": "String identifying the type of cell.",
          "enum": ["raw"]
        },
        "metadata": {
          "description": "Cell-level metadata.",
          "type": "object",
          "additionalProperties": true,
          "properties": {
            "format": {
              "description": "Raw cell metadata format for nbconvert.",
              "type": "string"
            },
            "name": { "$ref": "#/definitions/misc/metadata_name" },
            "tags": { "$ref": "#/definitions/misc/metadata_tags" }
          }
        },
        "attachments": { "$ref": "#/definitions/misc/attachments" },
        "source": { "$ref": "#/definitions/misc/source" }
      }
    },

    "markdown_cell": {
      "description": "Notebook markdown cell.",
      "type": "object",
      "additionalProperties": false,
      "required": ["cell_type", "metadata", "source"],
      "properties": {
        "cell_type": {
          "description": "String identifying the type of cell.",
          "enum": ["markdown"]
        },
        "metadata": {
          "description": "Cell-level metadata.",
          "type": "object",
          "properties": {
            "name": { "$ref": "#/definitions/misc/metadata_name" },
            "tags": { "$ref": "#/definitions/misc/metadata_tags" }
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
            "collapsed": {
              "description": "Whether the cell is collapsed/expanded.",
              "type": "boolean"
            },
            "scrolled": {
              "description": "Whether the cell's output is scrolled, unscrolled, or autoscrolled.",
              "enum": [true, false, "auto"]
            },
            "name": { "$ref": "#/definitions/misc/metadata_name" },
```
