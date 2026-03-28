# requires: msgspec pydantic>=2

"""
Rough timing comparison: ``msgspec`` JSON/MessagePack vs Pydantic vs ``json`` module.

This is a micro-benchmark — use ``pyperf`` or ``pytest-benchmark`` for serious work.

Interpret results cautiously: stdlib ``json`` works on ``dict`` views, Pydantic
validates into rich models, and msgspec decodes straight into slotted structs.
Each step solves different problems; the numbers mainly illustrate overhead
magnitudes, not universal rankings.
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass

import msgspec
from pydantic import BaseModel


@dataclass
class DCRow:
    id: int
    label: str
    score: float


class PDRow(BaseModel):
    id: int
    label: str
    score: float


class MSRow(msgspec.Struct):
    id: int
    label: str
    score: float


# --- Design notes -----------------------------------------------------------
# Warm up JIT-less code before measuring; Python timings include interpreter overhead.
# MessagePack shines for service-to-service traffic; JSON for browser clients.
# Prefer profiling your real payload shapes — sparse dicts behave differently.
# ---------------------------------------------------------------------------


def timeit(name: str, fn: object, iterations: int = 10_000) -> float:
    """Return milliseconds for ``iterations`` calls of zero-arg ``fn``."""
    start = time.perf_counter()
    for _ in range(iterations):
        fn()  # type: ignore[operator]
    elapsed_ms = (time.perf_counter() - start) * 1000
    print(f"{name}: {elapsed_ms:.1f} ms ({iterations} iters)")
    return elapsed_ms


def main() -> None:
    rows = [DCRow(i, f"item-{i}", float(i) * 1.5) for i in range(64)]
    pyd_rows = [PDRow.model_validate(asdict(r)) for r in rows]
    ms_rows = [MSRow(id=r.id, label=r.label, score=r.score) for r in rows]

    std_json_bytes = json.dumps([asdict(r) for r in rows]).encode()
    pyd_json_bytes = json.dumps([m.model_dump() for m in pyd_rows]).encode()
    ms_json_bytes = msgspec.json.encode(ms_rows)
    ms_msgpack_bytes = msgspec.msgpack.encode(ms_rows)

    print("--- encode (Python -> bytes) ---")
    timeit("stdlib json.dumps", lambda: json.dumps([asdict(r) for r in rows]).encode())
    timeit("pydantic json", lambda: json.dumps([m.model_dump() for m in pyd_rows]).encode())
    timeit("msgspec json", lambda: msgspec.json.encode(ms_rows))
    timeit("msgspec msgpack", lambda: msgspec.msgpack.encode(ms_rows))

    print("--- decode (bytes -> objects) ---")
    timeit("stdlib json.loads", lambda: json.loads(std_json_bytes))
    timeit("pydantic validate", lambda: [PDRow.model_validate(x) for x in json.loads(pyd_json_bytes)])
    dec_json = msgspec.json.Decoder(list[MSRow])
    dec_mp = msgspec.msgpack.Decoder(list[MSRow])
    timeit("msgspec json decode", lambda: dec_json.decode(ms_json_bytes))
    timeit("msgspec msgpack decode", lambda: dec_mp.decode(ms_msgpack_bytes))

    print("payload sizes: json", len(ms_json_bytes), "msgpack", len(ms_msgpack_bytes))


if __name__ == "__main__":
    main()
