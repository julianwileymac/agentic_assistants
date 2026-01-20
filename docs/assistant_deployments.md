# Framework Assistant Multi-Deployment Guide

The Framework Assistant supports multiple Ollama deployment endpoints for high availability, load balancing, and flexible deployment scenarios. This guide explains how to configure and manage multiple endpoints.

## Overview

The assistant can connect to multiple Ollama instances and will automatically:
- Try endpoints in priority order (lower number = higher priority)
- Failover to backup endpoints if the primary is unavailable
- Report health status for all configured endpoints

## Configuration

### Default Configuration

By default, the assistant connects to a local Ollama instance:

```json
{
  "ollamaEndpoints": [
    {
      "url": "http://localhost:11434",
      "priority": 1,
      "name": "local",
      "enabled": true
    }
  ]
}
```

### Adding Multiple Endpoints

You can configure multiple endpoints for redundancy. The assistant will try them in priority order:

```json
{
  "ollamaEndpoints": [
    {
      "url": "http://localhost:11434",
      "priority": 1,
      "name": "local",
      "enabled": true
    },
    {
      "url": "http://ollama.cluster.local:11434",
      "priority": 2,
      "name": "kubernetes-cluster",
      "enabled": true
    },
    {
      "url": "http://ollama-backup.internal:11434",
      "priority": 3,
      "name": "backup",
      "enabled": true
    }
  ]
}
```

### Endpoint Properties

| Property | Type | Description |
|----------|------|-------------|
| `url` | string | The Ollama API URL (e.g., `http://localhost:11434`) |
| `priority` | number | Priority order (1 = highest priority, tried first) |
| `name` | string | Human-readable name for the endpoint |
| `enabled` | boolean | Whether this endpoint should be used |

## API Endpoints

### List Endpoints with Health Status

```http
GET /api/v1/assistant/endpoints
```

Returns all configured endpoints with real-time health checks:

```json
{
  "endpoints": [
    {
      "url": "http://localhost:11434",
      "priority": 1,
      "name": "local",
      "enabled": true,
      "health": {
        "status": "healthy",
        "url": "http://localhost:11434",
        "models": ["llama3.2", "codellama"],
        "model_count": 2
      }
    }
  ],
  "total": 1,
  "healthy_count": 1
}
```

### Add an Endpoint

```http
POST /api/v1/assistant/endpoints/add
Content-Type: application/json

{
  "url": "http://new-ollama:11434",
  "priority": 2,
  "name": "new-deployment",
  "enabled": true
}
```

### Remove an Endpoint

```http
DELETE /api/v1/assistant/endpoints/{endpoint_name}
```

### Test Connection

```http
GET /api/v1/assistant/test
```

Tests all endpoints and returns the status:

```json
{
  "status": "ok",
  "model": "llama3.2",
  "ollama_host": "http://localhost:11434",
  "message": "Connected to Ollama successfully"
}
```

## Deployment Scenarios

### 1. Local Development

Single local Ollama instance:

```json
{
  "ollamaEndpoints": [
    {"url": "http://localhost:11434", "priority": 1, "name": "local"}
  ]
}
```

### 2. Kubernetes Cluster with Local Fallback

Primary on Kubernetes, fallback to local:

```json
{
  "ollamaEndpoints": [
    {"url": "http://ollama.model-serving:11434", "priority": 1, "name": "k8s-primary"},
    {"url": "http://localhost:11434", "priority": 2, "name": "local-fallback"}
  ]
}
```

### 3. Multi-Region Deployment

Multiple regions with geographic priority:

```json
{
  "ollamaEndpoints": [
    {"url": "http://ollama-us-east.internal:11434", "priority": 1, "name": "us-east"},
    {"url": "http://ollama-us-west.internal:11434", "priority": 2, "name": "us-west"},
    {"url": "http://ollama-eu.internal:11434", "priority": 3, "name": "europe"}
  ]
}
```

### 4. Development vs Production

Separate development and production endpoints:

```json
{
  "ollamaEndpoints": [
    {"url": "http://localhost:11434", "priority": 1, "name": "dev", "enabled": true},
    {"url": "http://prod-ollama:11434", "priority": 2, "name": "prod", "enabled": false}
  ]
}
```

Toggle `enabled` based on environment.

## Troubleshooting

### No Healthy Endpoints

If you see "No healthy Ollama endpoints available":

1. **Check Ollama is running**: Run `ollama serve` locally
2. **Verify network connectivity**: Ensure the endpoint URLs are accessible
3. **Check firewall rules**: Ollama typically runs on port 11434
4. **Use the endpoints API**: Call `GET /api/v1/assistant/endpoints` to see detailed health status

### Model Not Found

If you see "Model not found":

1. **Pull the model**: Run `ollama pull <model-name>`
2. **Check model name**: Verify the model name in assistant settings matches an installed model
3. **List available models**: Run `ollama list` to see installed models

### Connection Timeouts

If requests are timing out:

1. **Check model loading**: First request may be slow while model loads
2. **Verify resources**: Ensure the Ollama server has adequate CPU/GPU resources
3. **Reduce message length**: Shorter context may process faster

## Best Practices

1. **Always have a fallback**: Configure at least one backup endpoint
2. **Monitor endpoint health**: Regularly check `/api/v1/assistant/endpoints`
3. **Use meaningful names**: Name endpoints clearly (e.g., "prod-us-east", "dev-local")
4. **Test before deploying**: Verify new endpoints work before setting high priority
5. **Keep local fallback**: A local Ollama instance provides resilience during network issues

## Related Documentation

- [Framework Assistant Configuration](./framework_assistant.md)
- [Ollama Fine-tuning](./ollama_finetuning.md)
- [Configuration Guide](./configuration.md)
