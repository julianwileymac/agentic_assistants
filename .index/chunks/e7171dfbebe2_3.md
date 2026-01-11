# Chunk: e7171dfbebe2_3

- source: `.venv-lab/Lib/site-packages/urllib3/contrib/emscripten/fetch.py`
- lines: 237-315
- chunk: 4/9

```
0 else None
        js_shared_buffer = js.SharedArrayBuffer.new(1048576)
        js_int_buffer = js.Int32Array.new(js_shared_buffer)
        js_byte_buffer = js.Uint8Array.new(js_shared_buffer, 8)

        js.Atomics.store(js_int_buffer, 0, ERROR_TIMEOUT)
        js.Atomics.notify(js_int_buffer, 0)
        js_absolute_url = js.URL.new(request.url, js.location).href
        self.js_worker.postMessage(
            _obj_from_dict(
                {
                    "buffer": js_shared_buffer,
                    "url": js_absolute_url,
                    "fetchParams": fetch_data,
                }
            )
        )
        # wait for the worker to send something
        js.Atomics.wait(js_int_buffer, 0, ERROR_TIMEOUT, timeout)
        if js_int_buffer[0] == ERROR_TIMEOUT:
            raise _TimeoutError(
                "Timeout connecting to streaming request",
                request=request,
                response=None,
            )
        elif js_int_buffer[0] == SUCCESS_HEADER:
            # got response
            # header length is in second int of intBuffer
            string_len = js_int_buffer[1]
            # decode the rest to a JSON string
            js_decoder = js.TextDecoder.new()
            # this does a copy (the slice) because decode can't work on shared array
            # for some silly reason
            json_str = js_decoder.decode(js_byte_buffer.slice(0, string_len))
            # get it as an object
            response_obj = json.loads(json_str)
            return EmscriptenResponse(
                request=request,
                status_code=response_obj["status"],
                headers=response_obj["headers"],
                body=_ReadStream(
                    js_int_buffer,
                    js_byte_buffer,
                    request.timeout,
                    self.js_worker,
                    response_obj["connectionID"],
                    request,
                ),
            )
        elif js_int_buffer[0] == ERROR_EXCEPTION:
            string_len = js_int_buffer[1]
            # decode the error string
            js_decoder = js.TextDecoder.new()
            json_str = js_decoder.decode(js_byte_buffer.slice(0, string_len))
            raise _StreamingError(
                f"Exception thrown in fetch: {json_str}", request=request, response=None
            )
        else:
            raise _StreamingError(
                f"Unknown status from worker in fetch: {js_int_buffer[0]}",
                request=request,
                response=None,
            )


class _JSPIReadStream(io.RawIOBase):
    """
    A read stream that uses pyodide.ffi.run_sync to read from a JavaScript fetch
    response. This requires support for WebAssembly JavaScript Promise Integration
    in the containing browser, and for pyodide to be launched via runPythonAsync.

    :param js_read_stream:
        The JavaScript stream reader

    :param timeout:
        Timeout in seconds

    :param request:
```
