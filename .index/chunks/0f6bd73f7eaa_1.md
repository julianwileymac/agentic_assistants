# Chunk: 0f6bd73f7eaa_1

- source: `docs/installation.md`
- lines: 149-189
- chunk: 2/2

```
ry running `ollama --version`.

### MLFlow Connection Error

```
Failed to initialize MLFlow
```

**Solution**: Start the MLFlow server with `agentic mlflow start` or disable tracking with `AGENTIC_MLFLOW_ENABLED=false`.

### Port Already in Use

```
Port 5000 is already in use
```

**Solution**: Either stop the conflicting service or change the port in `.env`:
```bash
MLFLOW_TRACKING_URI=http://localhost:5001
```

### Poetry Not Found

```
poetry: command not found
```

**Solution**: Install Poetry:
```bash
pip install poetry
# Or
curl -sSL https://install.python-poetry.org | python3 -
```

## Next Steps

- Explore the [CLI Reference](cli_reference.md)
- Try the [example notebooks](../notebooks/)
- Read the [Architecture Overview](architecture.md)

```
