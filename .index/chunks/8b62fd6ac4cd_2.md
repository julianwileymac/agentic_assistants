# Chunk: 8b62fd6ac4cd_2

- source: `src/agentic_assistants/server/api/config.py`
- lines: 150-212
- chunk: 3/7

```
l=self._get_override("log_level", self.config.log_level),
            data_dir=str(self.config.data_dir),
        )
    
    def update_global(self, updates: GlobalConfigUpdate) -> GlobalConfigResponse:
        """Update global configuration."""
        if updates.mlflow_enabled is not None:
            self._runtime_overrides["mlflow_enabled"] = updates.mlflow_enabled
        if updates.telemetry_enabled is not None:
            self._runtime_overrides["telemetry_enabled"] = updates.telemetry_enabled
        if updates.log_level is not None:
            self._validate_log_level(updates.log_level)
            self._runtime_overrides["log_level"] = updates.log_level
            self._update_log_level(updates.log_level)
        
        return self.get_global()
    
    def get_ollama(self) -> OllamaConfigResponse:
        """Get Ollama configuration."""
        return OllamaConfigResponse(
            host=self._get_override("ollama_host", self.config.ollama.host),
            default_model=self._get_override("ollama_model", self.config.ollama.default_model),
            timeout=self._get_override("ollama_timeout", self.config.ollama.timeout),
        )
    
    def update_ollama(self, updates: OllamaConfigUpdate) -> OllamaConfigResponse:
        """Update Ollama configuration."""
        if updates.host is not None:
            self._runtime_overrides["ollama_host"] = updates.host
        if updates.default_model is not None:
            self._runtime_overrides["ollama_model"] = updates.default_model
        if updates.timeout is not None:
            self._runtime_overrides["ollama_timeout"] = updates.timeout
        
        return self.get_ollama()
    
    def get_mlflow(self) -> MLFlowConfigResponse:
        """Get MLFlow configuration."""
        return MLFlowConfigResponse(
            tracking_uri=self._get_override("mlflow_uri", self.config.mlflow.tracking_uri),
            experiment_name=self._get_override("mlflow_experiment", self.config.mlflow.experiment_name),
            artifact_location=self.config.mlflow.artifact_location,
        )
    
    def update_mlflow(self, updates: MLFlowConfigUpdate) -> MLFlowConfigResponse:
        """Update MLFlow configuration."""
        if updates.tracking_uri is not None:
            self._runtime_overrides["mlflow_uri"] = updates.tracking_uri
        if updates.experiment_name is not None:
            self._runtime_overrides["mlflow_experiment"] = updates.experiment_name
        
        return self.get_mlflow()
    
    def get_vectordb(self) -> VectorDBConfigResponse:
        """Get vector database configuration."""
        return VectorDBConfigResponse(
            backend=self.config.vectordb.backend,
            path=str(self.config.vectordb.path),
            embedding_model=self.config.vectordb.embedding_model,
            embedding_dimension=self.config.vectordb.embedding_dimension,
        )
    
```
