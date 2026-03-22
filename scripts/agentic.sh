#!/bin/bash
# =============================================================================
# Agentic CLI wrapper for Git Bash on Windows
# =============================================================================
# Git Bash can't directly execute Python entry point scripts on Windows.
# This wrapper calls Python directly to run the CLI.
#
# Usage: ./scripts/agentic.sh <command> [args]
# Example: ./scripts/agentic.sh ollama status
# =============================================================================

# Find the script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Change to project directory
cd "$PROJECT_DIR"

# Activate virtual environment (prefer Poetry's managed venv)
if command -v poetry &> /dev/null; then
    POETRY_VENV=$(poetry env info --path 2>/dev/null || echo "")
    if [ -n "$POETRY_VENV" ] && [ -d "$POETRY_VENV" ]; then
        source "$POETRY_VENV/Scripts/activate" 2>/dev/null || source "$POETRY_VENV/bin/activate" 2>/dev/null
    fi
elif [ -d "py11_venv" ]; then
    source py11_venv/Scripts/activate 2>/dev/null || source py11_venv/bin/activate 2>/dev/null
elif [ -d "venv" ]; then
    source venv/Scripts/activate 2>/dev/null || source venv/bin/activate 2>/dev/null
fi

# Run the CLI via Python module
python -m agentic_assistants "$@"






