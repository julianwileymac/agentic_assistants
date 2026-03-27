# Dagster Integration Guide

This document covers the Dagster orchestration integration in the Agentic Assistants framework, including setup, architecture, usage examples, Kubernetes deployment, and monitoring.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Installation](#installation)
- [Core Components](#core-components)
- [Usage Examples](#usage-examples)
- [Web UI](#web-ui)
- [API Reference](#api-reference)
- [Docker Deployment](#docker-deployment)
- [Kubernetes Deployment](#kubernetes-deployment)
- [Monitoring & Observability](#monitoring--observability)
- [Migration from APScheduler/Prefect](#migration-from-apschedulerprefect)

## Overview

Dagster is integrated as an asset-oriented data orchestration engine for process scheduling, workflow orchestration, background processing, and monitoring. It complements the existing Prefect integration and APScheduler-based scheduling layer.

Key capabilities:

- **Jobs & Ops**: Define Python functions as units of computation, compose them into jobs
- **Software-Defined Assets**: Declare data assets with dependency tracking and lineage
- **Schedules & Sensors**: Time-based and event-driven automation
- **Pipeline Bridge**: Convert existing Kedro-inspired pipelines to Dagster jobs/assets
- **Observability**: MLFlow, OpenTelemetry, and Prometheus integration
- **Kubernetes**: Full K8s deployment with webserver, daemon, and code server

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    WebUI (Next.js)                       │
│  /dagster          /dagster/develop    /dagster/jobs     │
│  Dashboard         Code IDE           Job Browser       │
└─────────────────────┬───────────────────────────────────┘
                      │ REST API
┌─────────────────────▼───────────────────────────────────┐
│                  FastAPI Backend                         │
│  api/dagster.py    DagsterAdapter    DagsterBridge       │
│  DagsterRunner     DagsterCallbacks  DagsterComponents   │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│              Dagster Infrastructure                      │
│  Webserver (UI)    Daemon (scheduler)   Code Server     │
│  PostgreSQL        MinIO (artifacts)                    │
└─────────────────────────────────────────────────────────┘
```

### Component Map

| Component | File | Purpose |
|-----------|------|---------|
| Adapter | `adapters/dagster_adapter.py` | Framework integration with observability |
| Bridge | `orchestration/dagster_bridge.py` | Pipeline-to-Dagster conversion |
| Runner | `pipelines/runners/dagster.py` | Execute pipelines via Dagster |
| Callbacks | `orchestration/dagster_callbacks.py` | Run/op lifecycle hooks + metrics |
| Components | `orchestration/dagster_components.py` | Pre-built ops and assets |
| Code Location | `orchestration/dagster_code/` | Dagster user code server |
| API Router | `server/api/dagster.py` | REST endpoints |

## Installation

### Dependencies

Install the Dagster extras:

```bash
# Using Poetry
poetry install -E dagster

# Or install all orchestration extras
poetry install -E orchestration

# Or pip
pip install dagster dagster-webserver dagster-postgres dagster-k8s dagster-docker
```

### Local Development

Start Dagster locally:

```bash
# Set DAGSTER_HOME
export DAGSTER_HOME=$(pwd)/conf/base

# Run the Dagster dev server
dagster dev -m agentic_assistants.orchestration.dagster_code
```

The Dagster UI will be available at `http://localhost:3000`.

## Core Components

### DagsterAdapter

The `DagsterAdapter` follows the `BaseAdapter` pattern, providing MLFlow, OpenTelemetry, and usage tracking for all Dagster operations.

```python
from agentic_assistants.adapters import DagsterAdapter

adapter = DagsterAdapter()

# Create a tracked job
@adapter.job(name="etl_pipeline")
def etl_pipeline():
    extract() >> transform() >> load()

# Create a tracked asset
@adapter.asset(name="cleaned_data", group_name="etl")
def cleaned_data(raw_data):
    return raw_data.dropna()

# Create a schedule
schedule = adapter.schedule("0 */6 * * *", job=etl_pipeline, name="six_hourly_etl")

# Run with full observability
result = adapter.run_job(etl_pipeline, run_config={})

# Assemble Definitions for code location
defs = adapter.create_definitions()
```

### Pipeline Bridge

Convert existing Kedro-inspired pipelines to Dagster:

```python
from agentic_assistants.orchestration import pipeline_to_job, pipeline_to_assets

# Convert pipeline to a Dagster job
dagster_job = pipeline_to_job(my_pipeline, name="my_dagster_job")

# Convert pipeline nodes to software-defined assets
assets = pipeline_to_assets(my_pipeline, group_name="my_group")

# Convert triggers to schedules
from agentic_assistants.orchestration import create_schedule_from_trigger
from agentic_assistants.scheduling.triggers import CronTrigger

trigger = CronTrigger(hour=2, minute=0)
schedule = create_schedule_from_trigger(trigger, dagster_job, name="daily_2am")
```

### DagsterRunner

Execute pipelines using Dagster as the execution backend:

```python
from agentic_assistants.pipelines.runners.dagster import DagsterRunner

# Local execution
runner = DagsterRunner()
result = runner.run(pipeline, catalog)

# Remote execution (Dagster instance)
runner = DagsterRunner(dagster_host="http://dagster:3000")
result = runner.run(pipeline, catalog)
```

### Pre-built Components

Ready-to-use ops and assets:

```python
from agentic_assistants.orchestration.dagster_components import (
    web_search_op,         # Web search API calls
    invoke_pipeline_op,    # Execute framework pipelines
    data_fetch_op,         # Fetch from catalog sources
    data_transform_op,     # Polars/Pandas transforms
    llm_inference_op,      # LLM inference
    workspace_cleanup_op,  # Workspace maintenance
    repo_ingestion_asset,  # Repository indexing asset
    knowledge_base_asset,  # Knowledge base update asset
    maintenance_job,       # Pre-built maintenance job
    web_search_job,        # Pre-built search job
)
```

## Usage Examples

### Creating a Custom Job

```python
import dagster as dg

@dg.op(description="Fetch data from API")
def fetch_data(context):
    import httpx
    response = httpx.get("https://api.example.com/data")
    context.log.info(f"Fetched {len(response.json())} records")
    return response.json()

@dg.op(description="Process the fetched data")
def process_data(context, raw_data):
    processed = [item for item in raw_data if item.get("active")]
    context.log.info(f"Processed {len(processed)} active records")
    return processed

@dg.job(description="Data processing pipeline")
def data_pipeline():
    raw = fetch_data()
    process_data(raw)
```

### Creating Software-Defined Assets

```python
import dagster as dg

@dg.asset(group_name="analytics")
def raw_events():
    """Load raw events from database."""
    return load_events()

@dg.asset(group_name="analytics", deps=[raw_events])
def daily_metrics():
    """Compute daily metrics from raw events."""
    events = load_raw_events()
    return compute_metrics(events)

@dg.asset(group_name="analytics", deps=[daily_metrics])
def weekly_report():
    """Generate weekly report from daily metrics."""
    metrics = load_daily_metrics()
    return generate_report(metrics)
```

### Scheduling

```python
import dagster as dg

# Time-based schedule
hourly_schedule = dg.ScheduleDefinition(
    job=data_pipeline,
    cron_schedule="0 * * * *",
    name="hourly_data_sync",
)

# Event-driven sensor
@dg.sensor(job=data_pipeline, minimum_interval_seconds=60)
def new_data_sensor(context):
    if check_for_new_data():
        yield dg.RunRequest(run_key="new_data")
```

## Web UI

### Dashboard (`/dagster`)

Overview of Dagster status including:
- Health status indicator
- Job, asset, and schedule counts
- Recent run history with status badges
- Quick launch buttons

### Development Environment (`/dagster/develop`)

Interactive code IDE for writing Dagster components:
- Code editor with Python syntax
- Template library (web search, data fetch, LLM inference, scheduled cleanup)
- Schedule wizard with cron expression builder
- Validate, Test Run, and Deploy buttons
- Output panel with execution results

### Jobs Browser (`/dagster/jobs`)

Browse and manage jobs:
- Search and filter jobs
- View run history per job
- Schedule management (enable/disable)
- Launch jobs with one click

### Flow Editor Integration

Dagster nodes available in the visual flow editor:
- **DagsterJobNode**: Trigger a Dagster job from within a flow
- **DagsterAssetNode**: Materialize a Dagster asset from a flow

## API Reference

All endpoints are prefixed with `/api/v1/dagster`.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Instance health check |
| GET | `/jobs` | List available jobs |
| GET | `/assets` | List software-defined assets |
| GET | `/schedules` | List schedules |
| POST | `/schedules/{name}/toggle` | Enable/disable schedule |
| GET | `/sensors` | List sensors |
| POST | `/jobs/{name}/run` | Launch a job run |
| POST | `/assets/materialize` | Materialize assets |
| GET | `/runs` | List recent runs |
| GET | `/runs/{run_id}` | Get run details |
| DELETE | `/runs/{run_id}` | Cancel a run |
| POST | `/code/validate` | Validate Python code |
| POST | `/code/deploy` | Deploy user code |
| GET | `/metrics` | Prometheus metrics |

## Docker Deployment

Start Dagster services via Docker Compose:

```bash
# Rebuild images after Dockerfile / workspace changes
docker compose --profile dagster build --no-cache

# Start Postgres + Dagster (postgres profile is included for the dagster profile)
docker compose --profile dagster up -d

# Services started:
# - dagster-webserver (port 3100 -> 3000)
# - dagster-daemon
# - dagster-code (gRPC port 4000)
```

The Dagster UI is accessible at `http://localhost:3100`.

### Instance config and Docker volumes

The `dagster_data` named volume mounts over `$DAGSTER_HOME`. Without a bootstrap step, that would hide `dagster.yaml` and `workspace.yaml` from the image and the webserver would fail to start (connection refused / unhealthy).

The image uses [`docker/dagster-entrypoint.sh`](../docker/dagster-entrypoint.sh) to copy templates from `/opt/dagster/dagster_config_templates/` into `$DAGSTER_HOME` when those files are missing. After changing compose or env, rebuild with `docker compose --profile dagster build`.

If you still see an empty or broken UI, remove the old volume and bring the stack up again:

```bash
docker compose --profile dagster down
docker volume rm agentic_assistants_dagster_data  # name may vary; use docker volume ls
docker compose --profile dagster up -d
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DAGSTER_HOME` | `/opt/dagster/dagster_home` | Dagster home directory |
| `PYTHONPATH` | `/app` | Ensures the installed package is importable in all Dagster processes |
| `DAGSTER_PG_HOST` | `postgres` | PostgreSQL host |
| `DAGSTER_PG_PORT` | `5432` | PostgreSQL port |
| `DAGSTER_PG_DB` | `agentic` | Database name (must match the `postgres` service) |
| `DAGSTER_PG_USERNAME` | `agentic` | Database user |
| `DAGSTER_PG_PASSWORD` | `agentic123` | Database password |

## Kubernetes Deployment

Dagster is deployed to Kubernetes using Kustomize.

### Components

- **Webserver**: Dagster UI and GraphQL API (port 3000)
- **Daemon**: Scheduler and sensor evaluation daemon
- **Code Server**: gRPC server hosting user code locations (port 4000)
- **ConfigMap**: Instance configuration (dagster.yaml, workspace.yaml)
- **PVC**: 5Gi persistent volume for artifacts and compute logs

### Deploy

```bash
# Apply with Kustomize
kubectl apply -k k8s/

# Verify pods
kubectl get pods -n agentic -l app.kubernetes.io/name=dagster

# Port-forward the webserver
kubectl port-forward -n agentic svc/dagster-webserver 3100:3000
```

### Ingress

The Dagster UI is exposed at `/dagster` via the shared ingress:

```
http://agentic.local/dagster
```

## Monitoring & Observability

### Prometheus Metrics

Metrics are exported at `/api/v1/dagster/metrics`:

- `dagster_runs_total{status}` - Run count by status
- `dagster_asset_materializations_total{asset}` - Materialization count
- `dagster_run_duration_seconds` - Run duration summary
- `dagster_op_duration_seconds{op}` - Op duration summary
- `dagster_active_runs` - Currently active runs gauge
- `dagster_queued_runs` - Queued runs gauge

### Grafana Dashboard

Import `conf/base/grafana/dagster-dashboard.json` into Grafana for:

- Run status overview (success/failure rates)
- Run duration trends
- Asset materialization timeline
- Op-level performance breakdown
- Error rate monitoring

### MLFlow Integration

All Dagster runs are tracked in MLFlow via the `DagsterRunCallback`:

- Run parameters (job name, tags)
- Duration and success metrics
- Error details on failure

### OpenTelemetry

OTLP spans are emitted for:

- Each run lifecycle (start, steps, completion)
- Each op execution
- Asset materialization events
- Schedule/sensor evaluations

View traces in Jaeger at `http://localhost:16686`.

## Migration from APScheduler/Prefect

### From APScheduler

```python
from agentic_assistants.orchestration.dagster_bridge import migrate_apscheduler_job

# Migrate a scheduled function
job, schedule = migrate_apscheduler_job(
    job_func=my_scheduled_function,
    schedule="0 */6 * * *",  # Cron expression
    name="my_migrated_job",
)
```

### From Prefect

The Dagster adapter mirrors the Prefect adapter API:

| Prefect | Dagster |
|---------|---------|
| `@adapter.flow()` | `@adapter.job()` |
| `@adapter.task()` | `@adapter.op()` |
| `pipeline_to_flow()` | `pipeline_to_job()` |
| `task_wrapper()` | `node_to_op()` |
| `run_flow()` | `run_job()` |

### From CronJobs

Replace Kubernetes CronJobs with Dagster schedules for better visibility and management:

```python
# Before: k8s/cronjobs/data-sync-cronjob.yaml
# After:
data_sync_schedule = dg.ScheduleDefinition(
    job=data_sync_job,
    cron_schedule="0 */6 * * *",
    name="data_sync_schedule",
)
```
