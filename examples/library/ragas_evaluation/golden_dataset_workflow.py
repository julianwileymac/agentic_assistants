# requires: agentic-assistants

"""Golden dataset JSON workflow: load, multi-mode evaluation, evolve with reviewed items."""

from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path
try:
    from agentic_assistants.core.evaluation import GoldenDataset, MatchMode
except ImportError as exc:  # pragma: no cover
    _IMPORT_ERROR: ImportError | None = exc
else:
    _IMPORT_ERROR = None


if _IMPORT_ERROR is None:

    def _write_initial_golden(path: Path) -> None:
        cases = [
            {
                "id": "q1",
                "prompt": "Capital of France?",
                "expected": "Paris",
                "actual": "Paris",
            },
            {
                "id": "q2",
                "prompt": "2+2?",
                "expected": "4",
                "actual": "four",
            },
            {
                "id": "q3",
                "prompt": "Color of the sky on a clear day?",
                "expected": "blue",
                "actual": "The sky appears blue due to Rayleigh scattering.",
            },
        ]
        path.write_text(json.dumps(cases, indent=2), encoding="utf-8")

    def main() -> None:
        print("GoldenDataset: create JSON, load, evaluate (exact/fuzzy/substring/bleu), evolve")
        print("-" * 60)

        tmpdir = Path(tempfile.mkdtemp(prefix="golden_dataset_demo_"))
        golden_path = tmpdir / "golden.json"
        _write_initial_golden(golden_path)
        print("Wrote synthetic golden file:", golden_path)

        ds = GoldenDataset(golden_path)
        ds.load()
        print("Loaded items:", len(ds.items))

        modes: tuple[MatchMode, ...] = ("exact", "fuzzy", "substring", "bleu")
        print("\nEvaluation vs `expected` (predictions from each item's `actual` field):")
        for mode in modes:
            r = ds.evaluate(
                [],
                reference_key="expected",
                prediction_key="actual",
                mode=mode,
                fuzzy_threshold=0.85 if mode != "bleu" else 0.35,
            )
            print(f"  mode={mode!r}: score={r['score']:.4f} correct={r['correct']}/{r['total']}")

        reviewed = [
            {
                "id": "q4",
                "prompt": "Unit of electrical resistance?",
                "expected": "ohm",
                "actual": "Ohm",
            }
        ]
        added = ds.evolve(reviewed)
        print(f"\nEvolve feedback loop: appended {added} reviewed item(s); file updated on disk.")

        ds2 = GoldenDataset(golden_path)
        ds2.load()
        print("Reloaded size:", len(ds2.items))

        exact_after = ds2.evaluate(
            [],
            reference_key="expected",
            prediction_key="actual",
            mode="exact",
        )
        print("Exact match score after evolve:", round(exact_after["score"], 4))

        shutil.rmtree(tmpdir, ignore_errors=True)


else:

    def main() -> None:
        print("Install the project so `agentic_assistants` is importable, e.g. `poetry install`.")
        print("Import error:", _IMPORT_ERROR)


if __name__ == "__main__":
    main()
