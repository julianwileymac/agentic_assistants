"""
Trace storage, export, and import for offline / multi-tier observability.

Provides:
- FileSpanExporter: OpenTelemetry SpanExporter that writes OTLP JSON files
- TraceStore: utilities to export, import, and sync trace files to live
  OTLP collectors (Kubernetes, Docker, or standalone)

The canonical interchange format is **OTLP JSON** -- the JSON representation of
``ExportTraceServiceRequest`` protobuf messages.  Every OTLP-compatible backend
(Jaeger, Grafana Tempo, Datadog, etc.) can ingest this format directly.
"""

from __future__ import annotations

import json
import shutil
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# OTLP JSON serialisation helpers
# ---------------------------------------------------------------------------

def _span_to_otlp_dict(span) -> Dict[str, Any]:
    """Convert an OpenTelemetry ReadableSpan to an OTLP-JSON-compatible dict."""
    ctx = span.context
    parent_id = (
        format(span.parent.span_id, "016x") if span.parent else ""
    )

    def _encode_attributes(attrs) -> List[Dict[str, Any]]:
        if not attrs:
            return []
        out: list[dict] = []
        for k, v in attrs.items():
            if isinstance(v, bool):
                out.append({"key": k, "value": {"boolValue": v}})
            elif isinstance(v, int):
                out.append({"key": k, "value": {"intValue": str(v)}})
            elif isinstance(v, float):
                out.append({"key": k, "value": {"doubleValue": v}})
            else:
                out.append({"key": k, "value": {"stringValue": str(v)}})
        return out

    def _encode_events(events) -> List[Dict[str, Any]]:
        if not events:
            return []
        return [
            {
                "timeUnixNano": str(ev.timestamp),
                "name": ev.name,
                "attributes": _encode_attributes(ev.attributes),
            }
            for ev in events
        ]

    kind_map = {None: 0, 0: 0, 1: 1, 2: 2, 3: 3, 4: 4}
    raw_kind = getattr(span, "kind", None)
    if raw_kind is not None and hasattr(raw_kind, "value"):
        raw_kind = raw_kind.value
    span_kind = kind_map.get(raw_kind, 1)

    status = getattr(span, "status", None)
    status_dict: Dict[str, Any] = {}
    if status is not None:
        code = getattr(status, "status_code", None)
        if code is not None:
            status_dict["code"] = getattr(code, "value", int(code))
        desc = getattr(status, "description", None)
        if desc:
            status_dict["message"] = desc

    return {
        "traceId": format(ctx.trace_id, "032x"),
        "spanId": format(ctx.span_id, "016x"),
        "parentSpanId": parent_id,
        "name": span.name,
        "kind": span_kind,
        "startTimeUnixNano": str(span.start_time),
        "endTimeUnixNano": str(span.end_time),
        "attributes": _encode_attributes(span.attributes),
        "events": _encode_events(span.events),
        "status": status_dict,
    }


def _spans_to_otlp_json(spans: Sequence) -> Dict[str, Any]:
    """
    Build a full ``ExportTraceServiceRequest`` JSON structure from a batch of
    ReadableSpan objects, grouped by resource and instrumentation scope.
    """
    resource_map: Dict[int, Dict[str, Any]] = {}

    for span in spans:
        res = span.resource
        res_id = id(res)

        if res_id not in resource_map:
            res_attrs = []
            if res and res.attributes:
                for k, v in res.attributes.items():
                    res_attrs.append({"key": k, "value": {"stringValue": str(v)}})
            resource_map[res_id] = {
                "resource": {"attributes": res_attrs},
                "scopeSpans": {},
            }

        scope = span.instrumentation_scope
        scope_name = scope.name if scope else ""
        scope_key = scope_name

        rs = resource_map[res_id]
        if scope_key not in rs["scopeSpans"]:
            rs["scopeSpans"][scope_key] = {
                "scope": {"name": scope_name},
                "spans": [],
            }

        rs["scopeSpans"][scope_key]["spans"].append(_span_to_otlp_dict(span))

    resource_spans = []
    for rs in resource_map.values():
        resource_spans.append({
            "resource": rs["resource"],
            "scopeSpans": list(rs["scopeSpans"].values()),
        })

    return {"resourceSpans": resource_spans}


# ---------------------------------------------------------------------------
# FileSpanExporter  (OpenTelemetry SDK SpanExporter implementation)
# ---------------------------------------------------------------------------

class FileSpanExporter:
    """
    SpanExporter that writes batches as OTLP JSON files.

    Each ``export()`` call produces one ``.json`` file in *export_dir*,
    timestamped to avoid collisions.  These files can later be replayed
    into a live OTLP collector via :class:`TraceStore`.

    Implements the ``opentelemetry.sdk.trace.export.SpanExporter`` protocol
    without inheriting from the ABC so the module stays importable even when
    OTel SDK extras are missing.
    """

    def __init__(self, export_dir: Path | str):
        self._dir = Path(export_dir)
        self._dir.mkdir(parents=True, exist_ok=True)
        self._seq = 0

    def export(self, spans: Sequence) -> int:
        """
        Write spans as an OTLP JSON file.

        Returns:
            0 (SUCCESS) on disk write, 1 (FAILURE) otherwise.
        """
        try:
            payload = _spans_to_otlp_json(spans)
            ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%f")
            self._seq += 1
            filename = self._dir / f"traces_{ts}_{self._seq:04d}.json"
            filename.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            logger.debug("Wrote %d spans to %s", len(spans), filename)
            return 0  # SUCCESS
        except Exception as exc:
            logger.warning("FileSpanExporter failed: %s", exc)
            return 1  # FAILURE

    def shutdown(self) -> None:
        pass

    def force_flush(self, timeout_millis: int = 30_000) -> bool:
        return True


# ---------------------------------------------------------------------------
# TraceStore  (export / import / sync)
# ---------------------------------------------------------------------------

class TraceStore:
    """
    Manage file-based trace storage and synchronisation with OTLP collectors.

    Workflow
    --------
    1. During normal operation *FileSpanExporter* writes OTLP JSON into the
       ``store_dir``.
    2. ``export_to_file(dest)`` copies / archives those files for backup.
    3. ``import_from_file(src, endpoint)`` reads files and POSTs them to an
       OTLP HTTP endpoint (``/v1/traces``).
    4. ``sync_to_collector(endpoint)`` is a convenience that imports **and**
       deletes successfully synced files.
    """

    def __init__(self, store_dir: Path | str = "data/traces"):
        self.store_dir = Path(store_dir)
        self.store_dir.mkdir(parents=True, exist_ok=True)

    # -- list / count --------------------------------------------------------

    def pending_files(self) -> List[Path]:
        """Return all ``.json`` trace files sorted oldest-first."""
        return sorted(self.store_dir.glob("traces_*.json"))

    def pending_count(self) -> int:
        return len(self.pending_files())

    # -- export (copy to backup) --------------------------------------------

    def export_to_file(self, dest: Path | str) -> int:
        """
        Copy all pending trace files to *dest* directory.

        Returns:
            Number of files copied.
        """
        dest = Path(dest)
        dest.mkdir(parents=True, exist_ok=True)
        files = self.pending_files()
        for f in files:
            shutil.copy2(f, dest / f.name)
        logger.info("Exported %d trace files to %s", len(files), dest)
        return len(files)

    # -- import (send to OTLP collector) ------------------------------------

    @staticmethod
    def _post_otlp_json(endpoint: str, payload: Dict[str, Any]) -> bool:
        """POST an OTLP JSON payload to an HTTP endpoint's /v1/traces path."""
        import urllib.request
        import urllib.error

        url = endpoint.rstrip("/")
        if not url.endswith("/v1/traces"):
            url = url + "/v1/traces"

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                return resp.status < 300
        except urllib.error.URLError as exc:
            logger.warning("OTLP POST to %s failed: %s", url, exc)
            return False

    def import_from_file(
        self,
        source: Path | str,
        endpoint: str,
        delete_on_success: bool = False,
    ) -> int:
        """
        Read OTLP JSON files from *source* and POST them to *endpoint*.

        Args:
            source: Directory containing ``traces_*.json`` files.
            endpoint: OTLP HTTP endpoint (e.g. ``http://localhost:4318``).
            delete_on_success: Remove files after successful upload.

        Returns:
            Number of files successfully imported.
        """
        source = Path(source)
        files = sorted(source.glob("traces_*.json"))
        ok = 0
        for f in files:
            try:
                payload = json.loads(f.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError) as exc:
                logger.warning("Skipping invalid trace file %s: %s", f, exc)
                continue

            if self._post_otlp_json(endpoint, payload):
                ok += 1
                if delete_on_success:
                    f.unlink(missing_ok=True)

        logger.info("Imported %d / %d trace files to %s", ok, len(files), endpoint)
        return ok

    def sync_to_collector(self, endpoint: str) -> int:
        """
        Sync all pending file-stored traces to a live OTLP collector,
        removing files on successful delivery.

        Args:
            endpoint: OTLP HTTP endpoint (e.g. ``http://localhost:4318``).

        Returns:
            Number of files synced.
        """
        return self.import_from_file(
            source=self.store_dir,
            endpoint=endpoint,
            delete_on_success=True,
        )
