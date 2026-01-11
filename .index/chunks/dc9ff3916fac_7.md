# Chunk: dc9ff3916fac_7

- source: `.venv-lab/Lib/site-packages/pip/_vendor/resolvelib/resolvers/resolution.py`
- lines: 498-570
- chunk: 8/9

```
            )
            else:
                narrowed_unstatisfied_names = unsatisfied_names

            # If there are no unsatisfied names use unsatisfied names
            if not narrowed_unstatisfied_names:
                raise RuntimeError("narrow_requirement_selection returned 0 names")

            # If there is only 1 unsatisfied name skip calling self._get_preference
            if len(narrowed_unstatisfied_names) > 1:
                # Choose the most preferred unpinned criterion to try.
                name = min(narrowed_unstatisfied_names, key=self._get_preference)
            else:
                name = narrowed_unstatisfied_names[0]

            failure_criterion = self._attempt_to_pin_criterion(name)

            if failure_criterion:
                causes = self._extract_causes(failure_criterion)
                # Backjump if pinning fails. The backjump process puts us in
                # an unpinned state, so we can work on it in the next round.
                self._r.resolving_conflicts(causes=causes)

                try:
                    success = self._backjump(causes)
                except ResolutionImpossible:
                    if self._optimistic_backjumping_ratio and self._save_states:
                        failed_optimistic_backjumping = True
                    else:
                        raise
                else:
                    failed_optimistic_backjumping = bool(
                        not success
                        and self._optimistic_backjumping_ratio
                        and self._save_states
                    )

                if failed_optimistic_backjumping and self._save_states:
                    self._rollback_states()
                else:
                    self.state.backtrack_causes[:] = causes

                    # Dead ends everywhere. Give up.
                    if not success:
                        raise ResolutionImpossible(self.state.backtrack_causes)
            else:
                # discard as information sources any invalidated names
                # (unsatisfied names that were previously satisfied)
                newly_unsatisfied_names = {
                    key
                    for key, criterion in self.state.criteria.items()
                    if key in satisfied_names
                    and not self._is_current_pin_satisfying(key, criterion)
                }
                self._remove_information_from_criteria(
                    self.state.criteria, newly_unsatisfied_names
                )
                # Pinning was successful. Push a new state to do another pin.
                self._push_new_state()

            self._r.ending_round(index=round_index, state=self.state)

        raise ResolutionTooDeep(max_rounds)


class Resolver(AbstractResolver[RT, CT, KT]):
    """The thing that performs the actual resolution work."""

    base_exception = ResolverException

    def resolve(  # type: ignore[override]
        self,
```
