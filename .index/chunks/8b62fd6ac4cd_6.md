# Chunk: 8b62fd6ac4cd_6

- source: `src/agentic_assistants/server/api/config.py`
- lines: 430-487
- chunk: 7/7

```
ponse)
async def get_session_config() -> SessionConfigResponse:
    """Get session configuration."""
    logger.debug("Getting session configuration")
    
    manager = get_config_manager()
    return manager.get_session()


@router.patch("/session", response_model=SessionConfigResponse)
async def update_session_config(updates: SessionConfigUpdate) -> SessionConfigResponse:
    """Update session configuration."""
    logger.info("Updating session configuration")
    
    manager = get_config_manager()
    return manager.update_session(updates)


@router.get("/validate")
async def validate_config() -> dict[str, Any]:
    """Validate current configuration."""
    logger.debug("Validating configuration")
    
    manager = get_config_manager()
    errors = []
    warnings = []
    
    # Validate data directory
    config = manager.config
    if not Path(config.data_dir).exists():
        warnings.append(f"Data directory does not exist: {config.data_dir}")
    
    # Validate Ollama host
    try:
        import httpx
        response = httpx.get(f"{config.ollama.host}/api/tags", timeout=2)
        if response.status_code != 200:
            warnings.append("Ollama server is not responding")
    except Exception:
        warnings.append("Cannot connect to Ollama server")
    
    # Validate MLFlow if enabled
    if config.mlflow_enabled:
        try:
            import httpx
            response = httpx.get(f"{config.mlflow.tracking_uri}/health", timeout=2)
            if response.status_code != 200:
                warnings.append("MLFlow server is not responding")
        except Exception:
            warnings.append("Cannot connect to MLFlow server")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }

```
