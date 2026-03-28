"""
Skill-based agentic interface for the Agentic Assistants framework.

Implements the Analyze-Decide-Act lifecycle for modular agent capabilities.
An ``AgentController`` manages a registry of skills and routes incoming
payloads to the appropriate handler.

Usage:
    >>> class SummarizeSkill(BaseSkill):
    ...     name = "summarize"
    ...     def analyze(self, payload): return {"length": len(payload.get("text", ""))}
    ...     def decide(self, analysis): return "short" if analysis["length"] < 100 else "full"
    ...     def act(self, payload, decision): return SkillResult(output=f"[{decision}] done")
    >>> controller = AgentController()
    >>> controller.register(SummarizeSkill())
    >>> result = controller.route("summarize", {"text": "hello"})
"""

from __future__ import annotations

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from typing import Any, Callable, Optional

from pydantic import Field

from agentic_assistants.core.base_models import AgenticBaseModel

logger = logging.getLogger(__name__)

SkillMiddleware = Callable[["BaseSkill", dict[str, Any], "SkillResult"], "SkillResult"]


class SkillConfig(AgenticBaseModel):
    """Per-skill configuration."""

    timeout_seconds: float = Field(default=30.0, gt=0)
    max_retries: int = Field(default=0, ge=0)
    retry_delay_seconds: float = Field(default=0.5, ge=0)
    fallback_skill: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class SkillResult(AgenticBaseModel):
    """Outcome of a single skill execution."""

    output: Any = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    skill_name: str = ""
    decision: str = ""
    latency_ms: float = 0.0
    attempts: int = 1
    metadata: dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None


class BaseSkill(ABC):
    """Abstract base for an agentic skill following the Analyze-Decide-Act pattern.

    Subclasses must set ``name`` and implement the three lifecycle methods.
    """

    name: str = ""
    config: SkillConfig = SkillConfig()

    @abstractmethod
    def analyze(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Process the input payload and extract context for the decision step."""

    @abstractmethod
    def decide(self, analysis: dict[str, Any]) -> str:
        """Select the best course of action based on the analysis."""

    @abstractmethod
    def act(self, payload: dict[str, Any], decision: str) -> SkillResult:
        """Produce the final output for the given payload and decision."""

    def _run_lifecycle(self, payload: dict[str, Any]) -> SkillResult:
        """Single attempt at the Analyze -> Decide -> Act lifecycle."""
        analysis = self.analyze(payload)
        decision = self.decide(analysis)
        result = self.act(payload, decision)
        result.skill_name = self.name
        result.decision = decision
        return result

    def execute(self, payload: dict[str, Any]) -> SkillResult:
        """Run the full Analyze -> Decide -> Act lifecycle with retries."""
        t0 = time.perf_counter()
        last_error: Optional[str] = None

        for attempt in range(1, self.config.max_retries + 2):
            try:
                result = self._run_lifecycle(payload)
                result.latency_ms = (time.perf_counter() - t0) * 1000
                result.attempts = attempt
                return result
            except Exception as exc:
                last_error = str(exc)
                logger.warning(
                    "Skill '%s' attempt %d/%d failed: %s",
                    self.name, attempt, self.config.max_retries + 1, exc,
                )
                if attempt <= self.config.max_retries and self.config.retry_delay_seconds > 0:
                    time.sleep(self.config.retry_delay_seconds)

        return SkillResult(
            skill_name=self.name,
            error=last_error,
            attempts=self.config.max_retries + 1,
            latency_ms=(time.perf_counter() - t0) * 1000,
        )

    async def async_execute(self, payload: dict[str, Any]) -> SkillResult:
        """Async variant of ``execute`` with ``asyncio.wait_for`` timeout."""
        t0 = time.perf_counter()
        last_error: Optional[str] = None

        for attempt in range(1, self.config.max_retries + 2):
            try:
                coro = asyncio.get_event_loop().run_in_executor(
                    None, self._run_lifecycle, payload,
                )
                result = await asyncio.wait_for(coro, timeout=self.config.timeout_seconds)
                result.latency_ms = (time.perf_counter() - t0) * 1000
                result.attempts = attempt
                return result
            except asyncio.TimeoutError:
                last_error = f"Skill '{self.name}' timed out after {self.config.timeout_seconds}s"
                logger.warning(last_error)
            except Exception as exc:
                last_error = str(exc)
                logger.warning(
                    "Skill '%s' async attempt %d/%d failed: %s",
                    self.name, attempt, self.config.max_retries + 1, exc,
                )
            if attempt <= self.config.max_retries and self.config.retry_delay_seconds > 0:
                await asyncio.sleep(self.config.retry_delay_seconds)

        return SkillResult(
            skill_name=self.name,
            error=last_error,
            attempts=self.config.max_retries + 1,
            latency_ms=(time.perf_counter() - t0) * 1000,
        )


class AgentController:
    """Central manager that registers skills and routes inputs.

    Provides a plug-and-play architecture where new skills can be added
    without modifying the core orchestrator.  Supports middleware for
    cross-cutting concerns (logging, telemetry, security).
    """

    def __init__(self, middleware: Optional[list[SkillMiddleware]] = None) -> None:
        self._skills: dict[str, BaseSkill] = {}
        self._middleware: list[SkillMiddleware] = list(middleware or [])

    def add_middleware(self, fn: SkillMiddleware) -> None:
        self._middleware.append(fn)

    def register(self, skill: BaseSkill) -> None:
        if not skill.name:
            raise ValueError("Skill must have a non-empty 'name' attribute")
        if skill.name in self._skills:
            logger.warning("Overwriting existing skill '%s'", skill.name)
        self._skills[skill.name] = skill
        logger.debug("Registered skill '%s'", skill.name)

    def unregister(self, name: str) -> Optional[BaseSkill]:
        return self._skills.pop(name, None)

    def get(self, name: str) -> Optional[BaseSkill]:
        return self._skills.get(name)

    def list_skills(self) -> list[str]:
        return list(self._skills.keys())

    def _apply_middleware(
        self, skill: BaseSkill, payload: dict[str, Any], result: SkillResult,
    ) -> SkillResult:
        for mw in self._middleware:
            result = mw(skill, payload, result)
        return result

    def route(self, skill_name: str, payload: dict[str, Any]) -> SkillResult:
        """Route a payload to the named skill, falling back if configured."""
        skill = self._skills.get(skill_name)
        if skill is None:
            return SkillResult(skill_name=skill_name, error=f"Unknown skill: {skill_name}")

        result = skill.execute(payload)
        result = self._apply_middleware(skill, payload, result)

        if result.error and skill.config.fallback_skill:
            fallback = self._skills.get(skill.config.fallback_skill)
            if fallback:
                logger.info(
                    "Skill '%s' failed, falling back to '%s'",
                    skill_name, skill.config.fallback_skill,
                )
                result = fallback.execute(payload)
                result = self._apply_middleware(fallback, payload, result)

        return result

    async def async_route(self, skill_name: str, payload: dict[str, Any]) -> SkillResult:
        """Async variant of ``route``."""
        skill = self._skills.get(skill_name)
        if skill is None:
            return SkillResult(skill_name=skill_name, error=f"Unknown skill: {skill_name}")

        result = await skill.async_execute(payload)
        result = self._apply_middleware(skill, payload, result)

        if result.error and skill.config.fallback_skill:
            fallback = self._skills.get(skill.config.fallback_skill)
            if fallback:
                logger.info(
                    "Skill '%s' failed, falling back to '%s'",
                    skill_name, skill.config.fallback_skill,
                )
                result = await fallback.async_execute(payload)
                result = self._apply_middleware(fallback, payload, result)

        return result

    def route_best(self, payload: dict[str, Any]) -> SkillResult:
        """Analyze with all skills, then execute only the highest-confidence one."""
        best_skill: Optional[BaseSkill] = None
        best_confidence: float = -1.0

        for skill in self._skills.values():
            try:
                analysis = skill.analyze(payload)
                confidence = float(analysis.get("confidence", 0.0))
                if confidence > best_confidence:
                    best_confidence = confidence
                    best_skill = skill
            except Exception:
                continue

        if best_skill is None:
            return SkillResult(error="No skill could handle the payload")

        result = best_skill.execute(payload)
        return self._apply_middleware(best_skill, payload, result)

    async def async_route_best(self, payload: dict[str, Any]) -> SkillResult:
        """Async variant of ``route_best``."""
        best_skill: Optional[BaseSkill] = None
        best_confidence: float = -1.0

        for skill in self._skills.values():
            try:
                analysis = skill.analyze(payload)
                confidence = float(analysis.get("confidence", 0.0))
                if confidence > best_confidence:
                    best_confidence = confidence
                    best_skill = skill
            except Exception:
                continue

        if best_skill is None:
            return SkillResult(error="No skill could handle the payload")

        result = await best_skill.async_execute(payload)
        return self._apply_middleware(best_skill, payload, result)


__all__ = [
    "SkillConfig",
    "SkillResult",
    "SkillMiddleware",
    "BaseSkill",
    "AgentController",
]
