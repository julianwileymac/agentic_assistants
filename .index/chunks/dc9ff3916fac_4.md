# Chunk: dc9ff3916fac_4

- source: `.venv-lab/Lib/site-packages/pip/_vendor/resolvelib/resolvers/resolution.py`
- lines: 313-376
- chunk: 5/9

```
tates are irrelevant.

        1. No pins worked for Z, so it does not have a pin.
        2. We want to reset state Y to unpinned, and pin another candidate.
        3. State X holds what state Y was before the pin, but does not
           have the incompatibility information gathered in state Y.

        Each iteration of the loop will:

        1.  Identify Z. The incompatibility is not always caused by the latest
            state. For example, given three requirements A, B and C, with
            dependencies A1, B1 and C1, where A1 and B1 are incompatible: the
            last state might be related to C, so we want to discard the
            previous state.
        2.  Discard Z.
        3.  Discard Y but remember its incompatibility information gathered
            previously, and the failure we're dealing with right now.
        4.  Push a new state Y' based on X, and apply the incompatibility
            information from Y to Y'.
        5a. If this causes Y' to conflict, we need to backtrack again. Make Y'
            the new Z and go back to step 2.
        5b. If the incompatibilities apply cleanly, end backtracking.
        """
        incompatible_reqs: Iterable[CT | RT] = itertools.chain(
            (c.parent for c in causes if c.parent is not None),
            (c.requirement for c in causes),
        )
        incompatible_deps = {self._p.identify(r) for r in incompatible_reqs}
        while len(self._states) >= 3:
            # Remove the state that triggered backtracking.
            del self._states[-1]

            # Optimistically backtrack to a state that caused the incompatibility
            broken_state = self.state
            while True:
                # Retrieve the last candidate pin and known incompatibilities.
                try:
                    broken_state = self._states.pop()
                    name, candidate = broken_state.mapping.popitem()
                except (IndexError, KeyError):
                    raise ResolutionImpossible(causes) from None

                if (
                    not self._optimistic_backjumping_ratio
                    and name not in incompatible_deps
                ):
                    # For safe backjumping only backjump if the current dependency
                    # is not the same as the incompatible dependency
                    break

                # On the first time a non-safe backjump is done the state
                # is saved so we can restore it later if the resolution fails
                if (
                    self._optimistic_backjumping_ratio
                    and self._save_states is None
                    and name not in incompatible_deps
                ):
                    self._save_state()

                # If the current dependencies and the incompatible dependencies
                # are overlapping then we have likely found a cause of the
                # incompatibility
                current_dependencies = {
```
