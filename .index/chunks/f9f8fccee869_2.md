# Chunk: f9f8fccee869_2

- source: `.venv-lab/Lib/site-packages/jupyter_lsp/specs/config/dockerfile-language-server-nodejs.schema.json`
- lines: 196-274
- chunk: 3/5

```
: ["CreatedTime", "VolumeName"]
    },
    "docker.volumes.sortBy": {
      "type": "string",
      "default": "CreatedTime",
      "description": "The property to use when sorting volumes.",
      "enum": ["CreatedTime", "Label"]
    },
    "docker.imageBuildContextPath": {
      "type": "string",
      "default": "",
      "description": "Build context PATH to pass to Docker build command"
    },
    "docker.truncateLongRegistryPaths": {
      "type": "boolean",
      "default": false,
      "description": "Truncate long Image and Container registry paths in the Explorer"
    },
    "docker.truncateMaxLength": {
      "type": "number",
      "default": 10,
      "description": "Maximum number of characters for long registry paths in the Explorer, including elipsis"
    },
    "docker.host": {
      "type": "string",
      "default": "",
      "description": "Equivalent to setting the DOCKER_HOST environment variable."
    },
    "docker.certPath": {
      "type": "string",
      "default": "",
      "description": "Equivalent to setting the DOCKER_CERT_PATH environment variable."
    },
    "docker.tlsVerify": {
      "type": "string",
      "default": "",
      "description": "Equivalent to setting the DOCKER_TLS_VERIFY environment variable."
    },
    "docker.machineName": {
      "type": "string",
      "default": "",
      "description": "Equivalent to setting the DOCKER_MACHINE_NAME environment variable."
    },
    "docker.languageserver.diagnostics.deprecatedMaintainer": {
      "scope": "resource",
      "type": "string",
      "default": "warning",
      "enum": ["ignore", "warning", "error"],
      "description": "Controls the diagnostic severity for the deprecated MAINTAINER instruction"
    },
    "docker.languageserver.diagnostics.emptyContinuationLine": {
      "scope": "resource",
      "type": "string",
      "default": "warning",
      "enum": ["ignore", "warning", "error"],
      "description": "Controls the diagnostic severity for flagging empty continuation lines found in instructions that span multiple lines"
    },
    "docker.languageserver.diagnostics.directiveCasing": {
      "scope": "resource",
      "type": "string",
      "default": "warning",
      "enum": ["ignore", "warning", "error"],
      "description": "Controls the diagnostic severity for parser directives that are not written in lowercase"
    },
    "docker.languageserver.diagnostics.instructionCasing": {
      "scope": "resource",
      "type": "string",
      "default": "warning",
      "enum": ["ignore", "warning", "error"],
      "description": "Controls the diagnostic severity for instructions that are not written in uppercase"
    },
    "docker.languageserver.diagnostics.instructionCmdMultiple": {
      "scope": "resource",
      "type": "string",
      "default": "warning",
      "enum": ["ignore", "warning", "error"],
      "description": "Controls the diagnostic severity for flagging a Dockerfile with multiple CMD instructions"
    },
```
