"""
DataHub integration for metadata catalog, search, and lineage.

Wraps the DataHub Python SDK (acryl-datahub) to provide search,
dataset browsing, lineage traversal, and metadata emission.
"""

from typing import Any, Dict, List, Optional

import httpx

from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


class DataHubClient:
    """
    Lightweight client for DataHub GMS REST and GraphQL APIs.

    Uses httpx for HTTP calls so the heavy ``datahub`` SDK is optional.
    When the SDK *is* installed, ``get_graph()`` returns the richer
    ``DatahubGraph`` object for programmatic metadata emission.
    """

    def __init__(
        self,
        gms_url: str = "http://localhost:8080",
        token: Optional[str] = None,
        timeout: float = 30.0,
    ):
        self.gms_url = gms_url.rstrip("/")
        self.token = token
        self.timeout = timeout

    def _headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    # -- SDK bridge (optional) -------------------------------------------------

    def get_graph(self):
        """Return a ``datahub.ingestion.graph.client.DatahubGraph`` instance."""
        from datahub.ingestion.graph.client import DatahubGraph, DatahubClientConfig

        return DatahubGraph(
            DatahubClientConfig(server=self.gms_url, token=self.token)
        )

    # -- Search ----------------------------------------------------------------

    async def search(
        self,
        query: str,
        entity_type: str = "dataset",
        start: int = 0,
        count: int = 20,
        filters: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "input": query,
            "entity": entity_type,
            "start": start,
            "count": count,
        }
        if filters:
            payload["filter"] = {
                "or": [
                    {"and": [{"field": k, "value": v} for k, v in filters.items()]}
                ]
            }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(
                f"{self.gms_url}/entities?action=search",
                json=payload,
                headers=self._headers(),
            )
            resp.raise_for_status()
            return resp.json()

    # -- Entity CRUD -----------------------------------------------------------

    async def get_dataset(self, urn: str) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(
                f"{self.gms_url}/entities/{urn}",
                headers=self._headers(),
            )
            resp.raise_for_status()
            return resp.json()

    async def list_datasets(
        self,
        start: int = 0,
        count: int = 50,
        platform: Optional[str] = None,
    ) -> Dict[str, Any]:
        query = "*"
        filters = {}
        if platform:
            filters["platform"] = f"urn:li:dataPlatform:{platform}"
        return await self.search(query, entity_type="dataset", start=start, count=count, filters=filters or None)

    # -- Lineage ---------------------------------------------------------------

    async def get_lineage(
        self,
        urn: str,
        direction: str = "DOWNSTREAM",
        max_hops: int = 3,
    ) -> Dict[str, Any]:
        params = {
            "urn": urn,
            "direction": direction,
            "maxHops": str(max_hops),
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(
                f"{self.gms_url}/relationships",
                params=params,
                headers=self._headers(),
            )
            resp.raise_for_status()
            return resp.json()

    # -- Domains / Glossary ----------------------------------------------------

    async def list_domains(self) -> Dict[str, Any]:
        return await self.search("*", entity_type="domain", count=100)

    async def list_glossary_terms(self) -> Dict[str, Any]:
        return await self.search("*", entity_type="glossaryTerm", count=100)

    # -- Ingestion -------------------------------------------------------------

    async def run_ingestion(self, recipe: Dict[str, Any]) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(
                f"{self.gms_url}/runs?action=ingest",
                json=recipe,
                headers=self._headers(),
            )
            resp.raise_for_status()
            return resp.json()

    # -- Health ----------------------------------------------------------------

    async def health(self) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(f"{self.gms_url}/config", headers=self._headers())
            resp.raise_for_status()
            return resp.json()

    # -- Statistics ------------------------------------------------------------

    async def get_stats(self) -> Dict[str, Any]:
        """Aggregate catalog statistics from search counts."""
        datasets = await self.search("*", entity_type="dataset", count=0)
        dashboards = await self.search("*", entity_type="dashboard", count=0)
        pipelines = await self.search("*", entity_type="dataFlow", count=0)

        def _total(resp):
            return resp.get("value", {}).get("numEntities", 0)

        return {
            "datasets": _total(datasets),
            "dashboards": _total(dashboards),
            "pipelines": _total(pipelines),
        }


    # -- Registration: Knowledge Bases & Document Stores -------------------------

    async def register_knowledge_base(
        self,
        name: str,
        description: str = "",
        platform: str = "vectordb",
        tags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Register a knowledge base as a DataHub dataset entity."""
        urn = f"urn:li:dataset:(urn:li:dataPlatform:{platform},{name},PROD)"
        payload = {
            "entity": {
                "value": {
                    "com.linkedin.metadata.snapshot.DatasetSnapshot": {
                        "urn": urn,
                        "aspects": [
                            {
                                "com.linkedin.dataset.DatasetProperties": {
                                    "name": name,
                                    "description": description or f"Knowledge base: {name}",
                                    "customProperties": {
                                        "resource_type": "knowledge_base",
                                        "tags": ",".join(tags or []),
                                    },
                                }
                            }
                        ],
                    }
                }
            }
        }
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(
                    f"{self.gms_url}/entities?action=ingest",
                    headers=self._headers(),
                    json=payload,
                )
                resp.raise_for_status()
                return {"urn": urn, "status": "registered"}
        except Exception as e:
            logger.warning(f"Failed to register KB in DataHub: {e}")
            return {"urn": urn, "status": "registered_locally", "error": str(e)}

    async def register_document_store(
        self,
        store_id: str,
        name: str,
        description: str = "",
        platform: str = "vectordb",
        ttl_hours: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Register a document store as a DataHub dataset entity."""
        urn = f"urn:li:dataset:(urn:li:dataPlatform:{platform},docstore-{name},PROD)"
        payload = {
            "entity": {
                "value": {
                    "com.linkedin.metadata.snapshot.DatasetSnapshot": {
                        "urn": urn,
                        "aspects": [
                            {
                                "com.linkedin.dataset.DatasetProperties": {
                                    "name": f"docstore-{name}",
                                    "description": description or f"Document store: {name}",
                                    "customProperties": {
                                        "resource_type": "document_store",
                                        "store_id": store_id,
                                        "ttl_hours": str(ttl_hours) if ttl_hours else "none",
                                        "ephemeral": "true",
                                    },
                                }
                            }
                        ],
                    }
                }
            }
        }
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(
                    f"{self.gms_url}/entities?action=ingest",
                    headers=self._headers(),
                    json=payload,
                )
                resp.raise_for_status()
                return {"urn": urn, "status": "registered"}
        except Exception as e:
            logger.warning(f"Failed to register DocStore in DataHub: {e}")
            return {"urn": urn, "status": "registered_locally", "error": str(e)}

    async def update_lineage(
        self,
        upstream_urn: str,
        downstream_urn: str,
    ) -> Dict[str, Any]:
        """Record lineage between two DataHub entities."""
        payload = {
            "entity": {
                "value": {
                    "com.linkedin.metadata.snapshot.DatasetSnapshot": {
                        "urn": downstream_urn,
                        "aspects": [
                            {
                                "com.linkedin.dataset.UpstreamLineage": {
                                    "upstreams": [
                                        {
                                            "dataset": upstream_urn,
                                            "type": "TRANSFORMED",
                                        }
                                    ]
                                }
                            }
                        ],
                    }
                }
            }
        }
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(
                    f"{self.gms_url}/entities?action=ingest",
                    headers=self._headers(),
                    json=payload,
                )
                resp.raise_for_status()
                return {"status": "lineage_recorded"}
        except Exception as e:
            logger.warning(f"Failed to update lineage in DataHub: {e}")
            return {"status": "error", "error": str(e)}


def get_datahub_client(config=None) -> DataHubClient:
    """Factory that builds a DataHubClient from AgenticConfig."""
    if config is None:
        from agentic_assistants.config import AgenticConfig
        config = AgenticConfig()

    dh_cfg = getattr(config, "datahub", None)
    if dh_cfg is not None:
        return DataHubClient(
            gms_url=dh_cfg.gms_url,
            token=dh_cfg.token or None,
        )
    return DataHubClient()
