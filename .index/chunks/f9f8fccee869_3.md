# Chunk: f9f8fccee869_3

- source: `.venv-lab/Lib/site-packages/jupyter_lsp/specs/config/dockerfile-language-server-nodejs.schema.json`
- lines: 267-335
- chunk: 4/5

```
.languageserver.diagnostics.instructionCmdMultiple": {
      "scope": "resource",
      "type": "string",
      "default": "warning",
      "enum": ["ignore", "warning", "error"],
      "description": "Controls the diagnostic severity for flagging a Dockerfile with multiple CMD instructions"
    },
    "docker.languageserver.diagnostics.instructionEntrypointMultiple": {
      "scope": "resource",
      "type": "string",
      "default": "warning",
      "enum": ["ignore", "warning", "error"],
      "description": "Controls the diagnostic severity for flagging a Dockerfile with multiple ENTRYPOINT instructions"
    },
    "docker.languageserver.diagnostics.instructionHealthcheckMultiple": {
      "scope": "resource",
      "type": "string",
      "default": "warning",
      "enum": ["ignore", "warning", "error"],
      "description": "Controls the diagnostic severity for flagging a Dockerfile with multiple HEALTHCHECK instructions"
    },
    "docker.languageserver.diagnostics.instructionJSONInSingleQuotes": {
      "scope": "resource",
      "type": "string",
      "default": "warning",
      "enum": ["ignore", "warning", "error"],
      "description": "Controls the diagnostic severity for JSON instructions that are written incorrectly with single quotes"
    },
    "docker.languageserver.diagnostics.instructionWorkdirRelative": {
      "scope": "resource",
      "type": "string",
      "default": "warning",
      "enum": ["ignore", "warning", "error"],
      "description": "Controls the diagnostic severity for WORKDIR instructions that do not point to an absolute path"
    },
    "docker.attachShellCommand.linuxContainer": {
      "type": "string",
      "default": "/bin/sh -c \"[ -e /bin/bash ] && /bin/bash || /bin/sh\"",
      "description": "Attach command to use for Linux containers"
    },
    "docker.attachShellCommand.windowsContainer": {
      "type": "string",
      "default": "powershell",
      "description": "Attach command to use for Windows containers"
    },
    "docker.dockerComposeBuild": {
      "type": "boolean",
      "default": true,
      "description": "Run docker-compose with the --build argument, defaults to true"
    },
    "docker.dockerComposeDetached": {
      "type": "boolean",
      "default": true,
      "description": "Run docker-compose with the --d (detached) argument, defaults to true"
    },
    "docker.showRemoteWorkspaceWarning": {
      "type": "boolean",
      "default": true,
      "description": "Show a prompt to switch from \"UI\" extension to \"Workspace\" extension if an operation is not supported."
    },
    "docker.dockerPath": {
      "type": "string",
      "default": "docker",
      "description": "Absolute path to Docker client executable ('docker' command). If the path contains whitespace, it needs to be quoted appropriately."
    },
    "docker.enableDockerComposeLanguageService": {
      "type": "boolean",
      "default": true,
```
