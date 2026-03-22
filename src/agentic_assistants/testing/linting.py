"""
Lightweight linting utilities for code snippets.
"""

from __future__ import annotations

import ast
import json
from typing import Dict, List

import yaml


def lint_code(code: str, language: str = "python") -> Dict[str, List[str]]:
    """Validate code and return a list of issues."""
    issues: List[str] = []
    normalized = (language or "python").lower()

    if normalized in ("python", "py"):
        try:
            ast.parse(code)
        except SyntaxError as exc:
            issues.append(f"SyntaxError: {exc.msg} (line {exc.lineno})")
    elif normalized in ("json",):
        try:
            json.loads(code)
        except json.JSONDecodeError as exc:
            issues.append(f"JSONDecodeError: {exc.msg} (line {exc.lineno})")
    elif normalized in ("yaml", "yml"):
        try:
            yaml.safe_load(code)
        except yaml.YAMLError as exc:
            issues.append(f"YAMLError: {exc}")

    return {"issues": issues}
