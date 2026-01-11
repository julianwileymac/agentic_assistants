# Chunk: 3c8ebfc99fab_3

- source: `.venv-lab/Lib/site-packages/tornado/test/process_test.py`
- lines: 197-265
- chunk: 4/4

```
 0)
        self.assertEqual(subproc.returncode, ret)

    @gen_test
    def test_sigchild_future(self):
        Subprocess.initialize()
        self.addCleanup(Subprocess.uninitialize)
        subproc = Subprocess([sys.executable, "-c", "pass"])
        ret = yield subproc.wait_for_exit()
        self.assertEqual(ret, 0)
        self.assertEqual(subproc.returncode, ret)

    def test_sigchild_signal(self):
        Subprocess.initialize()
        self.addCleanup(Subprocess.uninitialize)
        subproc = Subprocess(
            [sys.executable, "-c", "import time; time.sleep(30)"],
            stdout=Subprocess.STREAM,
        )
        self.addCleanup(subproc.stdout.close)
        subproc.set_exit_callback(self.stop)

        # For unclear reasons, killing a process too soon after
        # creating it can result in an exit status corresponding to
        # SIGKILL instead of the actual signal involved. This has been
        # observed on macOS 10.15 with Python 3.8 installed via brew,
        # but not with the system-installed Python 3.7.
        time.sleep(0.1)

        os.kill(subproc.pid, signal.SIGTERM)
        try:
            ret = self.wait()
        except AssertionError:
            # We failed to get the termination signal. This test is
            # occasionally flaky on pypy, so try to get a little more
            # information: did the process close its stdout
            # (indicating that the problem is in the parent process's
            # signal handling) or did the child process somehow fail
            # to terminate?
            fut = subproc.stdout.read_until_close()
            fut.add_done_callback(lambda f: self.stop())  # type: ignore
            try:
                self.wait()
            except AssertionError:
                raise AssertionError("subprocess failed to terminate")
            else:
                raise AssertionError(
                    "subprocess closed stdout but failed to " "get termination signal"
                )
        self.assertEqual(subproc.returncode, ret)
        self.assertEqual(ret, -signal.SIGTERM)

    @gen_test
    def test_wait_for_exit_raise(self):
        Subprocess.initialize()
        self.addCleanup(Subprocess.uninitialize)
        subproc = Subprocess([sys.executable, "-c", "import sys; sys.exit(1)"])
        with self.assertRaises(subprocess.CalledProcessError) as cm:
            yield subproc.wait_for_exit()
        self.assertEqual(cm.exception.returncode, 1)

    @gen_test
    def test_wait_for_exit_raise_disabled(self):
        Subprocess.initialize()
        self.addCleanup(Subprocess.uninitialize)
        subproc = Subprocess([sys.executable, "-c", "import sys; sys.exit(1)"])
        ret = yield subproc.wait_for_exit(raise_error=False)
        self.assertEqual(ret, 1)
```
