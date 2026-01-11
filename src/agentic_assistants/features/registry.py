"""
Feature definitions and registry.
"""

from dataclasses import dataclass, field
from datetime import timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union


class ValueType(str, Enum):
    """Supported feature value types."""
    
    INT32 = "int32"
    INT64 = "int64"
    FLOAT = "float"
    DOUBLE = "double"
    STRING = "string"
    BOOL = "bool"
    BYTES = "bytes"
    UNIX_TIMESTAMP = "unix_timestamp"
    INT32_LIST = "int32_list"
    INT64_LIST = "int64_list"
    FLOAT_LIST = "float_list"
    DOUBLE_LIST = "double_list"
    STRING_LIST = "string_list"
    BOOL_LIST = "bool_list"


@dataclass
class Entity:
    """
    An entity is a collection of semantically related features.
    
    Example:
        >>> user = Entity(
        ...     name="user",
        ...     join_keys=["user_id"],
        ...     value_type=ValueType.INT64,
        ...     description="A user of the system"
        ... )
    """
    
    name: str
    join_keys: List[str]
    value_type: ValueType = ValueType.INT64
    description: str = ""
    tags: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "join_keys": self.join_keys,
            "value_type": self.value_type.value,
            "description": self.description,
            "tags": self.tags,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Entity":
        return cls(
            name=data["name"],
            join_keys=data["join_keys"],
            value_type=ValueType(data.get("value_type", "int64")),
            description=data.get("description", ""),
            tags=data.get("tags", {}),
        )


@dataclass
class Feature:
    """
    A single feature definition.
    
    Example:
        >>> age = Feature(
        ...     name="age",
        ...     dtype=ValueType.INT32,
        ...     description="User's age in years"
        ... )
    """
    
    name: str
    dtype: ValueType = ValueType.FLOAT
    description: str = ""
    tags: Dict[str, str] = field(default_factory=dict)
    default_value: Optional[Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "dtype": self.dtype.value,
            "description": self.description,
            "tags": self.tags,
            "default_value": self.default_value,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Feature":
        return cls(
            name=data["name"],
            dtype=ValueType(data.get("dtype", "float")),
            description=data.get("description", ""),
            tags=data.get("tags", {}),
            default_value=data.get("default_value"),
        )


@dataclass
class FeatureView:
    """
    A feature view is a group of features from a single data source.
    
    Feature views define:
    - What features to serve
    - What entity they belong to
    - Where the data comes from
    - How long features are valid (TTL)
    
    Example:
        >>> user_features = FeatureView(
        ...     name="user_features",
        ...     entities=[user],
        ...     features=[
        ...         Feature(name="age", dtype=ValueType.INT32),
        ...         Feature(name="tenure_days", dtype=ValueType.INT32),
        ...         Feature(name="is_active", dtype=ValueType.BOOL),
        ...     ],
        ...     ttl=timedelta(days=1),
        ...     source="user_data.parquet"
        ... )
    """
    
    name: str
    entities: List[Entity]
    features: List[Feature]
    ttl: Optional[timedelta] = None
    source: Optional[str] = None  # Path or table name
    batch_source: Optional[str] = None
    stream_source: Optional[str] = None
    description: str = ""
    tags: Dict[str, str] = field(default_factory=dict)
    online: bool = True
    offline: bool = True
    
    def __post_init__(self):
        """Build feature name lookup."""
        self._feature_map = {f.name: f for f in self.features}
    
    def get_feature(self, name: str) -> Optional[Feature]:
        """Get a feature by name."""
        return self._feature_map.get(name)
    
    @property
    def feature_names(self) -> List[str]:
        """Get all feature names."""
        return [f.name for f in self.features]
    
    @property
    def entity_names(self) -> List[str]:
        """Get all entity names."""
        return [e.name for e in self.entities]
    
    @property
    def join_keys(self) -> List[str]:
        """Get all join keys from entities."""
        keys = []
        for entity in self.entities:
            keys.extend(entity.join_keys)
        return list(set(keys))
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "entities": [e.to_dict() for e in self.entities],
            "features": [f.to_dict() for f in self.features],
            "ttl_seconds": self.ttl.total_seconds() if self.ttl else None,
            "source": self.source,
            "batch_source": self.batch_source,
            "stream_source": self.stream_source,
            "description": self.description,
            "tags": self.tags,
            "online": self.online,
            "offline": self.offline,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FeatureView":
        ttl = None
        if data.get("ttl_seconds"):
            ttl = timedelta(seconds=data["ttl_seconds"])
        
        return cls(
            name=data["name"],
            entities=[Entity.from_dict(e) for e in data.get("entities", [])],
            features=[Feature.from_dict(f) for f in data.get("features", [])],
            ttl=ttl,
            source=data.get("source"),
            batch_source=data.get("batch_source"),
            stream_source=data.get("stream_source"),
            description=data.get("description", ""),
            tags=data.get("tags", {}),
            online=data.get("online", True),
            offline=data.get("offline", True),
        )


class FeatureRegistry:
    """
    Registry for managing feature definitions.
    
    The registry stores and manages:
    - Entities
    - Feature Views
    - Feature metadata
    
    Example:
        >>> registry = FeatureRegistry()
        >>> registry.register_entity(user_entity)
        >>> registry.register_feature_view(user_features)
    """
    
    def __init__(self, registry_path: Optional[str] = None):
        """
        Initialize the feature registry.
        
        Args:
            registry_path: Path to persist registry (optional)
        """
        self._entities: Dict[str, Entity] = {}
        self._feature_views: Dict[str, FeatureView] = {}
        self._registry_path = registry_path
        
        if registry_path:
            self._load_registry()
    
    def register_entity(self, entity: Entity) -> None:
        """Register an entity."""
        self._entities[entity.name] = entity
        self._save_registry()
    
    def get_entity(self, name: str) -> Optional[Entity]:
        """Get an entity by name."""
        return self._entities.get(name)
    
    def list_entities(self) -> List[str]:
        """List all registered entity names."""
        return list(self._entities.keys())
    
    def register_feature_view(self, feature_view: FeatureView) -> None:
        """Register a feature view."""
        # Also register associated entities
        for entity in feature_view.entities:
            self._entities[entity.name] = entity
        
        self._feature_views[feature_view.name] = feature_view
        self._save_registry()
    
    def get_feature_view(self, name: str) -> Optional[FeatureView]:
        """Get a feature view by name."""
        return self._feature_views.get(name)
    
    def list_feature_views(self) -> List[str]:
        """List all registered feature view names."""
        return list(self._feature_views.keys())
    
    def delete_feature_view(self, name: str) -> bool:
        """Delete a feature view."""
        if name in self._feature_views:
            del self._feature_views[name]
            self._save_registry()
            return True
        return False
    
    def get_feature(self, feature_ref: str) -> Optional[Feature]:
        """
        Get a feature by reference.
        
        Args:
            feature_ref: Feature reference (view:feature)
            
        Returns:
            Feature or None
        """
        if ":" not in feature_ref:
            return None
        
        view_name, feature_name = feature_ref.split(":", 1)
        view = self.get_feature_view(view_name)
        
        if view:
            return view.get_feature(feature_name)
        return None
    
    def _load_registry(self) -> None:
        """Load registry from disk."""
        import json
        from pathlib import Path
        
        if not self._registry_path:
            return
        
        registry_file = Path(self._registry_path) / "registry.json"
        
        if not registry_file.exists():
            return
        
        try:
            with open(registry_file, "r") as f:
                data = json.load(f)
            
            for entity_data in data.get("entities", []):
                entity = Entity.from_dict(entity_data)
                self._entities[entity.name] = entity
            
            for view_data in data.get("feature_views", []):
                view = FeatureView.from_dict(view_data)
                self._feature_views[view.name] = view
                
        except Exception as e:
            from agentic_assistants.utils.logging import get_logger
            logger = get_logger(__name__)
            logger.warning(f"Failed to load registry: {e}")
    
    def _save_registry(self) -> None:
        """Save registry to disk."""
        import json
        from pathlib import Path
        
        if not self._registry_path:
            return
        
        registry_dir = Path(self._registry_path)
        registry_dir.mkdir(parents=True, exist_ok=True)
        registry_file = registry_dir / "registry.json"
        
        data = {
            "entities": [e.to_dict() for e in self._entities.values()],
            "feature_views": [v.to_dict() for v in self._feature_views.values()],
        }
        
        with open(registry_file, "w") as f:
            json.dump(data, f, indent=2)
    
    def to_dict(self) -> Dict[str, Any]:
        """Export registry to dictionary."""
        return {
            "entities": [e.to_dict() for e in self._entities.values()],
            "feature_views": [v.to_dict() for v in self._feature_views.values()],
        }
