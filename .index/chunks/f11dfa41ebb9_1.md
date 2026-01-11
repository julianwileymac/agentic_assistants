# Chunk: f11dfa41ebb9_1

- source: `.venv-lab/Lib/site-packages/jupyter_client/runapp.py`
- lines: 81-115
- chunk: 2/2

```
lf.kernel_manager:
            self.kernel_manager.interrupt_kernel()
        else:
            self.log.error("Cannot interrupt kernels we didn't start.\n")

    def start(self) -> None:
        """Start the application."""
        self.log.debug("jupyter run: starting...")
        super().start()
        self.kernel_client.wait_for_ready(timeout=self.kernel_timeout)
        if self.filenames_to_run:
            for filename in self.filenames_to_run:
                self.log.debug("jupyter run: executing `%s`", filename)
                with open(filename) as fp:
                    code = fp.read()
                    reply = self.kernel_client.execute_interactive(code, timeout=OUTPUT_TIMEOUT)
                    return_code = 0 if reply["content"]["status"] == "ok" else 1
                    if return_code:
                        msg = f"jupyter-run error running '{filename}'"
                        raise Exception(msg)
        else:
            self.log.debug("jupyter run: executing from stdin")
            code = sys.stdin.read()
            reply = self.kernel_client.execute_interactive(code, timeout=OUTPUT_TIMEOUT)
            return_code = 0 if reply["content"]["status"] == "ok" else 1
            if return_code:
                msg = "jupyter-run error running 'stdin'"
                raise Exception(msg)


main = launch_new_instance = RunApp.launch_instance

if __name__ == "__main__":
    main()
```
