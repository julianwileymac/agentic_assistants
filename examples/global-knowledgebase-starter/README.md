Global Knowledgebase Starter
============================

This starter bundles a minimal set of artifacts to ingest remote GitHub repositories into the global knowledgebase backed by Chroma. It is intended as a seed project that any user can copy and run locally or on the cluster.

Contents
--------
- `repos.yaml`: persisted list of repositories (url, branch, tags, schedule, overrides)
- `config.yaml`: pipeline knobs (collection name, cache paths, chunking, augmentation mode, summary paths)
- `summaries/`: plaintext ingestion summaries (written per run)

Quickstart
----------
1) Update `repos.yaml` with the repositories to track (see example entries).
2) Run the ingestion pipeline:
   ```bash
   python -m agentic_assistants.pipelines.run_repo_ingestion --config examples/global-knowledgebase-starter/config.yaml
   ```
3) View plaintext summaries in `summaries/` and search the `global-knowledgebase` collection via MCP, REST, or CLI:
   ```bash
   agentic search "repo ingestion" --collection global-knowledgebase -k 5
   ```

Files
-----
- `repos.yaml` – sample tracked repos with per-repo tags, schedule (cron) and manual overrides.
- `config.yaml` – default collection `global-knowledgebase`, vectorDB settings, augmentation strategy (`crew` or `langchain`), and summary output path.
- `summaries/` – empty folder; summaries are appended per ingestion run.

Scheduling
----------
- Jobs are registered on server startup using the repo-level `schedule` field.
- Set `manual_override: true` on a repo to skip scheduled ingestion while keeping the entry.
- The K8s CronJob manifest at `k8s/cronjobs/global-repo-ingestion.yaml` runs the pipeline in-cluster.

MCP Usage
---------
Use the MCP endpoint to search the global knowledgebase collection:
```json
{"jsonrpc":"2.0","id":"1","method":"tools/call","params":{"name":"search_codebase","arguments":{"query":"pipeline", "collection":"global-knowledgebase", "top_k":5}}}
```

Coding Agent
------------
Use the MCP-backed Ollama coding agent for quick answers:
```python
from agentic_assistants import AgenticConfig
from agentic_assistants.agents import McpOllamaCodingAgent

agent = McpOllamaCodingAgent(config=AgenticConfig(), collection="global-knowledgebase")
print(agent.answer("How does repo ingestion work?"))
```

Notes
-----
- Chroma embedded mode is the default; point `vectordb.path` to a persistent volume for k8s.
- Scheduling is handled by APScheduler in-process; you can also deploy the provided k8s CronJob to trigger ingestion in-cluster.
- Augmentations can be toggled between CrewAI and LangChain; both emit metadata/tags into vector documents for filtered search.
- Set `AGENTIC_REPO_INGESTION_CONFIG` to override the default config path used on server startup.