# Chunk: 3c8ebfc99fab_2

- source: `.venv-lab/Lib/site-packages/tornado/test/process_test.py`
- lines: 126-206
- chunk: 3/4

```
ut down cleanly
                    fetch("/?exit=0", fail_ok=True)

                    os._exit(0)
            except Exception:
                logging.error("exception in child process %d", id, exc_info=True)
                raise


@skipIfNonUnix
class SubprocessTest(AsyncTestCase):
    def term_and_wait(self, subproc):
        subproc.proc.terminate()
        subproc.proc.wait()

    @gen_test
    def test_subprocess(self):
        subproc = Subprocess(
            [sys.executable, "-u", "-i", "-I"],
            stdin=Subprocess.STREAM,
            stdout=Subprocess.STREAM,
            stderr=subprocess.STDOUT,
        )
        self.addCleanup(lambda: self.term_and_wait(subproc))
        self.addCleanup(subproc.stdout.close)
        self.addCleanup(subproc.stdin.close)
        yield subproc.stdout.read_until(b">>> ")
        subproc.stdin.write(b"print('hello')\n")
        data = yield subproc.stdout.read_until(b"\n")
        self.assertEqual(data, b"hello\n")

        yield subproc.stdout.read_until(b">>> ")
        subproc.stdin.write(b"raise SystemExit\n")
        data = yield subproc.stdout.read_until_close()
        self.assertEqual(data, b"")

    @gen_test
    def test_close_stdin(self):
        # Close the parent's stdin handle and see that the child recognizes it.
        subproc = Subprocess(
            [sys.executable, "-u", "-i", "-I"],
            stdin=Subprocess.STREAM,
            stdout=Subprocess.STREAM,
            stderr=subprocess.STDOUT,
        )
        self.addCleanup(lambda: self.term_and_wait(subproc))
        yield subproc.stdout.read_until(b">>> ")
        subproc.stdin.close()
        data = yield subproc.stdout.read_until_close()
        self.assertEqual(data, b"\n")

    @gen_test
    def test_stderr(self):
        # This test is mysteriously flaky on twisted: it succeeds, but logs
        # an error of EBADF on closing a file descriptor.
        subproc = Subprocess(
            [sys.executable, "-u", "-c", r"import sys; sys.stderr.write('hello\n')"],
            stderr=Subprocess.STREAM,
        )
        self.addCleanup(lambda: self.term_and_wait(subproc))
        data = yield subproc.stderr.read_until(b"\n")
        self.assertEqual(data, b"hello\n")
        # More mysterious EBADF: This fails if done with self.addCleanup instead of here.
        subproc.stderr.close()

    def test_sigchild(self):
        Subprocess.initialize()
        self.addCleanup(Subprocess.uninitialize)
        subproc = Subprocess([sys.executable, "-c", "pass"])
        subproc.set_exit_callback(self.stop)
        ret = self.wait()
        self.assertEqual(ret, 0)
        self.assertEqual(subproc.returncode, ret)

    @gen_test
    def test_sigchild_future(self):
        Subprocess.initialize()
        self.addCleanup(Subprocess.uninitialize)
        subproc = Subprocess([sys.executable, "-c", "pass"])
        ret = yield subproc.wait_for_exit()
```
