# Chunk: 3c8ebfc99fab_1

- source: `.venv-lab/Lib/site-packages/tornado/test/process_test.py`
- lines: 68-137
- chunk: 2/4

```
               self.assertIsNotNone(id)
                signal.alarm(5)  # child processes
            except SystemExit as e:
                # if we exit cleanly from fork_processes, all the child processes
                # finished with status 0
                self.assertEqual(e.code, 0)
                self.assertIsNone(task_id())
                sock.close()
                return
            try:
                if id in (0, 1):
                    self.assertEqual(id, task_id())

                    async def f():
                        server = HTTPServer(self.get_app())
                        server.add_sockets([sock])
                        await asyncio.Event().wait()

                    asyncio.run(f())
                elif id == 2:
                    self.assertEqual(id, task_id())
                    sock.close()
                    # Always use SimpleAsyncHTTPClient here; the curl
                    # version appears to get confused sometimes if the
                    # connection gets closed before it's had a chance to
                    # switch from writing mode to reading mode.
                    client = HTTPClient(SimpleAsyncHTTPClient)

                    def fetch(url, fail_ok=False):
                        try:
                            return client.fetch(get_url(url))
                        except HTTPError as e:
                            if not (fail_ok and e.code == 599):
                                raise

                    # Make two processes exit abnormally
                    fetch("/?exit=2", fail_ok=True)
                    fetch("/?exit=3", fail_ok=True)

                    # They've been restarted, so a new fetch will work
                    int(fetch("/").body)

                    # Now the same with signals
                    # Disabled because on the mac a process dying with a signal
                    # can trigger an "Application exited abnormally; send error
                    # report to Apple?" prompt.
                    # fetch("/?signal=%d" % signal.SIGTERM, fail_ok=True)
                    # fetch("/?signal=%d" % signal.SIGABRT, fail_ok=True)
                    # int(fetch("/").body)

                    # Now kill them normally so they won't be restarted
                    fetch("/?exit=0", fail_ok=True)
                    # One process left; watch it's pid change
                    pid = int(fetch("/").body)
                    fetch("/?exit=4", fail_ok=True)
                    pid2 = int(fetch("/").body)
                    self.assertNotEqual(pid, pid2)

                    # Kill the last one so we shut down cleanly
                    fetch("/?exit=0", fail_ok=True)

                    os._exit(0)
            except Exception:
                logging.error("exception in child process %d", id, exc_info=True)
                raise


@skipIfNonUnix
class SubprocessTest(AsyncTestCase):
```
