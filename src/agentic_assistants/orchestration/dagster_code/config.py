"""
Dagster run configuration schemas and defaults.

Defines typed run configuration that ops can reference, and provides
helper functions for building common run configs.
"""

from typing import Any, Dict, List, Optional

from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)

try:
    import dagster as dg
    DAGSTER_AVAILABLE = True
except ImportError:
    DAGSTER_AVAILABLE = False
    dg = None  # type: ignore


# ---------------------------------------------------------------------------
# Default run configs for pre-built jobs
# ---------------------------------------------------------------------------

def get_maintenance_run_config(
    workspace_path: str = ".",
    max_age_days: int = 7,
    patterns: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Build run config for the maintenance job.

    Args:
        workspace_path: Path to clean up
        max_age_days: Max file age to keep
        patterns: File glob patterns to clean

    Returns:
        Dagster run config dict
    """
    return {
        "ops": {
            "workspace_cleanup_op": {
                "config": {
                    "workspace_path": workspace_path,
                    "max_age_days": max_age_days,
                    "patterns": patterns or ["*.tmp", "*.log", "*.pyc"],
                }
            }
        }
    }


def get_web_search_run_config(
    query: str = "",
    max_results: int = 10,
) -> Dict[str, Any]:
    """
    Build run config for the web search job.

    Args:
        query: Search query
        max_results: Max results

    Returns:
        Dagster run config dict
    """
    return {
        "ops": {
            "web_search_op": {
                "config": {
                    "query": query,
                    "max_results": max_results,
                }
            }
        }
    }


def get_llm_inference_run_config(
    prompt: str = "",
    model: str = "llama3.2",
    temperature: float = 0.7,
    max_tokens: int = 1024,
) -> Dict[str, Any]:
    """
    Build run config for an LLM inference op.

    Args:
        prompt: Input prompt
        model: Model name
        temperature: Sampling temperature
        max_tokens: Max output tokens

    Returns:
        Dagster run config dict
    """
    return {
        "ops": {
            "llm_inference_op": {
                "config": {
                    "prompt": prompt,
                    "model": model,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                }
            }
        }
    }


# ---------------------------------------------------------------------------
# Code deployment config
# ---------------------------------------------------------------------------

def validate_user_code(code: str) -> Dict[str, Any]:
    """
    Validate user-submitted Python code for Dagster compatibility.

    Performs syntax checking, import validation, and checks for
    Dagster decorator usage.

    Args:
        code: Python source code string

    Returns:
        Dict with keys: valid (bool), errors (list), warnings (list)
    """
    errors: List[str] = []
    warnings: List[str] = []

    # Syntax check
    try:
        compile(code, "<user_code>", "exec")
    except SyntaxError as e:
        errors.append(f"Syntax error at line {e.lineno}: {e.msg}")
        return {"valid": False, "errors": errors, "warnings": warnings}

    # Check for Dagster imports
    if "import dagster" not in code and "from dagster" not in code:
        warnings.append(
            "No Dagster imports found. Consider using 'import dagster as dg'"
        )

    # Check for decorator usage
    has_op = "@dg.op" in code or "@op" in code
    has_job = "@dg.job" in code or "@job" in code
    has_asset = "@dg.asset" in code or "@asset" in code

    if not (has_op or has_job or has_asset):
        warnings.append(
            "No @op, @job, or @asset decorators found. "
            "Code should define at least one Dagster component."
        )

    # Check for dangerous operations
    dangerous_patterns = [
        ("os.system(", "Avoid os.system(); use subprocess instead"),
        ("eval(", "Avoid eval() for security reasons"),
        ("exec(", "Avoid exec() for security reasons"),
        ("__import__", "Avoid __import__; use standard imports"),
    ]
    for pattern, warning in dangerous_patterns:
        if pattern in code:
            warnings.append(warning)

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }
