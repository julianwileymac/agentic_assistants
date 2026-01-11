# Chunk: abec6679af3c_2

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/_pydevd_bundle/_debug_adapter/debugProtocolCustom.json`
- lines: 141-232
- chunk: 3/4

```
: "integer",
					"description": "The remote line to which the mapping should map to (e.g.: for an ipython notebook this would be always 1 as it'd map the start of the cell)."
				}
			},
			"required": ["line", "endLine", "runtimeSource", "runtimeLine"]
		},

		"PydevdSystemInfoRequest": {
			"allOf": [ { "$ref": "#/definitions/Request" }, {
				"type": "object",
				"description": "The request can be used retrieve system information, python version, etc.",
				"properties": {
					"command": {
						"type": "string",
						"enum": [ "pydevdSystemInfo" ]
					},
					"arguments": {
						"$ref": "#/definitions/PydevdSystemInfoArguments"
					}
				},
				"required": [ "command" ]
			}]
		},
		"PydevdSystemInfoArguments": {
			"type": "object",
			"description": "Arguments for 'pydevdSystemInfo' request."
		},
		"PydevdSystemInfoResponse": {
			"allOf": [ { "$ref": "#/definitions/Response" }, {
				"type": "object",
				"description": "Response to 'pydevdSystemInfo' request.",
				"properties": {
					"body": {
						"type": "object",
						"properties": {
							"python": {
								"$ref": "#/definitions/PydevdPythonInfo",
								"description": "Information about the python version running in the current process."
							},
							"platform": {
								"$ref": "#/definitions/PydevdPlatformInfo",
								"description": "Information about the plarforn on which the current process is running."
							},
							"process": {
								"$ref": "#/definitions/PydevdProcessInfo",
								"description": "Information about the current process."
							},
							"pydevd": {
								"$ref": "#/definitions/PydevdInfo",
								"description": "Information about pydevd."
							}
						},
						"required": [ "python", "platform", "process", "pydevd" ]
					}
				},
				"required": [ "body" ]
			}]
		},

		"PydevdPythonInfo": {
			"type": "object",
			"description": "This object contains python version and implementation details.",
			"properties": {
				"version": {
					"type": "string",
					"description": "Python version as a string in semver format: <major>.<minor>.<micro><releaselevel><serial>."
				},
				"implementation": {
					"$ref": "#/definitions/PydevdPythonImplementationInfo",
					"description": "Python version as a string in this format <major>.<minor>.<micro><releaselevel><serial>."
				}
			}
		},
		"PydevdPythonImplementationInfo": {
			"type": "object",
			"description": "This object contains python implementation details.",
			"properties": {
				"name": {
					"type": "string",
					"description": "Python implementation name."
				},
				"version": {
					"type": "string",
					"description": "Python version as a string in semver format: <major>.<minor>.<micro><releaselevel><serial>."
				},
				"description": {
					"type": "string",
					"description": "Optional description for this python implementation."
				}
			}
		},
```
