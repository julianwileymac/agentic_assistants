# Chunk: f9f8fccee869_1

- source: `.venv-lab/Lib/site-packages/jupyter_lsp/specs/config/dockerfile-language-server-nodejs.schema.json`
- lines: 104-206
- chunk: 2/5

```
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
          "Registry",
          "Repository",
          "RepositoryName",
          "RepositoryNameAndTag",
          "Tag"
        ]
      }
    },
    "docker.images.label": {
      "type": "string",
      "default": "Tag",
      "description": "The primary property to display for a image.",
      "enum": [
        "CreatedTime",
        "FullTag",
        "ImageId",
        "Registry",
        "Repository",
        "RepositoryName",
        "RepositoryNameAndTag",
        "Tag"
      ]
    },
    "docker.images.sortBy": {
      "type": "string",
      "default": "CreatedTime",
      "description": "The property to use when sorting images.",
      "enum": ["CreatedTime", "Label"]
    },
    "docker.networks.groupBy": {
      "type": "string",
      "default": "None",
      "description": "The property to use when grouping networks.",
      "enum": [
        "CreatedTime",
        "NetworkDriver",
        "NetworkId",
        "NetworkName",
        "None"
      ]
    },
    "docker.networks.description": {
      "type": "array",
      "default": ["NetworkDriver", "CreatedTime"],
      "description": "Any secondary properties to display for a network.",
      "items": {
        "type": "string",
        "enum": ["CreatedTime", "NetworkDriver", "NetworkId", "NetworkName"]
      }
    },
    "docker.networks.label": {
      "type": "string",
      "default": "NetworkName",
      "description": "The primary property to display for a network.",
      "enum": ["CreatedTime", "NetworkDriver", "NetworkId", "NetworkName"]
    },
    "docker.networks.sortBy": {
      "type": "string",
      "default": "CreatedTime",
      "description": "The property to use when sorting networks.",
      "enum": ["CreatedTime", "Label"]
    },
    "docker.volumes.groupBy": {
      "type": "string",
      "default": "None",
      "description": "The property to use when grouping volumes.",
      "enum": ["CreatedTime", "VolumeName", "None"]
    },
    "docker.volumes.description": {
      "type": "array",
      "default": ["CreatedTime"],
      "description": "Any secondary properties to display for a volume.",
      "items": {
        "type": "string",
        "enum": ["CreatedTime", "VolumeName"]
      }
    },
    "docker.volumes.label": {
      "type": "string",
      "default": "VolumeName",
      "description": "The primary property to display for a volume.",
      "enum": ["CreatedTime", "VolumeName"]
    },
    "docker.volumes.sortBy": {
      "type": "string",
      "default": "CreatedTime",
      "description": "The property to use when sorting volumes.",
      "enum": ["CreatedTime", "Label"]
    },
    "docker.imageBuildContextPath": {
      "type": "string",
```
