# Chunk: f9f8fccee869_0

- source: `.venv-lab/Lib/site-packages/jupyter_lsp/specs/config/dockerfile-language-server-nodejs.schema.json`
- lines: 1-115
- chunk: 1/5

```
{
  "title": "Docker language server confiuguration",
  "type": "object",
  "$comment": "Based on settings of vscode-docker which is distributed under MIT License, Copyright (c) Microsoft Corporation",
  "properties": {
    "docker.defaultRegistryPath": {
      "type": "string",
      "default": "",
      "description": "Default registry and path when tagging an image"
    },
    "docker.explorerRefreshInterval": {
      "type": "number",
      "default": 2000,
      "description": "Explorer refresh interval, default is 2000ms"
    },
    "docker.containers.groupBy": {
      "type": "string",
      "default": "None",
      "description": "The property to use when grouping containers.",
      "enum": [
        "ContainerId",
        "ContainerName",
        "CreatedTime",
        "FullTag",
        "ImageId",
        "Networks",
        "None",
        "Ports",
        "Registry",
        "Repository",
        "RepositoryName",
        "RepositoryNameAndTag",
        "State",
        "Status",
        "Tag"
      ]
    },
    "docker.containers.description": {
      "type": "array",
      "default": ["ContainerName", "Status"],
      "description": "Any secondary properties to display for a container.",
      "items": {
        "type": "string",
        "enum": [
          "ContainerId",
          "ContainerName",
          "CreatedTime",
          "FullTag",
          "ImageId",
          "Networks",
          "Ports",
          "Registry",
          "Repository",
          "RepositoryName",
          "RepositoryNameAndTag",
          "State",
          "Status",
          "Tag"
        ]
      }
    },
    "docker.containers.label": {
      "type": "string",
      "default": "FullTag",
      "description": "The primary property to display for a container.",
      "enum": [
        "ContainerId",
        "ContainerName",
        "CreatedTime",
        "FullTag",
        "ImageId",
        "Networks",
        "Ports",
        "Registry",
        "Repository",
        "RepositoryName",
        "RepositoryNameAndTag",
        "State",
        "Status",
        "Tag"
      ]
    },
    "docker.containers.sortBy": {
      "type": "string",
      "default": "CreatedTime",
      "description": "The property to use when sorting containers.",
      "enum": ["CreatedTime", "Label"]
    },
    "docker.images.groupBy": {
      "type": "string",
      "default": "Repository",
      "description": "The property to use when grouping images.",
      "enum": [
        "CreatedTime",
        "FullTag",
        "ImageId",
        "None",
        "Registry",
        "Repository",
        "RepositoryName",
        "RepositoryNameAndTag",
        "Tag"
      ]
    },
    "docker.images.description": {
      "type": "array",
      "default": ["CreatedTime"],
      "description": "Any secondary properties to display for a image.",
      "items": {
        "type": "string",
        "enum": [
          "CreatedTime",
          "FullTag",
          "ImageId",
```
