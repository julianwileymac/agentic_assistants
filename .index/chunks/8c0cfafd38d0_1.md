# Chunk: 8c0cfafd38d0_1

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/_pydevd_bundle/pydevd_stackless.py`
- lines: 76-150
- chunk: 2/7

```
:
                if tasklet.is_main:
                    name = "MainTasklet"
                else:
                    name = "Tasklet-%s" % (self._tasklet_id,)

            thread_id = tasklet.thread_id
            if thread_id != -1:
                for thread in threading.enumerate():
                    if thread.ident == thread_id:
                        if thread.name:
                            thread_name = "of %s" % (thread.name,)
                        else:
                            thread_name = "of Thread-%s" % (thread.name or str(thread_id),)
                        break
                else:
                    # should not happen.
                    thread_name = "of Thread-%s" % (str(thread_id),)
                thread = None
            else:
                # tasklet is no longer bound to a thread, because its thread ended
                thread_name = "without thread"

            tid = id(tasklet)
            tasklet = None
        else:
            state = "dead"
            name = "Tasklet-%s" % (self._tasklet_id,)
            thread_name = ""
            tid = "-"
        self.tasklet_name = "%s %s %s (%s)" % (state, name, thread_name, tid)

    if not hasattr(stackless.tasklet, "trace_function"):
        # bug https://bitbucket.org/stackless-dev/stackless/issue/42
        # is not fixed. Stackless releases before 2014
        def update_name(self):
            tasklet = self.tasklet_weakref()
            if tasklet:
                try:
                    name = tasklet.name
                except AttributeError:
                    if tasklet.is_main:
                        name = "MainTasklet"
                    else:
                        name = "Tasklet-%s" % (self._tasklet_id,)

                thread_id = tasklet.thread_id
                for thread in threading.enumerate():
                    if thread.ident == thread_id:
                        if thread.name:
                            thread_name = "of %s" % (thread.name,)
                        else:
                            thread_name = "of Thread-%s" % (thread.name or str(thread_id),)
                        break
                else:
                    # should not happen.
                    thread_name = "of Thread-%s" % (str(thread_id),)
                thread = None

                tid = id(tasklet)
                tasklet = None
            else:
                name = "Tasklet-%s" % (self._tasklet_id,)
                thread_name = ""
                tid = "-"
            self.tasklet_name = "%s %s (%s)" % (name, thread_name, tid)


_weak_tasklet_registered_to_info = {}


# =======================================================================================================================
# get_tasklet_info
# =======================================================================================================================
```
