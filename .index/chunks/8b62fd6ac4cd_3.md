# Chunk: 8b62fd6ac4cd_3

- source: `src/agentic_assistants/server/api/config.py`
- lines: 205-273
- chunk: 4/7

```
        return VectorDBConfigResponse(
            backend=self.config.vectordb.backend,
            path=str(self.config.vectordb.path),
            embedding_model=self.config.vectordb.embedding_model,
            embedding_dimension=self.config.vectordb.embedding_dimension,
        )
    
    def get_server(self) -> ServerConfigResponse:
        """Get server configuration."""
        return ServerConfigResponse(
            host=self.config.server.host,
            port=self.config.server.port,
            enable_mcp=self.config.server.enable_mcp,
            enable_rest=self.config.server.enable_rest,
        )
    
    def get_user(self) -> UserConfigResponse:
        """Get user configuration."""
        return UserConfigResponse(
            user_id=self.config.user.user_id,
            home_dir=str(self.config.user.home_dir),
            preferences=self._get_override("user_preferences", self.config.user.preferences),
        )
    
    def update_user(self, updates: UserConfigUpdate) -> UserConfigResponse:
        """Update user configuration."""
        if updates.preferences is not None:
            current = self._get_override("user_preferences", self.config.user.preferences)
            current.update(updates.preferences)
            self._runtime_overrides["user_preferences"] = current
        
        return self.get_user()
    
    def get_session(self) -> SessionConfigResponse:
        """Get session configuration."""
        return SessionConfigResponse(
            session_id=self.config.session_config.session_id,
            memory_limit_mb=self._get_override("session_memory", self.config.session_config.memory_limit_mb),
            persist_interactions=self._get_override("session_persist", self.config.session_config.persist_interactions),
            shared_artifact_dir=str(self.config.session_config.shared_artifact_dir),
        )
    
    def update_session(self, updates: SessionConfigUpdate) -> SessionConfigResponse:
        """Update session configuration."""
        if updates.memory_limit_mb is not None:
            self._runtime_overrides["session_memory"] = updates.memory_limit_mb
        if updates.persist_interactions is not None:
            self._runtime_overrides["session_persist"] = updates.persist_interactions
        
        return self.get_session()
    
    def get_full(self) -> FullConfigResponse:
        """Get complete configuration."""
        return FullConfigResponse(
            global_config=self.get_global(),
            ollama=self.get_ollama(),
            mlflow=self.get_mlflow(),
            vectordb=self.get_vectordb(),
            server=self.get_server(),
            user=self.get_user(),
            session=self.get_session(),
        )
    
    def export_config(self) -> dict[str, Any]:
        """Export configuration as dictionary."""
        return self.config.to_dict()
    
    def reset_overrides(self) -> None:
```
