"""
Abstract Feature Store interface.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import pandas as pd


@dataclass
class FeatureStoreConfig:
    """Configuration for feature store backends."""
    
    # Backend selection
    backend: str = "local"  # local, feast
    
    # Storage paths
    registry_path: str = "./data/features/registry"
    online_store_path: str = "./data/features/online"
    offline_store_path: str = "./data/features/offline"
    
    # Feast-specific settings
    feast_repo_path: str = "./data/feast"
    feast_registry_type: str = "file"  # file, sql, s3
    feast_online_store_type: str = "sqlite"  # sqlite, redis
    feast_offline_store_type: str = "file"  # file, bigquery, redshift
    
    # Redis settings for online store
    redis_url: str = "redis://localhost:6379"
    
    # SQLite settings
    sqlite_path: str = "./data/features/feature_store.db"
    
    # Caching
    enable_cache: bool = True
    cache_ttl_seconds: int = 300
    
    # Materialization settings
    default_ttl_days: int = 30
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "backend": self.backend,
            "registry_path": self.registry_path,
            "online_store_path": self.online_store_path,
            "offline_store_path": self.offline_store_path,
            "enable_cache": self.enable_cache,
        }


@dataclass
class FeatureVector:
    """
    A vector of feature values for an entity.
    """
    
    entity_key: Dict[str, Any]
    features: Dict[str, Any]
    feature_view: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def get(self, feature_name: str, default: Any = None) -> Any:
        """Get a feature value by name."""
        return self.features.get(feature_name, default)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "entity_key": self.entity_key,
            "features": self.features,
            "feature_view": self.feature_view,
            "timestamp": self.timestamp.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FeatureVector":
        return cls(
            entity_key=data["entity_key"],
            features=data["features"],
            feature_view=data["feature_view"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
        )


class FeatureStore(ABC):
    """
    Abstract base class for feature stores.
    
    Feature stores manage the storage and retrieval of ML features
    for both training (offline) and inference (online) use cases.
    """
    
    def __init__(self, config: FeatureStoreConfig):
        """
        Initialize the feature store.
        
        Args:
            config: Feature store configuration
        """
        self.config = config
    
    @abstractmethod
    def register_feature_view(self, feature_view: "FeatureView") -> None:
        """
        Register a feature view with the store.
        
        Args:
            feature_view: Feature view definition
        """
        pass
    
    @abstractmethod
    def get_feature_view(self, name: str) -> Optional["FeatureView"]:
        """
        Get a feature view by name.
        
        Args:
            name: Feature view name
            
        Returns:
            Feature view or None if not found
        """
        pass
    
    @abstractmethod
    def list_feature_views(self) -> List[str]:
        """
        List all registered feature view names.
        
        Returns:
            List of feature view names
        """
        pass
    
    @abstractmethod
    def delete_feature_view(self, name: str) -> bool:
        """
        Delete a feature view.
        
        Args:
            name: Feature view name
            
        Returns:
            True if deleted
        """
        pass
    
    @abstractmethod
    def get_online_features(
        self,
        feature_refs: List[str],
        entity_keys: List[Dict[str, Any]],
    ) -> List[FeatureVector]:
        """
        Get feature values for online inference.
        
        Args:
            feature_refs: List of feature references (view:feature)
            entity_keys: List of entity key dictionaries
            
        Returns:
            List of FeatureVector objects
        """
        pass
    
    @abstractmethod
    def get_historical_features(
        self,
        feature_refs: List[str],
        entity_df: pd.DataFrame,
        full_feature_names: bool = True,
    ) -> pd.DataFrame:
        """
        Get historical feature values for training.
        
        Args:
            feature_refs: List of feature references
            entity_df: DataFrame with entity keys and timestamps
            full_feature_names: Include view name in column names
            
        Returns:
            DataFrame with features joined to entities
        """
        pass
    
    @abstractmethod
    def materialize(
        self,
        feature_views: Optional[List[str]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, int]:
        """
        Materialize features to the online store.
        
        Args:
            feature_views: Views to materialize (all if None)
            start_date: Start of materialization window
            end_date: End of materialization window
            
        Returns:
            Dict mapping view names to rows materialized
        """
        pass
    
    @abstractmethod
    def push(
        self,
        feature_view: str,
        df: pd.DataFrame,
        to_online: bool = True,
        to_offline: bool = True,
    ) -> int:
        """
        Push feature values to the store.
        
        Args:
            feature_view: Target feature view
            df: DataFrame with entity keys and feature values
            to_online: Push to online store
            to_offline: Push to offline store
            
        Returns:
            Number of rows pushed
        """
        pass
    
    def get_feature(
        self,
        feature_ref: str,
        entity_key: Dict[str, Any],
    ) -> Optional[Any]:
        """
        Get a single feature value.
        
        Args:
            feature_ref: Feature reference (view:feature)
            entity_key: Entity key dictionary
            
        Returns:
            Feature value or None
        """
        vectors = self.get_online_features([feature_ref], [entity_key])
        if vectors and vectors[0].features:
            # Extract feature name from ref
            feature_name = feature_ref.split(":")[-1]
            return vectors[0].features.get(feature_name)
        return None
    
    def apply(self, objects: List[Any]) -> None:
        """
        Apply multiple feature definitions.
        
        Args:
            objects: List of Feature Views, Entities, etc.
        """
        from agentic_assistants.features.registry import FeatureView, Entity
        
        for obj in objects:
            if isinstance(obj, FeatureView):
                self.register_feature_view(obj)
            # Entities are typically registered with feature views
    
    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """Get feature store statistics."""
        pass
