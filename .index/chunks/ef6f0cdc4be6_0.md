# Chunk: ef6f0cdc4be6_0

- source: `.venv-lab/Lib/site-packages/pip/_vendor/resolvelib/resolvers/__init__.py`
- lines: 1-28
- chunk: 1/1

```
from ..structs import RequirementInformation
from .abstract import AbstractResolver, Result
from .criterion import Criterion
from .exceptions import (
    InconsistentCandidate,
    RequirementsConflicted,
    ResolutionError,
    ResolutionImpossible,
    ResolutionTooDeep,
    ResolverException,
)
from .resolution import Resolution, Resolver

__all__ = [
    "AbstractResolver",
    "Criterion",
    "InconsistentCandidate",
    "RequirementInformation",
    "RequirementsConflicted",
    "Resolution",
    "ResolutionError",
    "ResolutionImpossible",
    "ResolutionTooDeep",
    "Resolver",
    "ResolverException",
    "Result",
]
```
