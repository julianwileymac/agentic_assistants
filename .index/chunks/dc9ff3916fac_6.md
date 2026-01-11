# Chunk: dc9ff3916fac_6

- source: `.venv-lab/Lib/site-packages/pip/_vendor/resolvelib/resolvers/resolution.py`
- lines: 438-506
- chunk: 7/9

```
l so the first ever pin can have
        # something to backtrack to if it fails. The root state is basically
        # pinning the virtual "root" package in the graph.
        self._push_new_state()

        # Variables for optimistic backjumping
        optimistic_rounds_cutoff: int | None = None
        optimistic_backjumping_start_round: int | None = None

        for round_index in range(max_rounds):
            self._r.starting_round(index=round_index)

            # Handle if optimistic backjumping has been running for too long
            if self._optimistic_backjumping_ratio and self._save_states is not None:
                if optimistic_backjumping_start_round is None:
                    optimistic_backjumping_start_round = round_index
                    optimistic_rounds_cutoff = int(
                        (max_rounds - round_index) * self._optimistic_backjumping_ratio
                    )

                    if optimistic_rounds_cutoff <= 0:
                        self._rollback_states()
                        continue
                elif optimistic_rounds_cutoff is not None:
                    if (
                        round_index - optimistic_backjumping_start_round
                        >= optimistic_rounds_cutoff
                    ):
                        self._rollback_states()
                        continue

            unsatisfied_names = [
                key
                for key, criterion in self.state.criteria.items()
                if not self._is_current_pin_satisfying(key, criterion)
            ]

            # All criteria are accounted for. Nothing more to pin, we are done!
            if not unsatisfied_names:
                self._r.ending(state=self.state)
                return self.state

            # keep track of satisfied names to calculate diff after pinning
            satisfied_names = set(self.state.criteria.keys()) - set(unsatisfied_names)

            if len(unsatisfied_names) > 1:
                narrowed_unstatisfied_names = list(
                    self._p.narrow_requirement_selection(
                        identifiers=unsatisfied_names,
                        resolutions=self.state.mapping,
                        candidates=IteratorMapping(
                            self.state.criteria,
                            operator.attrgetter("candidates"),
                        ),
                        information=IteratorMapping(
                            self.state.criteria,
                            operator.attrgetter("information"),
                        ),
                        backtrack_causes=self.state.backtrack_causes,
                    )
                )
            else:
                narrowed_unstatisfied_names = unsatisfied_names

            # If there are no unsatisfied names use unsatisfied names
            if not narrowed_unstatisfied_names:
                raise RuntimeError("narrow_requirement_selection returned 0 names")
```
