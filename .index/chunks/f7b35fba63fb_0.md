# Chunk: f7b35fba63fb_0

- source: `src/agentic_assistants/data/templates/__init__.py`
- lines: 1-44
- chunk: 1/1

```
"""
Data Source Templates for the Agentic Framework.

This module provides a template-based system for defining and creating
data sources with pre-configured settings.

Example:
    >>> from agentic_assistants.data.templates import TemplateRegistry, get_template
    >>> 
    >>> # Get a built-in template
    >>> template = get_template("github-api")
    >>> dataset = template.create_dataset(owner="octocat", repo="hello-world")
    >>> 
    >>> # Register a custom template
    >>> registry = TemplateRegistry()
    >>> registry.register(MyCustomTemplate())
"""

from agentic_assistants.data.templates.base import (
    DataSourceTemplate,
    TemplateParameter,
    TemplateCategory,
)
from agentic_assistants.data.templates.registry import (
    TemplateRegistry,
    get_registry,
    get_template,
    list_templates,
    register_template,
)

__all__ = [
    # Base classes
    "DataSourceTemplate",
    "TemplateParameter",
    "TemplateCategory",
    # Registry functions
    "TemplateRegistry",
    "get_registry",
    "get_template",
    "list_templates",
    "register_template",
]
```
