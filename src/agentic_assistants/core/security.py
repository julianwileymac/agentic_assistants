"""
Security guardrails for agentic systems.

Provides baseline safety checks that all agents can leverage: prompt injection
detection, PII scanning, tool-action allow/deny lists, token enforcement,
and output sanitization.

Usage:
    >>> config = SecurityConfig(blocked_tools=["rm", "drop_table"])
    >>> check_prompt_injection("Ignore all previous instructions")
    True
    >>> detect_pii("Call me at 555-123-4567")
    [PIIMatch(kind='phone', ...)]
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Optional, Sequence

from pydantic import Field, model_validator

from agentic_assistants.core.base_models import AgenticBaseModel

_INJECTION_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"ignore\s+(all\s+)?(previous|prior|above)\s+(instructions|prompts|rules)", re.I),
    re.compile(r"disregard\s+(all\s+)?(your|the)\s+(instructions|rules|guidelines)", re.I),
    re.compile(r"you\s+are\s+now\s+(a|an)\s+\w+", re.I),
    re.compile(r"new\s+instructions?:?\s", re.I),
    re.compile(r"system\s*:\s*", re.I),
    re.compile(r"<\s*/?\s*system\s*>", re.I),
    re.compile(r"\bDAN\b.*\bmode\b", re.I),
    re.compile(r"pretend\s+(you\s+)?(are|to\s+be)", re.I),
    re.compile(r"override\s+(safety|content)\s+(filter|policy)", re.I),
    re.compile(r"jailbreak", re.I),
]

_PII_PATTERNS: dict[str, re.Pattern[str]] = {
    "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "phone": re.compile(r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"),
    "credit_card": re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b"),
    "ip_address": re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"),
}


@dataclass
class PIIMatch:
    """A detected PII occurrence."""

    kind: str
    value: str
    start: int
    end: int


class SecurityConfig(AgenticBaseModel):
    """Security policy for an agent or workflow.

    Custom injection patterns are compiled once at init time via
    ``model_post_init`` for efficiency.
    """

    enable_injection_check: bool = True
    enable_pii_check: bool = True
    blocked_tools: list[str] = Field(default_factory=list)
    allowed_tools: Optional[list[str]] = None
    max_output_tokens: int = Field(default=4096, ge=1)
    custom_injection_patterns: list[str] = Field(default_factory=list)
    pii_kinds_to_detect: list[str] = Field(
        default_factory=lambda: list(_PII_PATTERNS.keys()),
    )
    redact_pii: bool = False

    _compiled_custom_patterns: list[re.Pattern[str]] = []

    @model_validator(mode="after")
    def _compile_custom_patterns(self) -> "SecurityConfig":
        object.__setattr__(
            self,
            "_compiled_custom_patterns",
            [re.compile(p, re.I) for p in self.custom_injection_patterns],
        )
        return self


def check_prompt_injection(
    text: str,
    extra_patterns: Sequence[str | re.Pattern[str]] = (),
) -> bool:
    """Return True if the text contains suspected prompt injection."""
    for pattern in _INJECTION_PATTERNS:
        if pattern.search(text):
            return True
    for raw in extra_patterns:
        if isinstance(raw, re.Pattern):
            if raw.search(text):
                return True
        elif re.search(raw, text, re.I):
            return True
    return False


def detect_pii(
    text: str,
    kinds: Sequence[str] | None = None,
) -> list[PIIMatch]:
    """Scan text for PII and return all matches."""
    results: list[PIIMatch] = []
    check_kinds = kinds or list(_PII_PATTERNS.keys())
    for kind in check_kinds:
        pattern = _PII_PATTERNS.get(kind)
        if pattern is None:
            continue
        for match in pattern.finditer(text):
            results.append(
                PIIMatch(kind=kind, value=match.group(), start=match.start(), end=match.end())
            )
    return results


def redact_pii(text: str, kinds: Sequence[str] | None = None) -> str:
    """Replace PII occurrences with ``[REDACTED:<kind>]`` placeholders."""
    matches = detect_pii(text, kinds)
    for m in sorted(matches, key=lambda x: x.start, reverse=True):
        text = text[: m.start] + f"[REDACTED:{m.kind}]" + text[m.end :]
    return text


@dataclass
class DisallowedActionGuard:
    """Gate that blocks disallowed tool invocations."""

    config: SecurityConfig = field(default_factory=SecurityConfig)

    def check(self, tool_name: str) -> bool:
        """Return True if the tool is allowed."""
        if tool_name in self.config.blocked_tools:
            return False
        if self.config.allowed_tools is not None:
            return tool_name in self.config.allowed_tools
        return True

    def enforce(self, tool_name: str) -> None:
        """Raise ValueError if the tool is blocked."""
        if not self.check(tool_name):
            raise ValueError(f"Tool '{tool_name}' is blocked by security policy")


def enforce_tool_policy(tool_name: str, config: SecurityConfig) -> bool:
    """Check tool against allow/block lists. Raises on violation."""
    guard = DisallowedActionGuard(config=config)
    guard.enforce(tool_name)
    return True


def sanitize_output(text: str, config: SecurityConfig | None = None) -> str:
    """Apply output-side guardrails: PII redaction and token-length trimming."""
    cfg = config or SecurityConfig()
    if cfg.redact_pii:
        text = redact_pii(text, cfg.pii_kinds_to_detect)
    approx_tokens = len(text.split())
    if approx_tokens > cfg.max_output_tokens:
        words = text.split()
        text = " ".join(words[: cfg.max_output_tokens]) + " [TRUNCATED]"
    return text


def validate_security(
    text: str,
    config: SecurityConfig | None = None,
) -> dict[str, Any]:
    """Run all configured security checks and return a report."""
    cfg = config or SecurityConfig()
    report: dict[str, Any] = {"passed": True, "issues": []}

    if cfg.enable_injection_check:
        all_patterns = list(cfg._compiled_custom_patterns) if hasattr(cfg, "_compiled_custom_patterns") else cfg.custom_injection_patterns
        if check_prompt_injection(text, all_patterns):
            report["passed"] = False
            report["issues"].append("prompt_injection_detected")

    if cfg.enable_pii_check:
        pii = detect_pii(text, cfg.pii_kinds_to_detect)
        if pii:
            report["pii_found"] = [{"kind": m.kind, "start": m.start, "end": m.end} for m in pii]
            if not cfg.redact_pii:
                report["passed"] = False
                report["issues"].append("pii_detected")

    approx_tokens = len(text.split())
    if approx_tokens > cfg.max_output_tokens:
        report["passed"] = False
        report["issues"].append("max_output_tokens_exceeded")
        report["token_count"] = approx_tokens

    return report


__all__ = [
    "SecurityConfig",
    "PIIMatch",
    "DisallowedActionGuard",
    "check_prompt_injection",
    "detect_pii",
    "redact_pii",
    "enforce_tool_policy",
    "sanitize_output",
    "validate_security",
]
