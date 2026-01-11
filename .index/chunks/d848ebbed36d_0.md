# Chunk: d848ebbed36d_0

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/_test_attach_to_process.py`
- lines: 1-12
- chunk: 1/1

```
import subprocess
import sys

print(sys.executable)

if __name__ == "__main__":
    p = subprocess.Popen([sys.executable, "-u", "_always_live_program.py"])
    import attach_pydevd

    attach_pydevd.main(attach_pydevd.process_command_line(["--pid", str(p.pid), "--protocol", "http"]))
    p.wait()
```
