"""
Apache Iceberg integration via DataHub's built-in Iceberg Catalog.

Uses PyIceberg to interact with Iceberg tables stored in MinIO,
with DataHub GMS serving as the REST catalog endpoint.
"""

from typing import Any, Dict, List, Optional

from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


class IcebergClient:
    """
    Client for interacting with Iceberg tables through DataHub's REST catalog.

    Wraps PyIceberg's catalog API with connection defaults sourced from
    AgenticConfig.  Falls back gracefully when pyiceberg is not installed.
    """

    def __init__(
        self,
        catalog_uri: str = "http://localhost:8080/iceberg",
        warehouse: str = "s3://iceberg-warehouse/",
        s3_endpoint: str = "http://localhost:9000",
        s3_access_key: str = "minioadmin",
        s3_secret_key: str = "minioadmin123",
        catalog_name: str = "datahub",
    ):
        self.catalog_uri = catalog_uri
        self.warehouse = warehouse
        self.s3_endpoint = s3_endpoint
        self.s3_access_key = s3_access_key
        self.s3_secret_key = s3_secret_key
        self.catalog_name = catalog_name
        self._catalog = None

    @property
    def catalog(self):
        if self._catalog is None:
            try:
                from pyiceberg.catalog import load_catalog

                self._catalog = load_catalog(
                    self.catalog_name,
                    **{
                        "type": "rest",
                        "uri": self.catalog_uri,
                        "warehouse": self.warehouse,
                        "s3.endpoint": self.s3_endpoint,
                        "s3.access-key-id": self.s3_access_key,
                        "s3.secret-access-key": self.s3_secret_key,
                        "s3.path-style-access": "true",
                        "s3.region": "us-east-1",
                    },
                )
            except ImportError:
                raise RuntimeError(
                    "pyiceberg is required: pip install 'pyiceberg[s3]'"
                )
        return self._catalog

    # -- Namespace operations --------------------------------------------------

    def list_namespaces(self) -> List[str]:
        return [".".join(ns) for ns in self.catalog.list_namespaces()]

    def create_namespace(self, namespace: str, properties: Optional[Dict[str, str]] = None):
        self.catalog.create_namespace(namespace, properties or {})

    # -- Table operations ------------------------------------------------------

    def list_tables(self, namespace: str = "default") -> List[str]:
        return [
            f"{ident[0]}.{ident[1]}" if len(ident) > 1 else str(ident[0])
            for ident in self.catalog.list_tables(namespace)
        ]

    def load_table(self, namespace: str, table: str) -> Any:
        return self.catalog.load_table(f"{namespace}.{table}")

    def create_table(
        self,
        namespace: str,
        table: str,
        schema_fields: List[Dict[str, Any]],
    ) -> Any:
        """Create an Iceberg table from a list of field definitions."""
        from pyiceberg.schema import Schema
        from pyiceberg.types import (
            BooleanType,
            DoubleType,
            FloatType,
            IntegerType,
            LongType,
            NestedField,
            StringType,
            TimestampType,
        )

        _type_map = {
            "string": StringType(),
            "long": LongType(),
            "int": IntegerType(),
            "integer": IntegerType(),
            "float": FloatType(),
            "double": DoubleType(),
            "boolean": BooleanType(),
            "timestamp": TimestampType(),
        }

        fields = []
        for idx, f in enumerate(schema_fields, start=1):
            iceberg_type = _type_map.get(f.get("type", "string").lower(), StringType())
            fields.append(
                NestedField(
                    field_id=idx,
                    name=f["name"],
                    field_type=iceberg_type,
                    required=f.get("required", False),
                )
            )

        schema = Schema(*fields)
        return self.catalog.create_table(f"{namespace}.{table}", schema=schema)

    def get_table_schema(self, namespace: str, table: str) -> List[Dict[str, Any]]:
        tbl = self.load_table(namespace, table)
        return [
            {
                "field_id": field.field_id,
                "name": field.name,
                "type": str(field.field_type),
                "required": field.required,
            }
            for field in tbl.schema().fields
        ]

    def get_snapshots(self, namespace: str, table: str) -> List[Dict[str, Any]]:
        tbl = self.load_table(namespace, table)
        return [
            {
                "snapshot_id": snap.snapshot_id,
                "timestamp_ms": snap.timestamp_ms,
                "manifest_list": snap.manifest_list,
            }
            for snap in tbl.metadata.snapshots
        ]

    def preview_table(
        self, namespace: str, table: str, limit: int = 50
    ) -> Dict[str, Any]:
        """Read a sample of rows via PyArrow and return as column-oriented dict."""
        tbl = self.load_table(namespace, table)
        scan = tbl.scan(limit=limit)
        arrow_table = scan.to_arrow()
        return {
            "columns": arrow_table.column_names,
            "rows": arrow_table.to_pydict(),
            "total_rows": arrow_table.num_rows,
        }

    def table_metadata(self, namespace: str, table: str) -> Dict[str, Any]:
        tbl = self.load_table(namespace, table)
        meta = tbl.metadata
        return {
            "table_uuid": str(meta.table_uuid),
            "location": meta.location,
            "format_version": meta.format_version,
            "schema": self.get_table_schema(namespace, table),
            "snapshot_count": len(meta.snapshots),
            "partition_specs": [
                {"spec_id": spec.spec_id, "fields": len(spec.fields)}
                for spec in meta.partition_specs
            ],
            "properties": dict(meta.properties),
        }


def get_iceberg_client(config=None) -> IcebergClient:
    """Factory that builds an IcebergClient from AgenticConfig."""
    if config is None:
        from agentic_assistants.config import AgenticConfig
        config = AgenticConfig()

    iceberg_cfg = getattr(config, "iceberg", None)
    if iceberg_cfg is not None:
        return IcebergClient(
            catalog_uri=iceberg_cfg.catalog_uri,
            warehouse=iceberg_cfg.warehouse,
            s3_endpoint=iceberg_cfg.s3_endpoint,
            s3_access_key=iceberg_cfg.s3_access_key,
            s3_secret_key=iceberg_cfg.s3_secret_key,
        )
    return IcebergClient()
