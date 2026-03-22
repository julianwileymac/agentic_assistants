"""
Template catalog and project scaffolding helpers.

This package exposes a manifest-driven template system used by the CLI:

- `agentic templates list`
- `agentic templates show <template-id>`
- `agentic init <template-id>`
"""

from agentic_assistants.templates.loader import (
    TemplateDefinition,
    load_template_catalog,
    list_templates,
    get_template,
    scaffold_template,
)

__all__ = [
    "TemplateDefinition",
    "load_template_catalog",
    "list_templates",
    "get_template",
    "scaffold_template",
]

