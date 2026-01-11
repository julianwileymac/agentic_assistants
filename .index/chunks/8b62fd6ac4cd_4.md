# Chunk: 8b62fd6ac4cd_4

- source: `src/agentic_assistants/server/api/config.py`
- lines: 263-359
- chunk: 5/7

```
ver=self.get_server(),
            user=self.get_user(),
            session=self.get_session(),
        )
    
    def export_config(self) -> dict[str, Any]:
        """Export configuration as dictionary."""
        return self.config.to_dict()
    
    def reset_overrides(self) -> None:
        """Reset all runtime overrides."""
        self._runtime_overrides.clear()
    
    def _get_override(self, key: str, default: Any) -> Any:
        """Get value with runtime override."""
        return self._runtime_overrides.get(key, default)
    
    def _validate_log_level(self, level: str) -> None:
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if level.upper() not in valid_levels:
            raise ValueError(f"Invalid log level: {level}")
    
    def _update_log_level(self, level: str) -> None:
        """Update logging level at runtime."""
        import logging
        logging.getLogger().setLevel(getattr(logging, level.upper()))


# Global config manager
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """Get the configuration manager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


# === Endpoints ===


@router.get("", response_model=FullConfigResponse)
async def get_full_config() -> FullConfigResponse:
    """Get complete configuration."""
    logger.debug("Getting full configuration")
    
    manager = get_config_manager()
    return manager.get_full()


@router.get("/export")
async def export_config() -> dict[str, Any]:
    """Export configuration as dictionary."""
    logger.debug("Exporting configuration")
    
    manager = get_config_manager()
    return manager.export_config()


@router.post("/reset")
async def reset_overrides() -> dict[str, str]:
    """Reset all runtime configuration overrides."""
    logger.info("Resetting configuration overrides")
    
    manager = get_config_manager()
    manager.reset_overrides()
    
    return {"status": "reset"}


@router.get("/global", response_model=GlobalConfigResponse)
async def get_global_config() -> GlobalConfigResponse:
    """Get global configuration."""
    logger.debug("Getting global configuration")
    
    manager = get_config_manager()
    return manager.get_global()


@router.patch("/global", response_model=GlobalConfigResponse)
async def update_global_config(updates: GlobalConfigUpdate) -> GlobalConfigResponse:
    """Update global configuration."""
    logger.info("Updating global configuration")
    
    manager = get_config_manager()
    
    try:
        return manager.update_global(updates)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/ollama", response_model=OllamaConfigResponse)
```
