"""
Feast Feature Store adapter.

Provides integration with Feast for production feature serving.
"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

from agentic_assistants.features.store import (
    FeatureStore,
    FeatureStoreConfig,
    FeatureVector,
)
from agentic_assistants.features.registry import (
    FeatureView as AgenticFeatureView,
    Feature,
    Entity,
    ValueType,
)
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


class FeastFeatureStore(FeatureStore):
    """
    Feast-based feature store implementation.
    
    This adapter wraps Feast's FeatureStore to provide:
    - Feature view registration and management
    - Online feature serving
    - Historical feature retrieval
    - Feature materialization
    
    Requires:
        pip install feast
    
    Example:
        >>> config = FeatureStoreConfig(
        ...     backend="feast",
        ...     feast_repo_path="./data/feast"
        ... )
        >>> store = FeastFeatureStore(config)
    """
    
    def __init__(self, config: Optional[FeatureStoreConfig] = None):
        """
        Initialize Feast feature store.
        
        Args:
            config: Feature store configuration
        """
        config = config or FeatureStoreConfig(backend="feast")
        super().__init__(config)
        
        self._feast_repo_path = Path(config.feast_repo_path)
        self._feast_store = None
        self._initialized = False
        
        # Create repo directory
        self._feast_repo_path.mkdir(parents=True, exist_ok=True)
        
        # Mapping from agentic views to feast views
        self._view_mapping: Dict[str, Any] = {}
    
    @property
    def feast_store(self):
        """Get or create Feast store instance."""
        if self._feast_store is None:
            try:
                from feast import FeatureStore as FeastFS
                
                # Check if repo exists
                feature_store_yaml = self._feast_repo_path / "feature_store.yaml"
                
                if not feature_store_yaml.exists():
                    self._create_feast_repo()
                
                self._feast_store = FeastFS(repo_path=str(self._feast_repo_path))
                self._initialized = True
                logger.info(f"Initialized Feast store at {self._feast_repo_path}")
                
            except ImportError:
                raise ImportError(
                    "feast is required for Feast integration. "
                    "Install with: pip install feast"
                )
        
        return self._feast_store
    
    def _create_feast_repo(self) -> None:
        """Create a new Feast repository."""
        import yaml
        
        # Create feature_store.yaml
        feast_config = {
            "project": "agentic_features",
            "registry": str(self._feast_repo_path / "registry.db"),
            "provider": "local",
            "online_store": {
                "type": self.config.feast_online_store_type,
            },
            "offline_store": {
                "type": self.config.feast_offline_store_type,
            },
        }
        
        # Configure online store
        if self.config.feast_online_store_type == "redis":
            feast_config["online_store"]["connection_string"] = self.config.redis_url
        elif self.config.feast_online_store_type == "sqlite":
            feast_config["online_store"]["path"] = str(
                self._feast_repo_path / "online_store.db"
            )
        
        feature_store_yaml = self._feast_repo_path / "feature_store.yaml"
        with open(feature_store_yaml, "w") as f:
            yaml.dump(feast_config, f)
        
        logger.info(f"Created Feast repository at {self._feast_repo_path}")
    
    def _convert_to_feast_feature_view(
        self,
        view: AgenticFeatureView,
    ) -> Any:
        """Convert agentic FeatureView to Feast FeatureView."""
        from feast import Entity as FeastEntity
        from feast import Feature as FeastFeature
        from feast import FeatureView as FeastFeatureView
        from feast import FileSource
        from feast.types import Float32, Int64, String, Bool
        
        # Map value types
        type_map = {
            ValueType.INT32: Int64,
            ValueType.INT64: Int64,
            ValueType.FLOAT: Float32,
            ValueType.DOUBLE: Float32,
            ValueType.STRING: String,
            ValueType.BOOL: Bool,
        }
        
        # Create Feast entities
        feast_entities = []
        for entity in view.entities:
            feast_entity = FeastEntity(
                name=entity.name,
                join_keys=entity.join_keys,
                description=entity.description,
            )
            feast_entities.append(feast_entity)
        
        # Create Feast features
        feast_features = []
        for feature in view.features:
            feast_type = type_map.get(feature.dtype, Float32)
            feast_feature = FeastFeature(
                name=feature.name,
                dtype=feast_type,
            )
            feast_features.append(feast_feature)
        
        # Create source
        source_path = view.source or str(
            self._feast_repo_path / "data" / f"{view.name}.parquet"
        )
        
        source = FileSource(
            path=source_path,
            timestamp_field="event_timestamp",
        )
        
        # Create Feast FeatureView
        feast_view = FeastFeatureView(
            name=view.name,
            entities=feast_entities,
            ttl=view.ttl or timedelta(days=1),
            schema=feast_features,
            online=view.online,
            source=source,
            description=view.description,
            tags=view.tags,
        )
        
        return feast_view, feast_entities
    
    def register_feature_view(self, feature_view: AgenticFeatureView) -> None:
        """Register a feature view with Feast."""
        try:
            feast_view, entities = self._convert_to_feast_feature_view(feature_view)
            
            # Apply to Feast
            self.feast_store.apply([*entities, feast_view])
            
            # Store mapping
            self._view_mapping[feature_view.name] = {
                "agentic_view": feature_view,
                "feast_view": feast_view,
            }
            
            logger.info(f"Registered feature view with Feast: {feature_view.name}")
            
        except Exception as e:
            logger.error(f"Failed to register with Feast: {e}")
            raise
    
    def get_feature_view(self, name: str) -> Optional[AgenticFeatureView]:
        """Get a feature view by name."""
        if name in self._view_mapping:
            return self._view_mapping[name]["agentic_view"]
        
        # Try to load from Feast registry
        try:
            feast_view = self.feast_store.get_feature_view(name)
            if feast_view:
                # Convert back to agentic view
                return self._convert_from_feast_view(feast_view)
        except Exception:
            pass
        
        return None
    
    def _convert_from_feast_view(self, feast_view) -> AgenticFeatureView:
        """Convert Feast FeatureView to agentic FeatureView."""
        from feast.types import Float32, Int64, String, Bool
        
        type_map = {
            Float32: ValueType.FLOAT,
            Int64: ValueType.INT64,
            String: ValueType.STRING,
            Bool: ValueType.BOOL,
        }
        
        entities = []
        for entity in feast_view.entities:
            entities.append(Entity(
                name=entity.name,
                join_keys=entity.join_keys,
                description=getattr(entity, "description", ""),
            ))
        
        features = []
        for feature in feast_view.features:
            dtype = type_map.get(type(feature.dtype), ValueType.FLOAT)
            features.append(Feature(
                name=feature.name,
                dtype=dtype,
            ))
        
        return AgenticFeatureView(
            name=feast_view.name,
            entities=entities,
            features=features,
            ttl=feast_view.ttl,
            description=getattr(feast_view, "description", ""),
            tags=getattr(feast_view, "tags", {}),
            online=feast_view.online,
        )
    
    def list_feature_views(self) -> List[str]:
        """List all registered feature view names."""
        try:
            views = self.feast_store.list_feature_views()
            return [v.name for v in views]
        except Exception as e:
            logger.warning(f"Failed to list Feast views: {e}")
            return list(self._view_mapping.keys())
    
    def delete_feature_view(self, name: str) -> bool:
        """Delete a feature view."""
        try:
            # Remove from Feast
            feast_view = self.feast_store.get_feature_view(name)
            if feast_view:
                self.feast_store.delete_feature_view(name)
            
            # Remove from mapping
            if name in self._view_mapping:
                del self._view_mapping[name]
            
            return True
        except Exception as e:
            logger.error(f"Failed to delete feature view: {e}")
            return False
    
    def get_online_features(
        self,
        feature_refs: List[str],
        entity_keys: List[Dict[str, Any]],
    ) -> List[FeatureVector]:
        """Get feature values for online inference."""
        try:
            # Get features from Feast
            response = self.feast_store.get_online_features(
                features=feature_refs,
                entity_rows=entity_keys,
            )
            
            # Convert to FeatureVector
            results = []
            feature_dict = response.to_dict()
            
            for i, entity_key in enumerate(entity_keys):
                features = {}
                for ref in feature_refs:
                    if ":" in ref:
                        feature_name = ref.split(":")[-1]
                    else:
                        feature_name = ref
                    
                    key = feature_name
                    if key in feature_dict:
                        features[feature_name] = feature_dict[key][i]
                
                results.append(FeatureVector(
                    entity_key=entity_key,
                    features=features,
                    feature_view=feature_refs[0].split(":")[0] if feature_refs else "",
                ))
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to get online features: {e}")
            return []
    
    def get_historical_features(
        self,
        feature_refs: List[str],
        entity_df: pd.DataFrame,
        full_feature_names: bool = True,
    ) -> pd.DataFrame:
        """Get historical feature values for training."""
        try:
            # Ensure timestamp column
            if "event_timestamp" not in entity_df.columns:
                entity_df = entity_df.copy()
                entity_df["event_timestamp"] = datetime.utcnow()
            
            # Get historical features from Feast
            response = self.feast_store.get_historical_features(
                features=feature_refs,
                entity_df=entity_df,
                full_feature_names=full_feature_names,
            )
            
            return response.to_df()
            
        except Exception as e:
            logger.error(f"Failed to get historical features: {e}")
            return entity_df
    
    def materialize(
        self,
        feature_views: Optional[List[str]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, int]:
        """Materialize features to the online store."""
        try:
            if end_date is None:
                end_date = datetime.utcnow()
            if start_date is None:
                start_date = end_date - timedelta(days=self.config.default_ttl_days)
            
            if feature_views:
                self.feast_store.materialize(
                    start_date=start_date,
                    end_date=end_date,
                    feature_views=feature_views,
                )
            else:
                self.feast_store.materialize(
                    start_date=start_date,
                    end_date=end_date,
                )
            
            return {view: -1 for view in (feature_views or self.list_feature_views())}
            
        except Exception as e:
            logger.error(f"Failed to materialize: {e}")
            return {}
    
    def push(
        self,
        feature_view: str,
        df: pd.DataFrame,
        to_online: bool = True,
        to_offline: bool = True,
    ) -> int:
        """Push feature values to the store."""
        try:
            # Ensure timestamp
            if "event_timestamp" not in df.columns:
                df = df.copy()
                df["event_timestamp"] = datetime.utcnow()
            
            # For Feast, we typically write to the source and then materialize
            # Write to parquet source
            data_dir = self._feast_repo_path / "data"
            data_dir.mkdir(parents=True, exist_ok=True)
            
            source_path = data_dir / f"{feature_view}.parquet"
            
            if source_path.exists():
                existing_df = pd.read_parquet(source_path)
                df = pd.concat([existing_df, df], ignore_index=True)
            
            df.to_parquet(source_path, index=False)
            
            # Materialize to online store if requested
            if to_online:
                self.materialize(feature_views=[feature_view])
            
            return len(df)
            
        except Exception as e:
            logger.error(f"Failed to push features: {e}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get feature store statistics."""
        return {
            "backend": "feast",
            "repo_path": str(self._feast_repo_path),
            "initialized": self._initialized,
            "feature_views": len(self.list_feature_views()),
            "online_store_type": self.config.feast_online_store_type,
            "offline_store_type": self.config.feast_offline_store_type,
        }
    
    def get_feast_ui_url(self) -> Optional[str]:
        """Get Feast UI URL if available."""
        # Feast UI is typically served on port 6566
        return "http://localhost:6566"
