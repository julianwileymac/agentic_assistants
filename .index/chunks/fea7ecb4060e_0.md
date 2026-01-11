# Chunk: fea7ecb4060e_0

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_plugins/pydevd_line_validation.py`
- lines: 1-62
- chunk: 1/3

```
from _pydevd_bundle.pydevd_breakpoints import LineBreakpoint
from _pydevd_bundle.pydevd_api import PyDevdAPI
import bisect
from _pydev_bundle import pydev_log


class LineBreakpointWithLazyValidation(LineBreakpoint):
    def __init__(self, *args, **kwargs):
        LineBreakpoint.__init__(self, *args, **kwargs)
        # This is the _AddBreakpointResult that'll be modified (and then re-sent on the
        # on_changed_breakpoint_state).
        self.add_breakpoint_result = None

        # The signature for the callback should be:
        #     on_changed_breakpoint_state(breakpoint_id: int, add_breakpoint_result: _AddBreakpointResult)
        self.on_changed_breakpoint_state = None

        # When its state is checked (in which case it'd call on_changed_breakpoint_state if the
        # state changed), we store a cache key in 'verified_cache_key' -- in case it changes
        # we'd need to re-verify it (for instance, the template could have changed on disk).
        self.verified_cache_key = None


class ValidationInfo(object):
    def __init__(self):
        self._canonical_normalized_filename_to_last_template_lines = {}

    def _collect_valid_lines_in_template(self, template):
        # We cache the lines in the template itself. Note that among requests the
        # template may be a different instance (because the template contents could be
        # changed on disk), but this may still be called multiple times during the
        # same render session, so, caching is interesting.
        lines_cache = getattr(template, "__pydevd_lines_cache__", None)
        if lines_cache is not None:
            lines, sorted_lines = lines_cache
            return lines, sorted_lines

        lines = self._collect_valid_lines_in_template_uncached(template)

        lines = frozenset(lines)
        sorted_lines = tuple(sorted(lines))
        template.__pydevd_lines_cache__ = lines, sorted_lines
        return lines, sorted_lines

    def _collect_valid_lines_in_template_uncached(self, template):
        raise NotImplementedError()

    def verify_breakpoints(self, py_db, canonical_normalized_filename, template_breakpoints_for_file, template):
        """
        This function should be called whenever a rendering is detected.

        :param str canonical_normalized_filename:
        :param dict[int:LineBreakpointWithLazyValidation] template_breakpoints_for_file:
        """
        valid_lines_frozenset, sorted_lines = self._collect_valid_lines_in_template(template)

        self._canonical_normalized_filename_to_last_template_lines[canonical_normalized_filename] = valid_lines_frozenset, sorted_lines
        self._verify_breakpoints_with_lines_collected(
            py_db, canonical_normalized_filename, template_breakpoints_for_file, valid_lines_frozenset, sorted_lines
        )

```
