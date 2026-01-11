# Chunk: fcda211deb9c_8

- source: `.venv-lab/Lib/site-packages/debugpy/adapter/servers.py`
- lines: 567-621
- chunk: 9/9

```
    if elapsed > 10:
                    taking_longer_than_expected = True
                    if sys.platform in ("linux", "linux2"):
                        on_output(
                            "stdout",
                            "\nThe attach to PID is taking longer than expected.\n",
                        )
                        on_output(
                            "stdout",
                            "On Linux it's possible to customize the value of\n",
                        )
                        on_output(
                            "stdout",
                            "`PYDEVD_GDB_SCAN_SHARED_LIBRARIES` so that fewer libraries.\n",
                        )
                        on_output(
                            "stdout",
                            "are scanned when searching for the needed symbols.\n\n",
                        )
                        on_output(
                            "stdout",
                            "i.e.: set in your environment variables (and restart your editor/client\n",
                        )
                        on_output(
                            "stdout",
                            "so that it picks up the updated environment variable value):\n\n",
                        )
                        on_output(
                            "stdout",
                            "PYDEVD_GDB_SCAN_SHARED_LIBRARIES=libdl, libltdl, libc, libfreebl3\n\n",
                        )
                        on_output(
                            "stdout",
                            "-- the actual library may be different (the gdb output typically\n",
                        )
                        on_output(
                            "stdout",
                            "-- writes the libraries that will be used, so, it should be possible\n",
                        )
                        on_output(
                            "stdout",
                            "-- to test other libraries if the above doesn't work).\n\n",
                        )
            if taking_longer_than_expected:
                # If taking longer than expected, start showing the actual output to the user.
                old = output_collected
                output_collected = []
                contents = "".join(old)
                if contents:
                    on_output("stderr", contents)                

    threading.Thread(
        target=info_on_timeout, name=f"Injector[PID={pid}] info on timeout", daemon=True
    ).start()
```
