# Chunk: fcda211deb9c_7

- source: `.venv-lab/Lib/site-packages/debugpy/adapter/servers.py`
- lines: 491-573
- chunk: 8/9

```
g attach-to-PID debugger injector: {0!r}", cmdline)
    try:
        injector = subprocess.Popen(
            cmdline,
            bufsize=0,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
    except Exception as exc:
        log.swallow_exception(
            "Failed to inject debug server into process with PID={0}", pid
        )
        raise messaging.MessageHandlingError(
            "Failed to inject debug server into process with PID={0}: {1}".format(
                pid, exc
            )
        )

    # We need to capture the output of the injector - needed so that it doesn't 
    # get blocked on a write() syscall (besides showing it to the user if it
    # is taking longer than expected).

    output_collected = []
    output_collected.append("--- Starting attach to pid: {0} ---\n".format(pid))

    def capture(stream):
        nonlocal output_collected
        try:
            while True:
                line = stream.readline()
                if not line:
                    break
                line = line.decode("utf-8", "replace")
                output_collected.append(line)
                log.info("Injector[PID={0}] output: {1}", pid, line.rstrip())
            log.info("Injector[PID={0}] exited.", pid)
        except Exception:
            s = io.StringIO()
            traceback.print_exc(file=s)
            on_output("stderr", s.getvalue())

    threading.Thread(
        target=capture,
        name=f"Injector[PID={pid}] stdout",
        args=(injector.stdout,),
        daemon=True,
    ).start()

    def info_on_timeout():
        nonlocal output_collected
        taking_longer_than_expected = False
        initial_time = time.time()
        while True:
            time.sleep(1)
            returncode = injector.poll()
            if returncode is not None:
                if returncode != 0:
                    # Something didn't work out. Let's print more info to the user.
                    on_output(
                        "stderr",
                        "Attach to PID failed.\n\n",
                    )
                    
                    old = output_collected
                    output_collected = []
                    contents = "".join(old)
                    on_output("stderr", "".join(contents))
                break

            elapsed = time.time() - initial_time
            on_output(
                "stdout", "Attaching to PID: %s (elapsed: %.2fs).\n" % (pid, elapsed)
            )

            if not taking_longer_than_expected:
                if elapsed > 10:
                    taking_longer_than_expected = True
                    if sys.platform in ("linux", "linux2"):
                        on_output(
                            "stdout",
                            "\nThe attach to PID is taking longer than expected.\n",
```
