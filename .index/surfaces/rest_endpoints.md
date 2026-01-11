# REST Endpoints

Generated from `src/agentic_assistants/server/rest.py` and `src/agentic_assistants/server/api/*.py`.

```json
[
  {
    "method": "GET",
    "path": "/health",
    "file": "src/agentic_assistants/server/rest.py",
    "lineno": 258,
    "tags": []
  },
  {
    "method": "POST",
    "path": "/chat",
    "file": "src/agentic_assistants/server/rest.py",
    "lineno": 268,
    "tags": []
  },
  {
    "method": "GET",
    "path": "/sessions",
    "file": "src/agentic_assistants/server/rest.py",
    "lineno": 285,
    "tags": []
  },
  {
    "method": "POST",
    "path": "/sessions",
    "file": "src/agentic_assistants/server/rest.py",
    "lineno": 291,
    "tags": []
  },
  {
    "method": "GET",
    "path": "/sessions/{name}",
    "file": "src/agentic_assistants/server/rest.py",
    "lineno": 301,
    "tags": []
  },
  {
    "method": "POST",
    "path": "/artifacts/tag",
    "file": "src/agentic_assistants/server/rest.py",
    "lineno": 310,
    "tags": []
  },
  {
    "method": "GET",
    "path": "/data/read",
    "file": "src/agentic_assistants/server/rest.py",
    "lineno": 327,
    "tags": []
  },
  {
    "method": "POST",
    "path": "/mlflow/experiment/start",
    "file": "src/agentic_assistants/server/rest.py",
    "lineno": 338,
    "tags": []
  },
  {
    "method": "POST",
    "path": "/search",
    "file": "src/agentic_assistants/server/rest.py",
    "lineno": 350,
    "tags": []
  },
  {
    "method": "POST",
    "path": "/index",
    "file": "src/agentic_assistants/server/rest.py",
    "lineno": 386,
    "tags": []
  },
  {
    "method": "GET",
    "path": "/collections",
    "file": "src/agentic_assistants/server/rest.py",
    "lineno": 429,
    "tags": []
  },
  {
    "method": "GET",
    "path": "/collections/{name}",
    "file": "src/agentic_assistants/server/rest.py",
    "lineno": 450,
    "tags": []
  },
  {
    "method": "DELETE",
    "path": "/collections/{name}",
    "file": "src/agentic_assistants/server/rest.py",
    "lineno": 466,
    "tags": []
  },
  {
    "method": "GET",
    "path": "/stats",
    "file": "src/agentic_assistants/server/rest.py",
    "lineno": 484,
    "tags": []
  },
  {
    "method": "GET",
    "path": "/api/v1/stats",
    "file": "src/agentic_assistants/server/rest.py",
    "lineno": 496,
    "tags": []
  },
  {
    "method": "GET",
    "path": "/agents",
    "router_prefix": "/agents",
    "tags": [
      "agents"
    ],
    "file": "src/agentic_assistants/server/api/agents.py",
    "lineno": 88
  },
  {
    "method": "POST",
    "path": "/agents",
    "router_prefix": "/agents",
    "tags": [
      "agents"
    ],
    "file": "src/agentic_assistants/server/api/agents.py",
    "lineno": 110
  },
  {
    "method": "GET",
    "path": "/agents/{agent_id}",
    "router_prefix": "/agents",
    "tags": [
      "agents"
    ],
    "file": "src/agentic_assistants/server/api/agents.py",
    "lineno": 135
  },
  {
    "method": "PUT",
    "path": "/agents/{agent_id}",
    "router_prefix": "/agents",
    "tags": [
      "agents"
    ],
    "file": "src/agentic_assistants/server/api/agents.py",
    "lineno": 147
  },
  {
    "method": "DELETE",
    "path": "/agents/{agent_id}",
    "router_prefix": "/agents",
    "tags": [
      "agents"
    ],
    "file": "src/agentic_assistants/server/api/agents.py",
    "lineno": 161
  },
  {
    "method": "POST",
    "path": "/agents/{agent_id}/deploy",
    "router_prefix": "/agents",
    "tags": [
      "agents"
    ],
    "file": "src/agentic_assistants/server/api/agents.py",
    "lineno": 172
  },
  {
    "method": "POST",
    "path": "/agents/{agent_id}/run",
    "router_prefix": "/agents",
    "tags": [
      "agents"
    ],
    "file": "src/agentic_assistants/server/api/agents.py",
    "lineno": 184
  },
  {
    "method": "GET",
    "path": "/artifacts",
    "router_prefix": "/artifacts",
    "tags": [
      "artifacts"
    ],
    "file": "src/agentic_assistants/server/api/artifacts.py",
    "lineno": 341
  },
  {
    "method": "POST",
    "path": "/artifacts",
    "router_prefix": "/artifacts",
    "tags": [
      "artifacts"
    ],
    "file": "src/agentic_assistants/server/api/artifacts.py",
    "lineno": 368
  },
  {
    "method": "GET",
    "path": "/artifacts/{artifact_id}",
    "router_prefix": "/artifacts",
    "tags": [
      "artifacts"
    ],
    "file": "src/agentic_assistants/server/api/artifacts.py",
    "lineno": 402
  },
  {
    "method": "GET",
    "path": "/artifacts/{artifact_id}/download",
    "router_prefix": "/artifacts",
    "tags": [
      "artifacts"
    ],
    "file": "src/agentic_assistants/server/api/artifacts.py",
    "lineno": 416
  },
  {
    "method": "PATCH",
    "path": "/artifacts/{artifact_id}",
    "router_prefix": "/artifacts",
    "tags": [
      "artifacts"
    ],
    "file": "src/agentic_assistants/server/api/artifacts.py",
    "lineno": 438
  },
  {
    "method": "DELETE",
    "path": "/artifacts/{artifact_id}",
    "router_prefix": "/artifacts",
    "tags": [
      "artifacts"
    ],
    "file": "src/agentic_assistants/server/api/artifacts.py",
    "lineno": 454
  },
  {
    "method": "POST",
    "path": "/artifacts/{artifact_id}/tags",
    "router_prefix": "/artifacts",
    "tags": [
      "artifacts"
    ],
    "file": "src/agentic_assistants/server/api/artifacts.py",
    "lineno": 467
  },
  {
    "method": "POST",
    "path": "/artifacts/{artifact_id}/groups",
    "router_prefix": "/artifacts",
    "tags": [
      "artifacts"
    ],
    "file": "src/agentic_assistants/server/api/artifacts.py",
    "lineno": 486
  },
  {
    "method": "POST",
    "path": "/artifacts/{artifact_id}/share",
    "router_prefix": "/artifacts",
    "tags": [
      "artifacts"
    ],
    "file": "src/agentic_assistants/server/api/artifacts.py",
    "lineno": 505
  },
  {
    "method": "GET",
    "path": "/artifacts/groups/list",
    "router_prefix": "/artifacts",
    "tags": [
      "artifacts"
    ],
    "file": "src/agentic_assistants/server/api/artifacts.py",
    "lineno": 519
  },
  {
    "method": "GET",
    "path": "/artifacts/tags/list",
    "router_prefix": "/artifacts",
    "tags": [
      "artifacts"
    ],
    "file": "src/agentic_assistants/server/api/artifacts.py",
    "lineno": 528
  },
  {
    "method": "GET",
    "path": "/artifacts/shared/list",
    "router_prefix": "/artifacts",
    "tags": [
      "artifacts"
    ],
    "file": "src/agentic_assistants/server/api/artifacts.py",
    "lineno": 537
  },
  {
    "method": "GET",
    "path": "/components",
    "router_prefix": "/components",
    "tags": [
      "components"
    ],
    "file": "src/agentic_assistants/server/api/components.py",
    "lineno": 102
  },
  {
    "method": "POST",
    "path": "/components",
    "router_prefix": "/components",
    "tags": [
      "components"
    ],
    "file": "src/agentic_assistants/server/api/components.py",
    "lineno": 131
  },
  {
    "method": "GET",
    "path": "/components/{component_id}",
    "router_prefix": "/components",
    "tags": [
      "components"
    ],
    "file": "src/agentic_assistants/server/api/components.py",
    "lineno": 160
  },
  {
    "method": "PUT",
    "path": "/components/{component_id}",
    "router_prefix": "/components",
    "tags": [
      "components"
    ],
    "file": "src/agentic_assistants/server/api/components.py",
    "lineno": 172
  },
  {
    "method": "DELETE",
    "path": "/components/{component_id}",
    "router_prefix": "/components",
    "tags": [
      "components"
    ],
    "file": "src/agentic_assistants/server/api/components.py",
    "lineno": 192
  },
  {
    "method": "GET",
    "path": "/components/categories/list",
    "router_prefix": "/components",
    "tags": [
      "components"
    ],
    "file": "src/agentic_assistants/server/api/components.py",
    "lineno": 203
  },
  {
    "method": "POST",
    "path": "/components/base/install",
    "router_prefix": "/components",
    "tags": [
      "components"
    ],
    "file": "src/agentic_assistants/server/api/components.py",
    "lineno": 878
  },
  {
    "method": "GET",
    "path": "/config",
    "router_prefix": "/config",
    "tags": [
      "config"
    ],
    "file": "src/agentic_assistants/server/api/config.py",
    "lineno": 307
  },
  {
    "method": "GET",
    "path": "/config/export",
    "router_prefix": "/config",
    "tags": [
      "config"
    ],
    "file": "src/agentic_assistants/server/api/config.py",
    "lineno": 316
  },
  {
    "method": "POST",
    "path": "/config/reset",
    "router_prefix": "/config",
    "tags": [
      "config"
    ],
    "file": "src/agentic_assistants/server/api/config.py",
    "lineno": 325
  },
  {
    "method": "GET",
    "path": "/config/global",
    "router_prefix": "/config",
    "tags": [
      "config"
    ],
    "file": "src/agentic_assistants/server/api/config.py",
    "lineno": 336
  },
  {
    "method": "PATCH",
    "path": "/config/global",
    "router_prefix": "/config",
    "tags": [
      "config"
    ],
    "file": "src/agentic_assistants/server/api/config.py",
    "lineno": 345
  },
  {
    "method": "GET",
    "path": "/config/ollama",
    "router_prefix": "/config",
    "tags": [
      "config"
    ],
    "file": "src/agentic_assistants/server/api/config.py",
    "lineno": 358
  },
  {
    "method": "PATCH",
    "path": "/config/ollama",
    "router_prefix": "/config",
    "tags": [
      "config"
    ],
    "file": "src/agentic_assistants/server/api/config.py",
    "lineno": 367
  },
  {
    "method": "GET",
    "path": "/config/mlflow",
    "router_prefix": "/config",
    "tags": [
      "config"
    ],
    "file": "src/agentic_assistants/server/api/config.py",
    "lineno": 376
  },
  {
    "method": "PATCH",
    "path": "/config/mlflow",
    "router_prefix": "/config",
    "tags": [
      "config"
    ],
    "file": "src/agentic_assistants/server/api/config.py",
    "lineno": 385
  }
]
```

(Total endpoints: 218)
