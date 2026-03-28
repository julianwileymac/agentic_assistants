"""
Evaluation metrics and reliability analysis for agentic systems.

Provides standard metric accumulators, an EvaluationMixin for base classes,
and a GoldenDataset loader for reference-based evaluation aligned with
the RAGAS and multi-level evaluation strategies.

Usage:
    >>> tracker = MetricTracker()
    >>> tracker.record("task_success", 1.0)
    >>> tracker.record("task_success", 0.0)
    >>> tracker.summary()["task_success"]["mean"]
    0.5
"""

from __future__ import annotations

import json
import math
import statistics
import time
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Literal, Optional, Sequence

from pydantic import Field

from agentic_assistants.core.base_models import AgenticBaseModel


class MetricValue(AgenticBaseModel):
    """Summary statistics for a single named metric."""

    name: str
    count: int = 0
    total: float = 0.0
    mean: float = 0.0
    min: float = float("inf")
    max: float = float("-inf")
    stddev: Optional[float] = None
    values: list[float] = Field(default_factory=list)


class MetricTracker:
    """Accumulates metric observations and computes summary statistics."""

    def __init__(self, keep_values: bool = True) -> None:
        self._data: dict[str, list[float]] = {}
        self._keep_values = keep_values

    def record(self, name: str, value: float) -> None:
        self._data.setdefault(name, []).append(value)

    def record_many(self, metrics: dict[str, float]) -> None:
        for name, value in metrics.items():
            self.record(name, value)

    def get(self, name: str) -> MetricValue:
        values = self._data.get(name, [])
        if not values:
            return MetricValue(name=name)
        return MetricValue(
            name=name,
            count=len(values),
            total=sum(values),
            mean=statistics.mean(values),
            min=min(values),
            max=max(values),
            stddev=statistics.stdev(values) if len(values) > 1 else None,
            values=values if self._keep_values else [],
        )

    def summary(self) -> dict[str, dict[str, Any]]:
        return {name: self.get(name).to_dict(exclude={"values"}) for name in self._data}

    def reset(self) -> None:
        self._data.clear()


# ---------------------------------------------------------------------------
# Core metric accumulators
# ---------------------------------------------------------------------------


class TaskSuccessRate(AgenticBaseModel):
    """Fraction of episodes where the agent completed its objective."""

    successes: int = 0
    failures: int = 0

    @property
    def total(self) -> int:
        return self.successes + self.failures

    @property
    def rate(self) -> float:
        return self.successes / self.total if self.total > 0 else 0.0

    def record(self, success: bool) -> None:
        if success:
            self.successes += 1
        else:
            self.failures += 1


class LatencyMetric(AgenticBaseModel):
    """Tracks operation latencies in milliseconds."""

    observations: list[float] = Field(default_factory=list)

    def record(self, start_time: float) -> float:
        elapsed = (time.perf_counter() - start_time) * 1000
        self.observations.append(elapsed)
        return elapsed

    def record_value(self, ms: float) -> None:
        self.observations.append(ms)

    @property
    def p50(self) -> float:
        return self._percentile(50)

    @property
    def p95(self) -> float:
        return self._percentile(95)

    @property
    def p99(self) -> float:
        return self._percentile(99)

    @property
    def mean(self) -> float:
        return statistics.mean(self.observations) if self.observations else 0.0

    def _percentile(self, pct: int) -> float:
        if not self.observations:
            return 0.0
        s = sorted(self.observations)
        k = (len(s) - 1) * pct / 100
        f = math.floor(k)
        c = math.ceil(k)
        if f == c:
            return s[int(k)]
        return s[f] * (c - k) + s[c] * (k - f)


class HallucinationRate(AgenticBaseModel):
    """Tracks grounded vs. ungrounded responses."""

    grounded: int = 0
    hallucinated: int = 0

    @property
    def total(self) -> int:
        return self.grounded + self.hallucinated

    @property
    def rate(self) -> float:
        return self.hallucinated / self.total if self.total > 0 else 0.0

    def record(self, is_grounded: bool) -> None:
        if is_grounded:
            self.grounded += 1
        else:
            self.hallucinated += 1


class HandoffEfficiency(AgenticBaseModel):
    """Measures inter-agent handoff quality."""

    total_handoffs: int = 0
    successful_handoffs: int = 0
    oscillations: int = 0
    deadlocks: int = 0

    @property
    def success_rate(self) -> float:
        return self.successful_handoffs / self.total_handoffs if self.total_handoffs > 0 else 0.0

    @property
    def oscillation_rate(self) -> float:
        return self.oscillations / self.total_handoffs if self.total_handoffs > 0 else 0.0

    def record_handoff(self, success: bool) -> None:
        self.total_handoffs += 1
        if success:
            self.successful_handoffs += 1

    def record_oscillation(self) -> None:
        self.oscillations += 1

    def record_deadlock(self) -> None:
        self.deadlocks += 1


# ---------------------------------------------------------------------------
# RAGAS-inspired context / answer metrics (rule-based, no LLM required)
# ---------------------------------------------------------------------------


class ContextRelevance(AgenticBaseModel):
    """Token-overlap proxy for RAGAS context_relevance.

    Measures what fraction of query tokens appear in the retrieved context.
    """

    scores: list[float] = Field(default_factory=list)

    def record(self, query: str, context: str) -> float:
        q_tokens = set(query.lower().split())
        c_tokens = set(context.lower().split())
        if not q_tokens:
            self.scores.append(0.0)
            return 0.0
        overlap = len(q_tokens & c_tokens) / len(q_tokens)
        self.scores.append(overlap)
        return overlap

    @property
    def mean(self) -> float:
        return statistics.mean(self.scores) if self.scores else 0.0


class ContextSufficiency(AgenticBaseModel):
    """Checks whether required answer tokens are present in the context."""

    scores: list[float] = Field(default_factory=list)

    def record(self, answer: str, context: str) -> float:
        a_tokens = set(answer.lower().split())
        c_tokens = set(context.lower().split())
        if not a_tokens:
            self.scores.append(0.0)
            return 0.0
        coverage = len(a_tokens & c_tokens) / len(a_tokens)
        self.scores.append(coverage)
        return coverage

    @property
    def mean(self) -> float:
        return statistics.mean(self.scores) if self.scores else 0.0


class AnswerRelevance(AgenticBaseModel):
    """Token-overlap proxy for answer relevance to the original query."""

    scores: list[float] = Field(default_factory=list)

    def record(self, query: str, answer: str) -> float:
        q_tokens = set(query.lower().split())
        a_tokens = set(answer.lower().split())
        if not q_tokens or not a_tokens:
            self.scores.append(0.0)
            return 0.0
        overlap = len(q_tokens & a_tokens) / len(q_tokens)
        self.scores.append(overlap)
        return overlap

    @property
    def mean(self) -> float:
        return statistics.mean(self.scores) if self.scores else 0.0


# ---------------------------------------------------------------------------
# Multi-agent coordination metrics
# ---------------------------------------------------------------------------


class CommunicationEfficiency(AgenticBaseModel):
    """Tracks volume and usefulness of inter-agent messages."""

    total_messages: int = 0
    useful_messages: int = 0
    total_tokens: int = 0

    def record_message(self, useful: bool, token_count: int = 0) -> None:
        self.total_messages += 1
        self.total_tokens += token_count
        if useful:
            self.useful_messages += 1

    @property
    def usefulness_rate(self) -> float:
        return self.useful_messages / self.total_messages if self.total_messages > 0 else 0.0

    @property
    def avg_tokens_per_message(self) -> float:
        return self.total_tokens / self.total_messages if self.total_messages > 0 else 0.0


class ResourceFootprint(AgenticBaseModel):
    """Tracks computational and monetary cost per task resolution."""

    total_tokens_used: int = 0
    total_api_calls: int = 0
    total_cost_usd: float = 0.0
    successful_resolutions: int = 0

    def record_call(self, tokens: int = 0, cost_usd: float = 0.0) -> None:
        self.total_api_calls += 1
        self.total_tokens_used += tokens
        self.total_cost_usd += cost_usd

    def record_resolution(self) -> None:
        self.successful_resolutions += 1

    @property
    def cost_per_resolution(self) -> float:
        if self.successful_resolutions == 0:
            return 0.0
        return self.total_cost_usd / self.successful_resolutions

    @property
    def tokens_per_resolution(self) -> float:
        if self.successful_resolutions == 0:
            return 0.0
        return self.total_tokens_used / self.successful_resolutions


# ---------------------------------------------------------------------------
# Evaluation aggregation
# ---------------------------------------------------------------------------


class EvaluationResult(AgenticBaseModel):
    """Aggregated evaluation report."""

    task_success: Optional[TaskSuccessRate] = None
    latency: Optional[LatencyMetric] = None
    hallucination: Optional[HallucinationRate] = None
    handoff: Optional[HandoffEfficiency] = None
    context_relevance: Optional[ContextRelevance] = None
    context_sufficiency: Optional[ContextSufficiency] = None
    answer_relevance: Optional[AnswerRelevance] = None
    communication: Optional[CommunicationEfficiency] = None
    resource_footprint: Optional[ResourceFootprint] = None
    custom_metrics: dict[str, Any] = Field(default_factory=dict)

    def summary(self) -> dict[str, Any]:
        out: dict[str, Any] = {}
        if self.task_success:
            out["task_success_rate"] = self.task_success.rate
        if self.latency:
            out["latency_p50_ms"] = self.latency.p50
            out["latency_p95_ms"] = self.latency.p95
        if self.hallucination:
            out["hallucination_rate"] = self.hallucination.rate
        if self.handoff:
            out["handoff_success_rate"] = self.handoff.success_rate
            out["oscillations"] = self.handoff.oscillations
            out["deadlocks"] = self.handoff.deadlocks
        if self.context_relevance:
            out["context_relevance_mean"] = self.context_relevance.mean
        if self.context_sufficiency:
            out["context_sufficiency_mean"] = self.context_sufficiency.mean
        if self.answer_relevance:
            out["answer_relevance_mean"] = self.answer_relevance.mean
        if self.communication:
            out["communication_usefulness"] = self.communication.usefulness_rate
        if self.resource_footprint:
            out["cost_per_resolution_usd"] = self.resource_footprint.cost_per_resolution
            out["tokens_per_resolution"] = self.resource_footprint.tokens_per_resolution
        out.update(self.custom_metrics)
        return out


class EvaluationMixin:
    """Mixin that adds ``compute_reliability_metrics`` to any class.

    Subclasses should override ``_collect_eval_data`` to supply raw observations.
    Expected keys from ``_collect_eval_data()``:
      - ``successes``: list[bool]
      - ``latencies``: list[float]  (milliseconds)
      - ``groundedness``: list[bool]
      - ``handoffs``: list[bool]  (success flags)
      - ``oscillations``: int
      - ``deadlocks``: int
      - ``context_pairs``: list[dict] with keys ``query``, ``context``
      - ``sufficiency_pairs``: list[dict] with keys ``answer``, ``context``
      - ``answer_pairs``: list[dict] with keys ``query``, ``answer``
      - ``messages``: list[dict] with keys ``useful`` (bool), ``tokens`` (int)
      - ``api_calls``: list[dict] with keys ``tokens``, ``cost_usd``
      - ``resolutions``: int
      - Any other keys are passed through as ``custom_metrics``.
    """

    _KNOWN_KEYS = frozenset({
        "successes", "latencies", "groundedness",
        "handoffs", "oscillations", "deadlocks",
        "context_pairs", "sufficiency_pairs", "answer_pairs",
        "messages", "api_calls", "resolutions",
    })

    def _collect_eval_data(self) -> dict[str, Any]:
        return {}

    def compute_reliability_metrics(self) -> EvaluationResult:
        data = self._collect_eval_data()
        result = EvaluationResult()

        successes = data.get("successes", [])
        if successes:
            result.task_success = TaskSuccessRate()
            for s in successes:
                result.task_success.record(s)

        latencies = data.get("latencies", [])
        if latencies:
            result.latency = LatencyMetric(observations=latencies)

        groundedness = data.get("groundedness", [])
        if groundedness:
            result.hallucination = HallucinationRate()
            for g in groundedness:
                result.hallucination.record(g)

        handoffs = data.get("handoffs", [])
        if handoffs or data.get("oscillations") or data.get("deadlocks"):
            result.handoff = HandoffEfficiency()
            for h in handoffs:
                result.handoff.record_handoff(h)
            for _ in range(data.get("oscillations", 0)):
                result.handoff.record_oscillation()
            for _ in range(data.get("deadlocks", 0)):
                result.handoff.record_deadlock()

        for pair in data.get("context_pairs", []):
            if result.context_relevance is None:
                result.context_relevance = ContextRelevance()
            result.context_relevance.record(pair["query"], pair["context"])

        for pair in data.get("sufficiency_pairs", []):
            if result.context_sufficiency is None:
                result.context_sufficiency = ContextSufficiency()
            result.context_sufficiency.record(pair["answer"], pair["context"])

        for pair in data.get("answer_pairs", []):
            if result.answer_relevance is None:
                result.answer_relevance = AnswerRelevance()
            result.answer_relevance.record(pair["query"], pair["answer"])

        for msg in data.get("messages", []):
            if result.communication is None:
                result.communication = CommunicationEfficiency()
            result.communication.record_message(msg.get("useful", True), msg.get("tokens", 0))

        api_calls = data.get("api_calls", [])
        resolutions = data.get("resolutions", 0)
        if api_calls or resolutions:
            result.resource_footprint = ResourceFootprint()
            for call in api_calls:
                result.resource_footprint.record_call(call.get("tokens", 0), call.get("cost_usd", 0.0))
            for _ in range(resolutions):
                result.resource_footprint.record_resolution()

        custom = {k: v for k, v in data.items() if k not in self._KNOWN_KEYS}
        if custom:
            result.custom_metrics = custom

        return result


# ---------------------------------------------------------------------------
# Golden dataset
# ---------------------------------------------------------------------------

MatchMode = Literal["exact", "fuzzy", "substring", "bleu"]


def _bleu_sentence(reference: str, hypothesis: str) -> float:
    """Simplified unigram BLEU score without brevity penalty."""
    ref_tokens = reference.lower().split()
    hyp_tokens = hypothesis.lower().split()
    if not hyp_tokens or not ref_tokens:
        return 0.0
    ref_counts: Counter[str] = Counter(ref_tokens)
    hyp_counts: Counter[str] = Counter(hyp_tokens)
    clipped = sum(min(hyp_counts[t], ref_counts[t]) for t in hyp_counts)
    precision = clipped / len(hyp_tokens)
    bp = min(1.0, len(hyp_tokens) / len(ref_tokens)) if ref_tokens else 0.0
    return precision * bp


class GoldenDataset:
    """Loader for reference-based evaluation datasets with multiple match modes."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self._items: list[dict[str, Any]] = []

    def load(self) -> list[dict[str, Any]]:
        if self.path.suffix == ".json":
            self._items = json.loads(self.path.read_text())
        elif self.path.suffix == ".jsonl":
            self._items = [
                json.loads(line) for line in self.path.read_text().splitlines() if line.strip()
            ]
        else:
            raise ValueError(f"Unsupported format: {self.path.suffix}")
        return self._items

    @property
    def items(self) -> list[dict[str, Any]]:
        if not self._items:
            self.load()
        return self._items

    def evaluate(
        self,
        predictions: Sequence[str],
        reference_key: str = "expected",
        prediction_key: str = "actual",
        mode: MatchMode = "exact",
        fuzzy_threshold: float = 0.8,
    ) -> dict[str, float]:
        """Compare predictions against golden references.

        Args:
            predictions: Either a list of prediction strings **or** ignored
                when ``prediction_key`` is found inside each item.
            reference_key: Key in the dataset item holding the reference answer.
            prediction_key: Key in the dataset item holding a pre-stored prediction
                (used only when *predictions* is empty).
            mode: Matching strategy — ``exact``, ``fuzzy`` (SequenceMatcher),
                ``substring``, or ``bleu``.
            fuzzy_threshold: Minimum ratio for ``fuzzy`` mode to count as correct.
        """
        items = self.items

        preds: list[str]
        if predictions:
            if len(predictions) != len(items):
                raise ValueError(
                    f"Prediction count ({len(predictions)}) != dataset size ({len(items)})"
                )
            preds = list(predictions)
        else:
            preds = [str(item.get(prediction_key, "")) for item in items]

        scores: list[float] = []
        for pred, item in zip(preds, items):
            ref = str(item.get(reference_key, "")).strip()
            pred_clean = pred.strip()

            if mode == "exact":
                scores.append(1.0 if pred_clean == ref else 0.0)
            elif mode == "fuzzy":
                ratio = SequenceMatcher(None, pred_clean.lower(), ref.lower()).ratio()
                scores.append(1.0 if ratio >= fuzzy_threshold else 0.0)
            elif mode == "substring":
                scores.append(1.0 if ref.lower() in pred_clean.lower() else 0.0)
            elif mode == "bleu":
                scores.append(_bleu_sentence(ref, pred_clean))

        total = len(scores)
        return {
            "score": statistics.mean(scores) if scores else 0.0,
            "correct": sum(1 for s in scores if s >= (1.0 if mode != "bleu" else fuzzy_threshold)),
            "total": total,
            "mode": mode,
        }

    def evolve(self, new_items: Sequence[dict[str, Any]]) -> int:
        """Append reviewed items and persist the updated dataset."""
        added = 0
        for item in new_items:
            if item not in self._items:
                self._items.append(item)
                added += 1
        if added > 0:
            self._persist()
        return added

    def _persist(self) -> None:
        if self.path.suffix == ".jsonl":
            self.path.write_text(
                "\n".join(json.dumps(item, default=str) for item in self._items) + "\n"
            )
        else:
            self.path.write_text(json.dumps(self._items, indent=2, default=str))


__all__ = [
    "MetricValue",
    "MetricTracker",
    "TaskSuccessRate",
    "LatencyMetric",
    "HallucinationRate",
    "HandoffEfficiency",
    "ContextRelevance",
    "ContextSufficiency",
    "AnswerRelevance",
    "CommunicationEfficiency",
    "ResourceFootprint",
    "EvaluationResult",
    "EvaluationMixin",
    "MatchMode",
    "GoldenDataset",
]
