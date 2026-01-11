# Chunk: abec6679af3c_3

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/_pydevd_bundle/_debug_adapter/debugProtocolCustom.json`
- lines: 222-325
- chunk: 4/4

```
ersion": {
					"type": "string",
					"description": "Python version as a string in semver format: <major>.<minor>.<micro><releaselevel><serial>."
				},
				"description": {
					"type": "string",
					"description": "Optional description for this python implementation."
				}
			}
		},
		"PydevdPlatformInfo": {
			"type": "object",
			"description": "This object contains python version and implementation details.",
			"properties": {
				"name": {
					"type": "string",
					"description": "Name of the platform as returned by 'sys.platform'."
				}
			}
		},
		"PydevdProcessInfo": {
			"type": "object",
			"description": "This object contains python process details.",
			"properties": {
				"pid": {
					"type": "integer",
					"description": "Process ID for the current process."
				},
				"ppid": {
					"type": "integer",
					"description": "Parent Process ID for the current process."
				},
				"executable": {
					"type": "string",
					"description": "Path to the executable as returned by 'sys.executable'."
				},
				"bitness": {
					"type": "integer",
					"description": "Integer value indicating the bitness of the current process."
				}
			}
		},
		"PydevdInfo": {
			"type": "object",
			"description": "This object contains details on pydevd.",
			"properties": {
				"usingCython": {
					"type": "boolean",
					"description": "Specifies whether the cython native module is being used."
				},
				"usingFrameEval": {
					"type": "boolean",
					"description": "Specifies whether the frame eval native module is being used."
				}
			}
		},
		"PydevdAuthorizeRequest": {
			"allOf": [ { "$ref": "#/definitions/Request" }, {
				"type": "object",
				"description": "A request to authorize the ide to start accepting commands.",
				"properties": {
					"command": {
						"type": "string",
						"enum": [ "pydevdAuthorize" ]
					},
					"arguments": {
						"$ref": "#/definitions/PydevdAuthorizeArguments"
					}
				},
				"required": [ "command", "arguments" ]
			}]
		},
		"PydevdAuthorizeArguments": {
			"type": "object",
			"description": "Arguments for 'pydevdAuthorize' request.",
			"properties": {
				"debugServerAccessToken": {
					"type": "string" ,
					"description": "The access token to access the debug server."
				}
			},
			"required": [ "command" ]
		},
		"PydevdAuthorizeResponse": {
			"allOf": [ { "$ref": "#/definitions/Response" }, {
				"type": "object",
				"description": "Response to 'pydevdAuthorize' request.",
				"properties": {
					"body": {
						"type": "object",
						"properties": {
							"clientAccessToken": {
								"type": "string",
								"description": "The access token to access the client (i.e.: usually the IDE)."
							}
						},
						"required": [ "clientAccessToken" ]
					}
				},
				"required": [ "body" ]
			}]
		}
	}
}
```
