# Trace Store Offline Sync

Use this pattern when running disconnected from an OTLP collector.

```bash
agentic traces status
agentic traces export -o ./trace-backup
agentic traces import -i ./trace-backup -e http://localhost:4318
```

`TraceStore` keeps pending OTLP JSON files until a collector becomes reachable.

