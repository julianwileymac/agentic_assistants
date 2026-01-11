"""
Lightweight local feature store implementation.

Uses SQLite for online store and Parquet for offline store.
"""

import json
import sqlite3
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
    FeatureView,
    FeatureRegistry,
)
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


class LocalFeatureStore(FeatureStore):
    """
    Local feature store using SQLite and Parquet.
    
    Architecture:
    - Online Store: SQLite for low-latency key-value lookups
    - Offline Store: Parquet files for historical features
    - Registry: JSON files for feature definitions
    
    Example:
        >>> store = LocalFeatureStore(FeatureStoreConfig())
        >>> store.register_feature_view(user_features)
        >>> store.push("user_features", df)
        >>> features = store.get_online_features(
        ...     ["user_features:age"],
        ...     [{"user_id": 123}]
        ... )
    """
    
    def __init__(self, config: Optional[FeatureStoreConfig] = None):
        """
        Initialize local feature store.
        
        Args:
            config: Feature store configuration
        """
        config = config or FeatureStoreConfig(backend="local")
        super().__init__(config)
        
        # Create directories
        self._registry_path = Path(config.registry_path)
        self._online_path = Path(config.online_store_path)
        self._offline_path = Path(config.offline_store_path)
        
        self._registry_path.mkdir(parents=True, exist_ok=True)
        self._online_path.mkdir(parents=True, exist_ok=True)
        self._offline_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize registry
        self._registry = FeatureRegistry(str(self._registry_path))
        
        # Initialize SQLite online store
        self._db_path = self._online_path / "online_store.db"
        self._init_online_store()
        
        # Stats
        self._stats = {
            "online_reads": 0,
            "online_writes": 0,
            "offline_reads": 0,
            "offline_writes": 0,
            "materializations": 0,
        }
    
    def _init_online_store(self) -> None:
        """Initialize SQLite database for online store."""
        with sqlite3.connect(str(self._db_path)) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS feature_values (
                    feature_view TEXT NOT NULL,
                    entity_key TEXT NOT NULL,
                    features TEXT NOT NULL,
                    event_timestamp TEXT NOT NULL,
                    created_timestamp TEXT NOT NULL,
                    PRIMARY KEY (feature_view, entity_key)
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_feature_view 
                ON feature_values(feature_view)
            """)
    
    def _make_entity_key(self, entity_dict: Dict[str, Any]) -> str:
        """Create a string key from entity dictionary."""
        # Sort keys for consistent ordering
        sorted_items = sorted(entity_dict.items())
        return json.dumps(sorted_items)
    
    def _parse_entity_key(self, key_str: str) -> Dict[str, Any]:
        """Parse entity key string back to dictionary."""
        items = json.loads(key_str)
        return dict(items)
    
    def register_feature_view(self, feature_view: FeatureView) -> None:
        """Register a feature view with the store."""
        self._registry.register_feature_view(feature_view)
        logger.info(f"Registered feature view: {feature_view.name}")
    
    def get_feature_view(self, name: str) -> Optional[FeatureView]:
        """Get a feature view by name."""
        return self._registry.get_feature_view(name)
    
    def list_feature_views(self) -> List[str]:
        """List all registered feature view names."""
        return self._registry.list_feature_views()
    
    def delete_feature_view(self, name: str) -> bool:
        """Delete a feature view."""
        if self._registry.delete_feature_view(name):
            # Clean up online store
            with sqlite3.connect(str(self._db_path)) as conn:
                conn.execute(
                    "DELETE FROM feature_values WHERE feature_view = ?",
                    (name,)
                )
            
            # Clean up offline store
            offline_file = self._offline_path / f"{name}.parquet"
            if offline_file.exists():
                offline_file.unlink()
            
            logger.info(f"Deleted feature view: {name}")
            return True
        return False
    
    def get_online_features(
        self,
        feature_refs: List[str],
        entity_keys: List[Dict[str, Any]],
    ) -> List[FeatureVector]:
        """Get feature values for online inference."""
        self._stats["online_reads"] += 1
        
        # Group features by view
        view_features: Dict[str, List[str]] = {}
        for ref in feature_refs:
            if ":" in ref:
                view_name, feature_name = ref.split(":", 1)
                if view_name not in view_features:
                    view_features[view_name] = []
                view_features[view_name].append(feature_name)
        
        results = []
        
        with sqlite3.connect(str(self._db_path)) as conn:
            for entity_key in entity_keys:
                entity_key_str = self._make_entity_key(entity_key)
                combined_features = {}
                feature_view_name = ""
                timestamp = datetime.utcnow()
                
                for view_name, feature_names in view_features.items():
                    feature_view_name = view_name
                    
                    cursor = conn.execute(
                        """
                        SELECT features, event_timestamp 
                        FROM feature_values 
                        WHERE feature_view = ? AND entity_key = ?
                        """,
                        (view_name, entity_key_str)
                    )
                    
                    row = cursor.fetchone()
                    
                    if row:
                        all_features = json.loads(row[0])
                        timestamp = datetime.fromisoformat(row[1])
                        
                        # Filter to requested features
                        for fname in feature_names:
                            if fname in all_features:
                                combined_features[fname] = all_features[fname]
                
                results.append(FeatureVector(
                    entity_key=entity_key,
                    features=combined_features,
                    feature_view=feature_view_name,
                    timestamp=timestamp,
                ))
        
        return results
    
    def get_historical_features(
        self,
        feature_refs: List[str],
        entity_df: pd.DataFrame,
        full_feature_names: bool = True,
    ) -> pd.DataFrame:
        """Get historical feature values for training."""
        self._stats["offline_reads"] += 1
        
        # Group features by view
        view_features: Dict[str, List[str]] = {}
        for ref in feature_refs:
            if ":" in ref:
                view_name, feature_name = ref.split(":", 1)
                if view_name not in view_features:
                    view_features[view_name] = []
                view_features[view_name].append(feature_name)
        
        result_df = entity_df.copy()
        
        for view_name, feature_names in view_features.items():
            # Load offline store for this view
            offline_file = self._offline_path / f"{view_name}.parquet"
            
            if not offline_file.exists():
                logger.warning(f"No offline data for view: {view_name}")
                continue
            
            view_df = pd.read_parquet(offline_file)
            
            # Get feature view to find join keys
            feature_view = self.get_feature_view(view_name)
            if not feature_view:
                continue
            
            join_keys = feature_view.join_keys
            
            # Select only needed columns
            columns_to_select = join_keys + feature_names
            if "event_timestamp" in view_df.columns:
                columns_to_select.append("event_timestamp")
            
            view_df = view_df[[c for c in columns_to_select if c in view_df.columns]]
            
            # Rename features if using full names
            if full_feature_names:
                rename_map = {
                    fname: f"{view_name}__{fname}"
                    for fname in feature_names
                }
                view_df = view_df.rename(columns=rename_map)
            
            # Join with entity_df
            result_df = result_df.merge(
                view_df,
                on=join_keys,
                how="left",
            )
        
        return result_df
    
    def materialize(
        self,
        feature_views: Optional[List[str]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, int]:
        """Materialize features to the online store."""
        self._stats["materializations"] += 1
        
        if feature_views is None:
            feature_views = self.list_feature_views()
        
        if end_date is None:
            end_date = datetime.utcnow()
        if start_date is None:
            start_date = end_date - timedelta(days=self.config.default_ttl_days)
        
        results = {}
        
        for view_name in feature_views:
            feature_view = self.get_feature_view(view_name)
            if not feature_view:
                continue
            
            # Load offline data
            offline_file = self._offline_path / f"{view_name}.parquet"
            
            if not offline_file.exists():
                results[view_name] = 0
                continue
            
            df = pd.read_parquet(offline_file)
            
            # Filter by date if timestamp column exists
            if "event_timestamp" in df.columns:
                df["event_timestamp"] = pd.to_datetime(df["event_timestamp"])
                df = df[
                    (df["event_timestamp"] >= start_date) &
                    (df["event_timestamp"] <= end_date)
                ]
            
            # Get latest values per entity
            join_keys = feature_view.join_keys
            
            if "event_timestamp" in df.columns:
                df = df.sort_values("event_timestamp").groupby(join_keys).last().reset_index()
            
            # Write to online store
            count = self._write_to_online(view_name, df, feature_view)
            results[view_name] = count
            
            logger.info(f"Materialized {count} rows for {view_name}")
        
        return results
    
    def push(
        self,
        feature_view: str,
        df: pd.DataFrame,
        to_online: bool = True,
        to_offline: bool = True,
    ) -> int:
        """Push feature values to the store."""
        view = self.get_feature_view(feature_view)
        if not view:
            raise ValueError(f"Feature view not found: {feature_view}")
        
        count = 0
        
        # Add timestamp if not present
        if "event_timestamp" not in df.columns:
            df = df.copy()
            df["event_timestamp"] = datetime.utcnow()
        
        # Push to offline store
        if to_offline:
            self._stats["offline_writes"] += 1
            offline_file = self._offline_path / f"{feature_view}.parquet"
            
            if offline_file.exists():
                existing_df = pd.read_parquet(offline_file)
                df = pd.concat([existing_df, df], ignore_index=True)
            
            df.to_parquet(offline_file, index=False)
            count = len(df)
        
        # Push to online store
        if to_online:
            self._stats["online_writes"] += 1
            count = self._write_to_online(feature_view, df, view)
        
        return count
    
    def _write_to_online(
        self,
        view_name: str,
        df: pd.DataFrame,
        feature_view: FeatureView,
    ) -> int:
        """Write data to online SQLite store."""
        join_keys = feature_view.join_keys
        feature_names = feature_view.feature_names
        
        now = datetime.utcnow().isoformat()
        count = 0
        
        with sqlite3.connect(str(self._db_path)) as conn:
            for _, row in df.iterrows():
                # Build entity key
                entity_key = {k: row[k] for k in join_keys if k in row}
                entity_key_str = self._make_entity_key(entity_key)
                
                # Build features dict
                features = {
                    f: row[f] for f in feature_names
                    if f in row and pd.notna(row[f])
                }
                
                # Convert numpy types to Python types
                features = {
                    k: (v.item() if hasattr(v, "item") else v)
                    for k, v in features.items()
                }
                
                # Get event timestamp
                event_ts = row.get("event_timestamp", datetime.utcnow())
                if hasattr(event_ts, "isoformat"):
                    event_ts = event_ts.isoformat()
                elif isinstance(event_ts, str):
                    pass
                else:
                    event_ts = str(event_ts)
                
                # Upsert into online store
                conn.execute(
                    """
                    INSERT OR REPLACE INTO feature_values
                    (feature_view, entity_key, features, event_timestamp, created_timestamp)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (view_name, entity_key_str, json.dumps(features), event_ts, now)
                )
                count += 1
        
        return count
    
    def get_stats(self) -> Dict[str, Any]:
        """Get feature store statistics."""
        # Count online store entries
        with sqlite3.connect(str(self._db_path)) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM feature_values")
            online_count = cursor.fetchone()[0]
        
        # Count offline files
        offline_files = list(self._offline_path.glob("*.parquet"))
        
        return {
            "backend": "local",
            "online_entries": online_count,
            "offline_files": len(offline_files),
            "feature_views": len(self.list_feature_views()),
            "operations": self._stats,
        }
    
    def cleanup_old_data(self, days: int = 30) -> Dict[str, int]:
        """
        Remove data older than specified days.
        
        Args:
            days: Remove data older than this many days
            
        Returns:
            Dict with cleanup statistics
        """
        cutoff = datetime.utcnow() - timedelta(days=days)
        cutoff_str = cutoff.isoformat()
        
        stats = {"online_deleted": 0, "offline_trimmed": 0}
        
        # Clean online store
        with sqlite3.connect(str(self._db_path)) as conn:
            cursor = conn.execute(
                "DELETE FROM feature_values WHERE event_timestamp < ?",
                (cutoff_str,)
            )
            stats["online_deleted"] = cursor.rowcount
        
        # Clean offline store
        for parquet_file in self._offline_path.glob("*.parquet"):
            try:
                df = pd.read_parquet(parquet_file)
                if "event_timestamp" in df.columns:
                    original_count = len(df)
                    df["event_timestamp"] = pd.to_datetime(df["event_timestamp"])
                    df = df[df["event_timestamp"] >= cutoff]
                    df.to_parquet(parquet_file, index=False)
                    stats["offline_trimmed"] += original_count - len(df)
            except Exception as e:
                logger.warning(f"Failed to clean {parquet_file}: {e}")
        
        return stats
