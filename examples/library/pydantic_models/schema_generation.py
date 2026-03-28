# requires: pydantic>=2

"""
Derive OpenAI-style tool JSON Schemas from Pydantic models.

LLM tool-calling APIs want a small wrapper object (``type``, ``function``) whose
``parameters`` field is a JSON Schema describing arguments. Pydantic's
``model_json_schema()`` already matches that shape; this module shows how to wrap
it for OpenAI-compatible clients and how to tighten schemas with
``additionalProperties: false`` when your runtime supports strict mode.
"""

from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class WeatherArgs(BaseModel):
    """Arguments for a hypothetical ``get_weather`` tool."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{"city": "Paris", "units": "metric"}],
        }
    )

    city: str = Field(description="City name in English")
    units: str = Field(default="metric", description="``metric`` or ``imperial``")


def openai_function_schema(
    *,
    name: str,
    description: str,
    model: type[BaseModel],
) -> dict[str, Any]:
    """
    Build the ``tools=[{"type":"function","function":{...}}]`` object shape.

    OpenAI expects ``parameters`` to be a JSON Schema object; Pydantic v2 exposes
    that via ``model_json_schema()`` with small reshaping (drop ``$defs`` placement
    is kept inline by default).
    """
    schema = model.model_json_schema()
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": schema,
        },
    }


# --- Design notes -----------------------------------------------------------
# Some providers cap tool schema size — prune ``description`` fields in prod.
# Version your tool names (``get_weather_v2``) when breaking parameters.
# Always test tool JSON against the vendor validator CLI when available.
# ---------------------------------------------------------------------------


def strict_parameters_schema(model: type[BaseModel]) -> dict[str, Any]:
    """Return parameters with ``additionalProperties: false`` for stricter tool use."""
    params = model.model_json_schema()
    params.setdefault("additionalProperties", False)
    if "properties" in params:
        params["required"] = list(params["properties"].keys())
    return params


def main() -> None:
    tool = openai_function_schema(
        name="get_weather",
        description="Look up current weather for a city.",
        model=WeatherArgs,
    )
    print(json.dumps(tool, indent=2)[:400], "...")

    strict = strict_parameters_schema(WeatherArgs)
    print("strict required keys:", strict.get("required"))
    print("additionalProperties:", strict.get("additionalProperties"))

    # ``$defs`` appears when models nest; inline or prune for smaller tool payloads.
    raw_schema = WeatherArgs.model_json_schema()
    print("schema has $defs:", "$defs" in raw_schema)


if __name__ == "__main__":
    main()
