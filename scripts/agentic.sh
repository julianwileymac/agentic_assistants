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

# Activate venv if it exists
if [ -d "venv" ]; then
    source venv/Scripts/activate 2>/dev/null || source venv/bin/activate 2>/dev/null
fi

# Run the CLI via Python module
python -m agentic_assistants "$@"



