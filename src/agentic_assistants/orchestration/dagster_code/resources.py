"""
Dagster resource definitions for the Agentic Assistants framework.

Provides configured resources (database connections, MinIO storage,
Kubernetes client, LLM providers) that Dagster ops and assets can
depend on.
"""

import os
from typing import Any, Dict

from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)

try:
    import dagster as dg
    DAGSTER_AVAILABLE = True
except ImportError:
    DAGSTER_AVAILABLE = False
    dg = None  # type: ignore


if DAGSTER_AVAILABLE:

    class AgenticConfigResource(dg.ConfigurableResource):
        """Dagster resource that wraps AgenticConfig."""

        workspace_path: str = "."
        mlflow_enabled: bool = True
        telemetry_enabled: bool = False

        def get_config(self):
            """Return an AgenticConfig instance."""
            from agentic_assistants.config import AgenticConfig
            return AgenticConfig()

    class MinIOResource(dg.ConfigurableResource):
        """Dagster resource for MinIO/S3 object storage."""

        endpoint: str = "localhost:9000"
        access_key: str = "minioadmin"
        secret_key: str = "minioadmin"
        secure: bool = False

        def get_client(self):
            """Return a MinIOStorage client."""
            from agentic_assistants.kubernetes.storage import MinIOStorage
            return MinIOStorage(
                endpoint=self.endpoint,
                access_key=self.access_key,
                secret_key=self.secret_key,
                secure=self.secure,
            )

    class KubernetesResource(dg.ConfigurableResource):
        """Dagster resource for Kubernetes cluster access."""

        kubeconfig_path: str = ""
        namespace: str = "agentic"

        def get_client(self):
            """Return a KubernetesClient."""
            from agentic_assistants.kubernetes.client import KubernetesClient
            return KubernetesClient(namespace=self.namespace)

    class TelemetryResource(dg.ConfigurableResource):
        """Dagster resource wrapping TelemetryManager for OpenTelemetry integration."""

        enabled: bool = False
        service_name: str = "agentic-dagster"

        def get_telemetry(self):
            """Return a TelemetryManager instance, initialized if enabled."""
            from agentic_assistants.core.telemetry import TelemetryManager
            from agentic_assistants.config import AgenticConfig
            config = AgenticConfig()
            tm = TelemetryManager(config)
            if self.enabled:
                tm.initialize()
            return tm

        def get_dagster_telemetry(self):
            """Return a DagsterTelemetry instance for Dagster-specific tracing."""
            from agentic_assistants.orchestration.dagster_callbacks import DagsterTelemetry
            from agentic_assistants.config import AgenticConfig
            config = AgenticConfig()
            return DagsterTelemetry(config)


def get_default_resources() -> Dict[str, Any]:
    """
    Build the default resource dictionary for the Dagster Definitions.

    Reads configuration from environment variables where available.

    Returns:
        Dict mapping resource key -> resource instance
    """
    if not DAGSTER_AVAILABLE:
        return {}

    resources: Dict[str, Any] = {
        "agentic_config": AgenticConfigResource(
            workspace_path=os.getenv("AGENTIC_WORKSPACE", "."),
            mlflow_enabled=os.getenv("MLFLOW_ENABLED", "true").lower() == "true",
            telemetry_enabled=os.getenv("OTEL_ENABLED", "false").lower() == "true",
        ),
    }

    # MinIO / S3 resource (if endpoint is configured)
    minio_endpoint = os.getenv("MINIO_ENDPOINT", "")
    if minio_endpoint:
        resources["minio"] = MinIOResource(
            endpoint=minio_endpoint,
            access_key=os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
            secret_key=os.getenv("MINIO_SECRET_KEY", "minioadmin"),
            secure=os.getenv("MINIO_SECURE", "false").lower() == "true",
        )

    # Kubernetes resource (if running in-cluster or kubeconfig is available)
    kubeconfig = os.getenv("KUBECONFIG", "")
    k8s_namespace = os.getenv("K8S_NAMESPACE", "agentic")
    resources["kubernetes"] = KubernetesResource(
        kubeconfig_path=kubeconfig,
        namespace=k8s_namespace,
    )

    # OpenTelemetry resource
    resources["telemetry"] = TelemetryResource(
        enabled=os.getenv("OTEL_ENABLED", "false").lower() == "true",
        service_name=os.getenv("OTEL_SERVICE_NAME", "agentic-dagster"),
    )

    return resources
