# Chunk: dddf3bff4c0b_1

- source: `.venv-lab/Lib/site-packages/nbformat/v4/nbformat.v4.4.schema.json`
- lines: 80-172
- chunk: 2/6

```
 backward compatible changes to the notebook format.",
      "type": "integer",
      "minimum": 4
    },
    "nbformat": {
      "description": "Notebook format (major number). Incremented between backwards incompatible changes to the notebook format.",
      "type": "integer",
      "minimum": 4,
      "maximum": 4
    },
    "cells": {
      "description": "Array of cells of the current notebook.",
      "type": "array",
      "items": { "$ref": "#/definitions/cell" }
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
            "jupyter": {
              "description": "Official Jupyter Metadata for Raw Cells",
              "type": "object",
              "additionalProperties": true,
              "source_hidden": {
                "description": "Whether the source is hidden.",
                "type": "boolean"
              }
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
            "tags": { "$ref": "#/definitions/misc/metadata_tags" },
            "jupyter": {
              "description": "Official Jupyter Metadata for Markdown Cells",
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
```
