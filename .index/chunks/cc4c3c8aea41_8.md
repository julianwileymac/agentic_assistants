# Chunk: cc4c3c8aea41_8

- source: `.venv-lab/Lib/site-packages/jupyter_server/services/kernels/kernelmanager.py`
- lines: 558-634
- chunk: 9/14

```
,
            "debug_request",
            "debug_reply",
            "stream",
            "display_data",
            "update_display_data",
            "execute_input",
            "execute_result",
            "error",
            "status",
            "clear_output",
            "debug_event",
            "input_request",
            "input_reply",
        ],
        help="""List of kernel message types excluded from user activity tracking.

        This should be a superset of the message types sent on any channel other
        than the shell channel.""",
    )

    def track_message_type(self, message_type):
        return message_type not in self.untracked_message_types

    def start_watching_activity(self, kernel_id):
        """Start watching IOPub messages on a kernel for activity.

        - update last_activity on every message
        - record execution_state from status messages
        """
        kernel = self._kernels[kernel_id]
        # add busy/activity markers:
        kernel.execution_state = "starting"
        kernel.reason = ""
        kernel.last_activity = utcnow()
        kernel._activity_stream = kernel.connect_iopub()
        session = Session(
            config=kernel.session.config,
            key=kernel.session.key,
        )

        def record_activity(msg_list):
            """Record an IOPub message arriving from a kernel"""
            idents, fed_msg_list = session.feed_identities(msg_list)
            msg = session.deserialize(fed_msg_list, content=False)

            msg_type = msg["header"]["msg_type"]
            parent_header = msg.get("parent_header")
            parent_msg_type = None if parent_header is None else parent_header.get("msg_type")
            if (
                self.track_message_type(msg_type)
                or self.track_message_type(parent_msg_type)
                or kernel.execution_state == "busy"
            ):
                self.last_kernel_activity = kernel.last_activity = utcnow()
            if msg_type == "status":
                msg = session.deserialize(fed_msg_list)
                execution_state = msg["content"]["execution_state"]
                if self.track_message_type(parent_msg_type):
                    kernel.execution_state = execution_state
                elif kernel.execution_state == "starting" and execution_state != "starting":
                    # We always normalize post-starting execution state to "idle"
                    # unless we know that the status is in response to one of our
                    # tracked message types.
                    kernel.execution_state = "idle"
                self.log.debug(
                    "activity on %s: %s (%s)",
                    kernel_id,
                    msg_type,
                    kernel.execution_state,
                )
            else:
                self.log.debug("activity on %s: %s", kernel_id, msg_type)

        kernel._activity_stream.on_recv(record_activity)
```
