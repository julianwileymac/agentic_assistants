# Chunk: d88adcef90d7_0

- source: `k8s/configmap.yaml`
- lines: 1-32
- chunk: 1/1

```
apiVersion: v1
kind: ConfigMap
metadata:
  name: agentic-config
  namespace: agentic
  labels:
    app: agentic-assistants
data:
  # Application settings
  AGENTIC_LOG_LEVEL: "INFO"
  AGENTIC_DATA_DIR: "/data"
  
  # Cache settings
  CACHE_BACKEND: "redis"
  REDIS_URL: "redis://redis:6379"
  CACHE_DEFAULT_TTL: "3600"
  
  # MLFlow settings
  MLFLOW_TRACKING_URI: "http://mlflow:5000"
  
  # Telemetry settings
  OTEL_EXPORTER_OTLP_ENDPOINT: "http://otel-collector:4317"
  OTEL_SERVICE_NAME: "agentic-assistants"
  
  # Feature store settings
  FEATURE_STORE_TYPE: "local"
  FEATURE_STORE_PATH: "/data/features"
  
  # Vector DB settings
  VECTORDB_PATH: "/data/vectordb"
  VECTORDB_EMBEDDING_MODEL: "all-MiniLM-L6-v2"
```
