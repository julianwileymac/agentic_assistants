# Chunk: dc9ff3916fac_0

- source: `.venv-lab/Lib/site-packages/pip/_vendor/resolvelib/resolvers/resolution.py`
- lines: 1-106
- chunk: 1/9

```
from __future__ import annotations

import collections
import itertools
import operator
from typing import TYPE_CHECKING, Generic

from ..structs import (
    CT,
    KT,
    RT,
    DirectedGraph,
    IterableView,
    IteratorMapping,
    RequirementInformation,
    State,
    build_iter_view,
)
from .abstract import AbstractResolver, Result
from .criterion import Criterion
from .exceptions import (
    InconsistentCandidate,
    RequirementsConflicted,
    ResolutionImpossible,
    ResolutionTooDeep,
    ResolverException,
)

if TYPE_CHECKING:
    from collections.abc import Collection, Iterable, Mapping

    from ..providers import AbstractProvider, Preference
    from ..reporters import BaseReporter

_OPTIMISTIC_BACKJUMPING_RATIO: float = 0.1


def _build_result(state: State[RT, CT, KT]) -> Result[RT, CT, KT]:
    mapping = state.mapping
    all_keys: dict[int, KT | None] = {id(v): k for k, v in mapping.items()}
    all_keys[id(None)] = None

    graph: DirectedGraph[KT | None] = DirectedGraph()
    graph.add(None)  # Sentinel as root dependencies' parent.

    connected: set[KT | None] = {None}
    for key, criterion in state.criteria.items():
        if not _has_route_to_root(state.criteria, key, all_keys, connected):
            continue
        if key not in graph:
            graph.add(key)
        for p in criterion.iter_parent():
            try:
                pkey = all_keys[id(p)]
            except KeyError:
                continue
            if pkey not in graph:
                graph.add(pkey)
            graph.connect(pkey, key)

    return Result(
        mapping={k: v for k, v in mapping.items() if k in connected},
        graph=graph,
        criteria=state.criteria,
    )


class Resolution(Generic[RT, CT, KT]):
    """Stateful resolution object.

    This is designed as a one-off object that holds information to kick start
    the resolution process, and holds the results afterwards.
    """

    def __init__(
        self,
        provider: AbstractProvider[RT, CT, KT],
        reporter: BaseReporter[RT, CT, KT],
    ) -> None:
        self._p = provider
        self._r = reporter
        self._states: list[State[RT, CT, KT]] = []

        # Optimistic backjumping variables
        self._optimistic_backjumping_ratio = _OPTIMISTIC_BACKJUMPING_RATIO
        self._save_states: list[State[RT, CT, KT]] | None = None
        self._optimistic_start_round: int | None = None

    @property
    def state(self) -> State[RT, CT, KT]:
        try:
            return self._states[-1]
        except IndexError as e:
            raise AttributeError("state") from e

    def _push_new_state(self) -> None:
        """Push a new state into history.

        This new state will be used to hold resolution results of the next
        coming round.
        """
        base = self._states[-1]
        state = State(
            mapping=base.mapping.copy(),
            criteria=base.criteria.copy(),
```
