# Chunk: 3c8ebfc99fab_0

- source: `.venv-lab/Lib/site-packages/tornado/test/process_test.py`
- lines: 1-74
- chunk: 1/4

```
import asyncio
import logging
import os
import signal
import subprocess
import sys
import time
import unittest

from tornado.httpclient import HTTPClient, HTTPError
from tornado.httpserver import HTTPServer
from tornado.log import gen_log
from tornado.process import fork_processes, task_id, Subprocess
from tornado.simple_httpclient import SimpleAsyncHTTPClient
from tornado.testing import bind_unused_port, ExpectLog, AsyncTestCase, gen_test
from tornado.test.util import skipIfNonUnix
from tornado.web import RequestHandler, Application


# Not using AsyncHTTPTestCase because we need control over the IOLoop.
@skipIfNonUnix
class ProcessTest(unittest.TestCase):
    def get_app(self):
        class ProcessHandler(RequestHandler):
            def get(self):
                if self.get_argument("exit", None):
                    # must use os._exit instead of sys.exit so unittest's
                    # exception handler doesn't catch it
                    os._exit(int(self.get_argument("exit")))
                if self.get_argument("signal", None):
                    os.kill(os.getpid(), int(self.get_argument("signal")))
                self.write(str(os.getpid()))

        return Application([("/", ProcessHandler)])

    def tearDown(self):
        if task_id() is not None:
            # We're in a child process, and probably got to this point
            # via an uncaught exception.  If we return now, both
            # processes will continue with the rest of the test suite.
            # Exit now so the parent process will restart the child
            # (since we don't have a clean way to signal failure to
            # the parent that won't restart)
            logging.error("aborting child process from tearDown")
            logging.shutdown()
            os._exit(1)
        # In the surviving process, clear the alarm we set earlier
        signal.alarm(0)
        super().tearDown()

    def test_multi_process(self):
        # This test doesn't work on twisted because we use the global
        # reactor and don't restore it to a sane state after the fork
        # (asyncio has the same issue, but we have a special case in
        # place for it).
        with ExpectLog(
            gen_log, "(Starting .* processes|child .* exited|uncaught exception)"
        ):
            sock, port = bind_unused_port()

            def get_url(path):
                return "http://127.0.0.1:%d%s" % (port, path)

            # ensure that none of these processes live too long
            signal.alarm(5)  # master process
            try:
                id = fork_processes(3, max_restarts=3)
                self.assertIsNotNone(id)
                signal.alarm(5)  # child processes
            except SystemExit as e:
                # if we exit cleanly from fork_processes, all the child processes
                # finished with status 0
                self.assertEqual(e.code, 0)
```
