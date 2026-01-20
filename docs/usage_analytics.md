# Usage Analytics and Observability

The framework includes a comprehensive usage tracking and meta-analysis system for monitoring framework usage and generating improvement suggestions.

## Overview

The observability module provides:

- **Usage Tracking**: Record all framework interactions
- **Analytics**: Aggregate usage statistics
- **Meta-Analysis**: AI-powered improvement suggestions
- **Health Monitoring**: Framework health assessment

## Components

### UsageTracker

Records usage events to a SQLite database:

```python
from agentic_assistants.observability import UsageTracker

tracker = UsageTracker()

# Track an agent run
tracker.track_agent_run(
    agent_name="researcher",
    framework="crewai",
    model="llama3.2",
    duration_seconds=15.5,
    success=True,
    tokens_input=150,
    tokens_output=500,
)

# Track API call
tracker.track_api_call(
    endpoint="/api/v1/chat",
    method="POST",
    status_code=200,
    duration_ms=234,
    success=True,
)

# Track RAG query
tracker.track_rag_query(
    knowledge_base="my_project",
    query="What is quantum computing?",
    num_results=5,
    duration_ms=45,
    top_score=0.92,
    avg_score=0.78,
)
```

### MetaAnalyzer

Analyzes usage patterns and generates suggestions:

```python
from agentic_assistants.observability import MetaAnalyzer, UsageTracker

tracker = UsageTracker()
analyzer = MetaAnalyzer(tracker)

# Run analysis
report = analyzer.run_analysis(days=7)

# Access results
print(f"Health Score: {report.health_score}")
print(f"Summary: {report.summary}")

for suggestion in report.suggestions:
    print(f"[{suggestion.priority}] {suggestion.title}")
    print(f"  Action: {suggestion.recommended_action}")
```

## Event Types

### AgentRunEvent

Tracks agent/crew executions:

```python
tracker.track_agent_run(
    agent_name="researcher",
    framework="crewai",  # crewai, langgraph, autogen, etc.
    model="llama3.2",
    duration_seconds=15.5,
    success=True,
    error_message=None,  # Set if failed
    tokens_input=150,
    tokens_output=500,
    task_type="research",
    tools_used=["web_search", "calculator"],
    user_id="user123",
    session_id="session456",
    project_id="project789",
)
```

### APICallEvent

Tracks API requests:

```python
tracker.track_api_call(
    endpoint="/api/v1/assistant/chat",
    method="POST",
    status_code=200,
    duration_ms=234,
    success=True,
    request_size_bytes=1024,
    response_size_bytes=2048,
)
```

### RAGQueryEvent

Tracks knowledge base queries:

```python
tracker.track_rag_query(
    knowledge_base="project_kb",
    query="How to deploy?",
    num_results=5,
    duration_ms=45,
    top_score=0.92,
    avg_score=0.78,
    embedding_model="nomic-embed-text",
    used_for_generation=True,
)
```

### ErrorEvent

Tracks errors:

```python
tracker.track_error(
    error_type="ConnectionError",
    error_message="Failed to connect to Ollama",
    component="ollama_adapter",
    stack_trace="...",
    framework="crewai",
    recoverable=True,
    resolution="Retried successfully",
)
```

### UserInteractionEvent

Tracks user interactions:

```python
tracker.track_user_interaction(
    interaction_type="chat",
    feature_used="coding_helper",
    input_length=150,
    response_length=500,
    duration_ms=2500,
    satisfaction_score=4,  # 1-5
)
```

## Analytics

### Get Usage Analytics

```python
analytics = tracker.get_analytics(days=7)

print(f"Period: {analytics.period_start} to {analytics.period_end}")
print(f"Total Events: {analytics.total_events}")
print(f"Agent Runs: {analytics.total_agent_runs}")
print(f"API Calls: {analytics.total_api_calls}")
print(f"RAG Queries: {analytics.total_rag_queries}")
print(f"Errors: {analytics.total_errors}")
print(f"Avg Response Time: {analytics.avg_response_time_ms}ms")
print(f"RAG Effectiveness: {analytics.rag_effectiveness_score}")
```

### Framework Statistics

```python
for stats in analytics.framework_stats:
    print(f"\n{stats.framework}:")
    print(f"  Total Runs: {stats.total_runs}")
    print(f"  Success Rate: {(1-stats.error_rate)*100:.1f}%")
    print(f"  Avg Duration: {stats.avg_duration_seconds:.1f}s")
```

### Query Events

```python
# Get recent events
events = tracker.get_events(
    event_type="agent_run",
    start_time=datetime.utcnow() - timedelta(days=1),
    project_id="my_project",
    limit=100,
)

for event in events:
    print(f"{event['timestamp']}: {event['agent_name']} - {event['framework']}")
```

## Meta-Analysis

### Health Score

The health score (0-100) is calculated based on:

- Error rates across frameworks
- RAG effectiveness
- Number of critical/high priority issues
- Overall error count

```python
# Get health summary
summary = analyzer.get_health_summary()

print(f"Health Score: {summary['health_score']}")
print(f"Status: {summary['status']}")  # excellent, good, fair, needs_attention
print(f"Error Rate: {summary['error_rate']*100:.1f}%")

for issue in summary['top_issues']:
    print(f"  - {issue}")
```

### Improvement Suggestions

Suggestions are generated based on:

- Error patterns
- Performance bottlenecks
- Underutilized features
- Configuration optimizations

```python
suggestions = analyzer.generate_suggestions(days=7)

for s in suggestions:
    print(f"\n[{s.priority}] {s.title}")
    print(f"Category: {s.category}")
    print(f"Description: {s.description}")
    print(f"Action: {s.recommended_action}")
    print(f"Impact: {s.estimated_impact}")
```

### Suggestion Categories

| Category | Description |
|----------|-------------|
| `performance` | Performance optimizations |
| `reliability` | Reliability improvements |
| `cost_optimization` | Cost reduction opportunities |
| `configuration` | Configuration improvements |
| `feature_adoption` | Underutilized features |
| `error_prevention` | Error prevention measures |
| `workflow_improvement` | Workflow optimizations |

### Suggestion Priorities

| Priority | Description |
|----------|-------------|
| `critical` | Requires immediate attention |
| `high` | Should be addressed soon |
| `medium` | Recommended improvement |
| `low` | Nice to have |

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/assistant/analytics` | GET | Get usage analytics |
| `/api/v1/assistant/health` | GET | Get health summary |
| `/api/v1/assistant/suggestions` | GET | Get improvement suggestions |
| `/api/v1/assistant/analyze` | POST | Run meta-analysis |

### Example: Get Analytics

```bash
curl "http://localhost:8080/api/v1/assistant/analytics?days=7"
```

### Example: Get Suggestions

```bash
curl "http://localhost:8080/api/v1/assistant/suggestions?priority=high&limit=5"
```

## WebUI Dashboard

Access the analytics dashboard at `/assistant/analytics`:

- **Health Score**: Visual health indicator
- **Usage Stats**: Event counts and trends
- **Framework Comparison**: Compare framework performance
- **Suggestions**: View and act on recommendations

## Configuration

Configure tracking in your `.env`:

```bash
# Enable usage tracking
ASSISTANT_USAGE_TRACKING_ENABLED=true

# Database location
ASSISTANT_USAGE_DB_PATH=./data/observability/usage.db

# Meta-analysis interval
ASSISTANT_META_ANALYSIS_INTERVAL_HOURS=24
```

## Data Retention

Clean up old events periodically:

```python
# Remove events older than 90 days
deleted = tracker.cleanup_old_events(days_to_keep=90)
print(f"Deleted {deleted} old events")
```

## Best Practices

1. **Enable Tracking**: Keep usage tracking enabled for insights
2. **Review Regularly**: Check the analytics dashboard weekly
3. **Act on Suggestions**: Implement high-priority recommendations
4. **Monitor Health Score**: Keep it above 70
5. **Clean Up Data**: Periodically remove old events

## Integration with Adapters

All framework adapters automatically track usage when connected to a tracker:

```python
from agentic_assistants.adapters import CrewAIAdapter
from agentic_assistants.observability import UsageTracker

tracker = UsageTracker()
adapter = CrewAIAdapter(usage_tracker=tracker)

# Runs are automatically tracked
result = adapter.run_crew(crew, inputs={...})
```

## See Also

- [Framework Assistant](framework_assistant.md) - Built-in assistant
- [Adapters](adapters.md) - Framework adapters
- [Configuration](configuration.md) - Configuration options
