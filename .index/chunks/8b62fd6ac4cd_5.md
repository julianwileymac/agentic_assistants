# Chunk: 8b62fd6ac4cd_5

- source: `src/agentic_assistants/server/api/config.py`
- lines: 348-440
- chunk: 6/7

```
.info("Updating global configuration")
    
    manager = get_config_manager()
    
    try:
        return manager.update_global(updates)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/ollama", response_model=OllamaConfigResponse)
async def get_ollama_config() -> OllamaConfigResponse:
    """Get Ollama configuration."""
    logger.debug("Getting Ollama configuration")
    
    manager = get_config_manager()
    return manager.get_ollama()


@router.patch("/ollama", response_model=OllamaConfigResponse)
async def update_ollama_config(updates: OllamaConfigUpdate) -> OllamaConfigResponse:
    """Update Ollama configuration."""
    logger.info("Updating Ollama configuration")
    
    manager = get_config_manager()
    return manager.update_ollama(updates)


@router.get("/mlflow", response_model=MLFlowConfigResponse)
async def get_mlflow_config() -> MLFlowConfigResponse:
    """Get MLFlow configuration."""
    logger.debug("Getting MLFlow configuration")
    
    manager = get_config_manager()
    return manager.get_mlflow()


@router.patch("/mlflow", response_model=MLFlowConfigResponse)
async def update_mlflow_config(updates: MLFlowConfigUpdate) -> MLFlowConfigResponse:
    """Update MLFlow configuration."""
    logger.info("Updating MLFlow configuration")
    
    manager = get_config_manager()
    return manager.update_mlflow(updates)


@router.get("/vectordb", response_model=VectorDBConfigResponse)
async def get_vectordb_config() -> VectorDBConfigResponse:
    """Get vector database configuration."""
    logger.debug("Getting vector database configuration")
    
    manager = get_config_manager()
    return manager.get_vectordb()


@router.get("/server", response_model=ServerConfigResponse)
async def get_server_config() -> ServerConfigResponse:
    """Get server configuration."""
    logger.debug("Getting server configuration")
    
    manager = get_config_manager()
    return manager.get_server()


@router.get("/user", response_model=UserConfigResponse)
async def get_user_config() -> UserConfigResponse:
    """Get user configuration."""
    logger.debug("Getting user configuration")
    
    manager = get_config_manager()
    return manager.get_user()


@router.patch("/user", response_model=UserConfigResponse)
async def update_user_config(updates: UserConfigUpdate) -> UserConfigResponse:
    """Update user configuration."""
    logger.info("Updating user configuration")
    
    manager = get_config_manager()
    return manager.update_user(updates)


@router.get("/session", response_model=SessionConfigResponse)
async def get_session_config() -> SessionConfigResponse:
    """Get session configuration."""
    logger.debug("Getting session configuration")
    
    manager = get_config_manager()
    return manager.get_session()


@router.patch("/session", response_model=SessionConfigResponse)
```
