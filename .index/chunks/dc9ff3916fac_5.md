# Chunk: dc9ff3916fac_5

- source: `.venv-lab/Lib/site-packages/pip/_vendor/resolvelib/resolvers/resolution.py`
- lines: 368-445
- chunk: 6/9

```
tible_deps
                ):
                    self._save_state()

                # If the current dependencies and the incompatible dependencies
                # are overlapping then we have likely found a cause of the
                # incompatibility
                current_dependencies = {
                    self._p.identify(d) for d in self._p.get_dependencies(candidate)
                }
                if not current_dependencies.isdisjoint(incompatible_deps):
                    break

                # Fallback: We should not backtrack to the point where
                # broken_state.mapping is empty, so stop backtracking for
                # a chance for the resolution to recover
                if not broken_state.mapping:
                    break

                # Guard: We need at least two state to remain to both
                # backtrack and push a new state
                if len(self._states) <= 1:
                    raise ResolutionImpossible(causes)

            incompatibilities_from_broken = [
                (k, list(v.incompatibilities)) for k, v in broken_state.criteria.items()
            ]

            # Also mark the newly known incompatibility.
            incompatibilities_from_broken.append((name, [candidate]))

            self._push_new_state()
            success = self._patch_criteria(incompatibilities_from_broken)

            # It works! Let's work on this new state.
            if success:
                return True

            # State does not work after applying known incompatibilities.
            # Try the still previous state.

        # No way to backtrack anymore.
        return False

    def _extract_causes(
        self, criteron: list[Criterion[RT, CT]]
    ) -> list[RequirementInformation[RT, CT]]:
        """Extract causes from list of criterion and deduplicate"""
        return list({id(i): i for c in criteron for i in c.information}.values())

    def resolve(self, requirements: Iterable[RT], max_rounds: int) -> State[RT, CT, KT]:
        if self._states:
            raise RuntimeError("already resolved")

        self._r.starting()

        # Initialize the root state.
        self._states = [
            State(
                mapping=collections.OrderedDict(),
                criteria={},
                backtrack_causes=[],
            )
        ]
        for r in requirements:
            try:
                self._add_to_criteria(self.state.criteria, r, parent=None)
            except RequirementsConflicted as e:
                raise ResolutionImpossible(e.criterion.information) from e

        # The root state is saved as a sentinel so the first ever pin can have
        # something to backtrack to if it fails. The root state is basically
        # pinning the virtual "root" package in the graph.
        self._push_new_state()

        # Variables for optimistic backjumping
        optimistic_rounds_cutoff: int | None = None
```
