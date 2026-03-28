# requires: (no external deps - uses core package only)

"""Agentic patterns: BaseSkill family, AgentController routing, BaseTrainer mock loop."""

from __future__ import annotations

import logging
import tempfile
from pathlib import Path
from typing import Any

try:
    from agentic_assistants.core.skills import (
        AgentController,
        BaseSkill,
        SkillConfig,
        SkillResult,
    )
    from agentic_assistants.core.trainer import (
        BaseTrainer,
        TrainingConfig,
        TrainingMetrics,
    )
except ImportError as exc:  # pragma: no cover
    _IMPORT_ERROR: ImportError | None = exc
else:
    _IMPORT_ERROR = None


if _IMPORT_ERROR is None:

    class TextAnalysisSkill(BaseSkill):
        name = "text_analysis"
        config = SkillConfig(timeout_seconds=60.0, metadata={"domain": "nlp"})

        def analyze(self, payload: dict[str, Any]) -> dict[str, Any]:
            text = str(payload.get("text", ""))
            return {
                "char_count": len(text),
                "word_count": len(text.split()),
                "confidence": 0.9 if text else 0.1,
            }

        def decide(self, analysis: dict[str, Any]) -> str:
            if analysis["word_count"] < 2:
                return "minimal"
            return "full"

        def act(self, payload: dict[str, Any], decision: str) -> SkillResult:
            text = str(payload.get("text", ""))
            summary = f"[{decision}] chars={len(text)}"
            return SkillResult(output=summary, confidence=0.85, metadata={"skill": self.name})

    class DataTransformSkill(BaseSkill):
        name = "data_transform"
        config = SkillConfig(timeout_seconds=45.0)

        def analyze(self, payload: dict[str, Any]) -> dict[str, Any]:
            rows = payload.get("table", [])
            n = len(rows) if isinstance(rows, list) else 0
            return {"rows": n, "confidence": 0.95 if n else 0.15}

        def decide(self, analysis: dict[str, Any]) -> str:
            return "normalize" if analysis["rows"] else "empty"

        def act(self, payload: dict[str, Any], decision: str) -> SkillResult:
            rows = payload.get("table", [])
            if not isinstance(rows, list):
                rows = []
            scaled = [[float(c) / 10.0 for c in r] for r in rows if r]
            return SkillResult(
                output={"scaled": scaled, "decision": decision},
                confidence=0.8,
                metadata={"skill": self.name},
            )

    class SummarizationSkill(BaseSkill):
        name = "summarization"
        config = SkillConfig(timeout_seconds=90.0)

        def analyze(self, payload: dict[str, Any]) -> dict[str, Any]:
            doc = str(payload.get("document", ""))
            return {
                "sections": doc.count("\n") + 1,
                "confidence": 0.88 if len(doc) > 80 else 0.2,
            }

        def decide(self, analysis: dict[str, Any]) -> str:
            return "bullet" if analysis["sections"] > 3 else "paragraph"

        def act(self, payload: dict[str, Any], decision: str) -> SkillResult:
            doc = str(payload.get("document", ""))
            head = doc[:120] + ("..." if len(doc) > 120 else "")
            return SkillResult(
                output=f"{decision.upper()}: {head}",
                confidence=0.82,
                metadata={"skill": self.name},
            )

    class MockAgentTrainer(BaseTrainer):
        """Tiny training loop to demonstrate BaseTrainer hooks and TrainingMetrics."""

        def __init__(self, config: TrainingConfig) -> None:
            super().__init__(config)
            self._step = 0.0

        def _train_epoch(self, epoch: int) -> dict[str, float]:
            self._step += 1.0
            loss = max(0.05, 1.0 / epoch)
            return {"loss": loss}

        def _valid_epoch(self, epoch: int) -> dict[str, float]:
            val = max(0.04, 0.85 / epoch)
            return {"val_loss": val}

    def main() -> None:
        logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

        print("=" * 60)
        print("AgentController: register skills, route by name")
        print("=" * 60)
        controller = AgentController()
        controller.register(TextAnalysisSkill())
        controller.register(DataTransformSkill())
        controller.register(SummarizationSkill())
        print("Registered skills:", controller.list_skills())

        r_text = controller.route("text_analysis", {"text": "design patterns for ml"})
        print("route(text_analysis):", r_text.output, "| error:", r_text.error)

        r_table = controller.route(
            "data_transform",
            {"table": [[10, 20], [30, 40]]},
        )
        print("route(data_transform):", r_table.output, "| error:", r_table.error)

        r_sum = controller.route(
            "summarization",
            {"document": "Intro\nBody\nConclusion\n" * 5},
        )
        print("route(summarization):", r_sum.output, "| error:", r_sum.error)

        print()
        print("=" * 60)
        print("route_best: auto-select skill via analyze() confidence")
        print("=" * 60)
        best_payload = {
            "text": "short",
            "table": [[1, 2]],
            "document": "x",
        }
        best = controller.route_best(best_payload)
        print(
            "route_best result skill:",
            best.skill_name,
            "confidence field:",
            best.confidence,
            "output:",
            best.output,
        )

        print()
        print("=" * 60)
        print("BaseTrainer: mock training loop, metrics summary")
        print("=" * 60)
        ckpt_dir = Path(tempfile.mkdtemp(prefix="agent_patterns_ckpt_"))
        config = TrainingConfig(
            epochs=4,
            checkpoint_dir=str(ckpt_dir),
            save_every=2,
            log_every=1,
            early_stopping_patience=0,
        )
        trainer = MockAgentTrainer(config)
        metrics: TrainingMetrics = trainer.train()
        print("Training summary:", metrics.summary())
        print("Last val_loss:", metrics.get_last("val_loss"))
        for p in sorted(ckpt_dir.glob("*.json")):
            p.unlink(missing_ok=True)
        ckpt_dir.rmdir()

else:

    def main() -> None:
        print("Install the project so `agentic_assistants` is importable, e.g. `poetry install`.")
        print("Import error:", _IMPORT_ERROR)


if __name__ == "__main__":
    main()
