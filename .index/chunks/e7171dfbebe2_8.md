# Chunk: e7171dfbebe2_8

- source: `.venv-lab/Lib/site-packages/urllib3/contrib/emscripten/fetch.py`
- lines: 647-727
- chunk: 9/9

```
equest being handled

    :param response:
        The response being handled (if it exists yet)

    :raises _TimeoutError: If the request times out
    :raises _RequestError: If the request raises a JavaScript exception

    :return: The result of awaiting the promise.
    """
    timer_id = None
    if timeout > 0:
        timer_id = js.setTimeout(
            js_abort_controller.abort.bind(js_abort_controller), int(timeout * 1000)
        )
    try:
        from pyodide.ffi import run_sync

        # run_sync here uses WebAssembly JavaScript Promise Integration to
        # suspend python until the JavaScript promise resolves.
        return run_sync(promise)
    except JsException as err:
        if err.name == "AbortError":
            raise _TimeoutError(
                message="Request timed out", request=request, response=response
            )
        else:
            raise _RequestError(message=err.message, request=request, response=response)
    finally:
        if timer_id is not None:
            js.clearTimeout(timer_id)


def has_jspi() -> bool:
    """
    Return true if jspi can be used.

    This requires both browser support and also WebAssembly
    to be in the correct state - i.e. that the javascript
    call into python was async not sync.

    :return: True if jspi can be used.
    :rtype: bool
    """
    try:
        from pyodide.ffi import can_run_sync, run_sync  # noqa: F401

        return bool(can_run_sync())
    except ImportError:
        return False


def _is_node_js() -> bool:
    """
    Check if we are in Node.js.

    :return: True if we are in Node.js.
    :rtype: bool
    """
    return (
        hasattr(js, "process")
        and hasattr(js.process, "release")
        # According to the Node.js documentation, the release name is always "node".
        and js.process.release.name == "node"
    )


def streaming_ready() -> bool | None:
    if _fetcher:
        return _fetcher.streaming_ready
    else:
        return None  # no fetcher, return None to signify that


async def wait_for_streaming_ready() -> bool:
    if _fetcher:
        await _fetcher.js_worker_ready_promise
        return True
    else:
        return False
```
