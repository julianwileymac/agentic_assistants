# Chunk: dc9ff3916fac_3

- source: `.venv-lab/Lib/site-packages/pip/_vendor/resolvelib/resolvers/resolution.py`
- lines: 241-320
- chunk: 4/9

```
g looks at this mapping to get the last pin.
            self.state.mapping.pop(name, None)
            self.state.mapping[name] = candidate

            return []

        # All candidates tried, nothing works. This criterion is a dead
        # end, signal for backtracking.
        return causes

    def _patch_criteria(
        self, incompatibilities_from_broken: list[tuple[KT, list[CT]]]
    ) -> bool:
        # Create a new state from the last known-to-work one, and apply
        # the previously gathered incompatibility information.
        for k, incompatibilities in incompatibilities_from_broken:
            if not incompatibilities:
                continue
            try:
                criterion = self.state.criteria[k]
            except KeyError:
                continue
            matches = self._p.find_matches(
                identifier=k,
                requirements=IteratorMapping(
                    self.state.criteria,
                    operator.methodcaller("iter_requirement"),
                ),
                incompatibilities=IteratorMapping(
                    self.state.criteria,
                    operator.attrgetter("incompatibilities"),
                    {k: incompatibilities},
                ),
            )
            candidates: IterableView[CT] = build_iter_view(matches)
            if not candidates:
                return False
            incompatibilities.extend(criterion.incompatibilities)
            self.state.criteria[k] = Criterion(
                candidates=candidates,
                information=list(criterion.information),
                incompatibilities=incompatibilities,
            )
        return True

    def _save_state(self) -> None:
        """Save states for potential rollback if optimistic backjumping fails."""
        if self._save_states is None:
            self._save_states = [
                State(
                    mapping=s.mapping.copy(),
                    criteria=s.criteria.copy(),
                    backtrack_causes=s.backtrack_causes[:],
                )
                for s in self._states
            ]

    def _rollback_states(self) -> None:
        """Rollback states and disable optimistic backjumping."""
        self._optimistic_backjumping_ratio = 0.0
        if self._save_states:
            self._states = self._save_states
            self._save_states = None

    def _backjump(self, causes: list[RequirementInformation[RT, CT]]) -> bool:
        """Perform backjumping.

        When we enter here, the stack is like this::

            [ state Z ]
            [ state Y ]
            [ state X ]
            .... earlier states are irrelevant.

        1. No pins worked for Z, so it does not have a pin.
        2. We want to reset state Y to unpinned, and pin another candidate.
        3. State X holds what state Y was before the pin, but does not
           have the incompatibility information gathered in state Y.
```
