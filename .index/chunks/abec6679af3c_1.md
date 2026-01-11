# Chunk: abec6679af3c_1

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/_pydevd_bundle/_debug_adapter/debugProtocolCustom.json`
- lines: 78-149
- chunk: 2/4

```
ons/Request" }, {
				"type": "object",
				"description": [
					"Sets multiple PydevdSourceMap for a single source and clears all previous PydevdSourceMap in that source.",
					"i.e.: Maps paths and lines in a 1:N mapping (use case: map a single file in the IDE to multiple IPython cells).",
					"To clear all PydevdSourceMap for a source, specify an empty array.",
					"Interaction with breakpoints: When a new mapping is sent, breakpoints that match the source (or previously matched a source) are reapplied.",
					"Interaction with launch pathMapping: both mappings are independent. This mapping is applied after the launch pathMapping."
				],
				"properties": {
					"command": {
						"type": "string",
						"enum": [ "setPydevdSourceMap" ]
					},
					"arguments": {
						"$ref": "#/definitions/SetPydevdSourceMapArguments"
					}
				},
				"required": [ "command", "arguments"  ]
			}]
		},
		"SetPydevdSourceMapArguments": {
			"type": "object",
			"description": "Arguments for 'setPydevdSourceMap' request.",
			"properties": {
				"source": {
					"$ref": "#/definitions/Source",
					"description": "The source location of the PydevdSourceMap; 'source.path' must be specified (e.g.: for an ipython notebook this could be something as /home/notebook/note.py)."
				},
				"pydevdSourceMaps": {
					"type": "array",
					"items": {
						"$ref": "#/definitions/PydevdSourceMap"
					},
					"description": "The PydevdSourceMaps to be set to the given source (provide an empty array to clear the source mappings for a given path)."
				}
			},
			"required": [ "source", "pydevdSourceMap" ]
		},
		"SetPydevdSourceMapResponse": {
			"allOf": [ { "$ref": "#/definitions/Response" }, {
				"type": "object",
				"description": "Response to 'setPydevdSourceMap' request. This is just an acknowledgement, so no body field is required."
			}]
		},

		"PydevdSourceMap": {
			"type": "object",
			"description": "Information that allows mapping a local line to a remote source/line.",
			"properties": {
				"line": {
					"type": "integer",
					"description": "The local line to which the mapping should map to (e.g.: for an ipython notebook this would be the first line of the cell in the file)."
				},
				"endLine": {
					"type": "integer",
					"description": "The end line."
				},
				"runtimeSource": {
					"$ref": "#/definitions/Source",
					"description": "The path that the user has remotely -- 'source.path' must be specified (e.g.: for an ipython notebook this could be something as '<ipython-input-1-4561234>')"
				},
				"runtimeLine": {
					"type": "integer",
					"description": "The remote line to which the mapping should map to (e.g.: for an ipython notebook this would be always 1 as it'd map the start of the cell)."
				}
			},
			"required": ["line", "endLine", "runtimeSource", "runtimeLine"]
		},

		"PydevdSystemInfoRequest": {
```
