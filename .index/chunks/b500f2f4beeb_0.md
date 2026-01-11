# Chunk: b500f2f4beeb_0

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/_pydevd_bundle/pydevd_concurrency_analyser/pydevd_concurrency_logger.py`
- lines: 1-82
- chunk: 1/8

```
import time

from _pydev_bundle._pydev_filesystem_encoding import getfilesystemencoding
from _pydev_bundle._pydev_saved_modules import threading
from _pydevd_bundle import pydevd_xml
from _pydevd_bundle.pydevd_constants import GlobalDebuggerHolder
from _pydevd_bundle.pydevd_constants import get_thread_id
from _pydevd_bundle.pydevd_net_command import NetCommand
from _pydevd_bundle.pydevd_concurrency_analyser.pydevd_thread_wrappers import ObjectWrapper, wrap_attr
import pydevd_file_utils
from _pydev_bundle import pydev_log
import sys

file_system_encoding = getfilesystemencoding()

from urllib.parse import quote

threadingCurrentThread = threading.current_thread

DONT_TRACE_THREADING = ["threading.py", "pydevd.py"]
INNER_METHODS = ["_stop"]
INNER_FILES = ["threading.py"]
THREAD_METHODS = ["start", "_stop", "join"]
LOCK_METHODS = ["__init__", "acquire", "release", "__enter__", "__exit__"]
QUEUE_METHODS = ["put", "get"]

# return time since epoch in milliseconds
cur_time = lambda: int(round(time.time() * 1000000))


def get_text_list_for_frame(frame):
    # partial copy-paste from make_thread_suspend_str
    curFrame = frame
    cmdTextList = []
    try:
        while curFrame:
            # print cmdText
            myId = str(id(curFrame))
            # print "id is ", myId

            if curFrame.f_code is None:
                break  # Iron Python sometimes does not have it!

            myName = curFrame.f_code.co_name  # method name (if in method) or ? if global
            if myName is None:
                break  # Iron Python sometimes does not have it!

            # print "name is ", myName

            absolute_filename = pydevd_file_utils.get_abs_path_real_path_and_base_from_frame(curFrame)[0]

            my_file, _applied_mapping = pydevd_file_utils.map_file_to_client(absolute_filename)

            # print "file is ", my_file
            # my_file = inspect.getsourcefile(curFrame) or inspect.getfile(frame)

            myLine = str(curFrame.f_lineno)
            # print "line is ", myLine

            # the variables are all gotten 'on-demand'
            # variables = pydevd_xml.frame_vars_to_xml(curFrame.f_locals)

            variables = ""
            cmdTextList.append('<frame id="%s" name="%s" ' % (myId, pydevd_xml.make_valid_xml_value(myName)))
            cmdTextList.append('file="%s" line="%s">' % (quote(my_file, "/>_= \t"), myLine))
            cmdTextList.append(variables)
            cmdTextList.append("</frame>")
            curFrame = curFrame.f_back
    except:
        pydev_log.exception()

    return cmdTextList


def send_concurrency_message(event_class, time, name, thread_id, type, event, file, line, frame, lock_id=0, parent=None):
    dbg = GlobalDebuggerHolder.global_dbg
    if dbg is None:
        return
    cmdTextList = ["<xml>"]

    cmdTextList.append("<" + event_class)
```
