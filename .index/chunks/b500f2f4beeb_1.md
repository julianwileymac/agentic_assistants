# Chunk: b500f2f4beeb_1

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/_pydevd_bundle/pydevd_concurrency_analyser/pydevd_concurrency_logger.py`
- lines: 72-142
- chunk: 2/8

```
eturn cmdTextList


def send_concurrency_message(event_class, time, name, thread_id, type, event, file, line, frame, lock_id=0, parent=None):
    dbg = GlobalDebuggerHolder.global_dbg
    if dbg is None:
        return
    cmdTextList = ["<xml>"]

    cmdTextList.append("<" + event_class)
    cmdTextList.append(' time="%s"' % pydevd_xml.make_valid_xml_value(str(time)))
    cmdTextList.append(' name="%s"' % pydevd_xml.make_valid_xml_value(name))
    cmdTextList.append(' thread_id="%s"' % pydevd_xml.make_valid_xml_value(thread_id))
    cmdTextList.append(' type="%s"' % pydevd_xml.make_valid_xml_value(type))
    if type == "lock":
        cmdTextList.append(' lock_id="%s"' % pydevd_xml.make_valid_xml_value(str(lock_id)))
    if parent is not None:
        cmdTextList.append(' parent="%s"' % pydevd_xml.make_valid_xml_value(parent))
    cmdTextList.append(' event="%s"' % pydevd_xml.make_valid_xml_value(event))
    cmdTextList.append(' file="%s"' % pydevd_xml.make_valid_xml_value(file))
    cmdTextList.append(' line="%s"' % pydevd_xml.make_valid_xml_value(str(line)))
    cmdTextList.append("></" + event_class + ">")

    cmdTextList += get_text_list_for_frame(frame)
    cmdTextList.append("</xml>")

    text = "".join(cmdTextList)
    if dbg.writer is not None:
        dbg.writer.add_command(NetCommand(145, 0, text))


def log_new_thread(global_debugger, t):
    event_time = cur_time() - global_debugger.thread_analyser.start_time
    send_concurrency_message(
        "threading_event", event_time, t.name, get_thread_id(t), "thread", "start", "code_name", 0, None, parent=get_thread_id(t)
    )


class ThreadingLogger:
    def __init__(self):
        self.start_time = cur_time()

    def set_start_time(self, time):
        self.start_time = time

    def log_event(self, frame):
        write_log = False
        self_obj = None
        if "self" in frame.f_locals:
            self_obj = frame.f_locals["self"]
            if isinstance(self_obj, threading.Thread) or self_obj.__class__ == ObjectWrapper:
                write_log = True
        if hasattr(frame, "f_back") and frame.f_back is not None:
            back = frame.f_back
            if hasattr(back, "f_back") and back.f_back is not None:
                back = back.f_back
                if "self" in back.f_locals:
                    if isinstance(back.f_locals["self"], threading.Thread):
                        write_log = True
        try:
            if write_log:
                t = threadingCurrentThread()
                back = frame.f_back
                if not back:
                    return
                name, _, back_base = pydevd_file_utils.get_abs_path_real_path_and_base_from_frame(back)
                event_time = cur_time() - self.start_time
                method_name = frame.f_code.co_name

                if isinstance(self_obj, threading.Thread):
```
