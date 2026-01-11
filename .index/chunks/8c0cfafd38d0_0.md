# Chunk: 8c0cfafd38d0_0

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/_pydevd_bundle/pydevd_stackless.py`
- lines: 1-85
- chunk: 1/7

```
from __future__ import nested_scopes

import weakref
import sys

from _pydevd_bundle.pydevd_comm import get_global_debugger
from _pydevd_bundle.pydevd_constants import call_only_once
from _pydev_bundle._pydev_saved_modules import threading
from _pydevd_bundle.pydevd_custom_frames import update_custom_frame, remove_custom_frame, add_custom_frame
import stackless  # @UnresolvedImport
from _pydev_bundle import pydev_log


# Used so that we don't loose the id (because we'll remove when it's not alive and would generate a new id for the
# same tasklet).
class TaskletToLastId:
    """
    So, why not a WeakKeyDictionary?
    The problem is that removals from the WeakKeyDictionary will create a new tasklet (as it adds a callback to
    remove the key when it's garbage-collected), so, we can get into a recursion.
    """

    def __init__(self):
        self.tasklet_ref_to_last_id = {}
        self._i = 0

    def get(self, tasklet):
        return self.tasklet_ref_to_last_id.get(weakref.ref(tasklet))

    def __setitem__(self, tasklet, last_id):
        self.tasklet_ref_to_last_id[weakref.ref(tasklet)] = last_id
        self._i += 1
        if self._i % 100 == 0:  # Collect at each 100 additions to the dict (no need to rush).
            for tasklet_ref in list(self.tasklet_ref_to_last_id.keys()):
                if tasklet_ref() is None:
                    del self.tasklet_ref_to_last_id[tasklet_ref]


_tasklet_to_last_id = TaskletToLastId()


# =======================================================================================================================
# _TaskletInfo
# =======================================================================================================================
class _TaskletInfo:
    _last_id = 0

    def __init__(self, tasklet_weakref, tasklet):
        self.frame_id = None
        self.tasklet_weakref = tasklet_weakref

        last_id = _tasklet_to_last_id.get(tasklet)
        if last_id is None:
            _TaskletInfo._last_id += 1
            last_id = _TaskletInfo._last_id
            _tasklet_to_last_id[tasklet] = last_id

        self._tasklet_id = last_id

        self.update_name()

    def update_name(self):
        tasklet = self.tasklet_weakref()
        if tasklet:
            if tasklet.blocked:
                state = "blocked"
            elif tasklet.paused:
                state = "paused"
            elif tasklet.scheduled:
                state = "scheduled"
            else:
                state = "<UNEXPECTED>"

            try:
                name = tasklet.name
            except AttributeError:
                if tasklet.is_main:
                    name = "MainTasklet"
                else:
                    name = "Tasklet-%s" % (self._tasklet_id,)

            thread_id = tasklet.thread_id
            if thread_id != -1:
                for thread in threading.enumerate():
```
