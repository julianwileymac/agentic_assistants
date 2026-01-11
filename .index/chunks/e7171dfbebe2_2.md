# Chunk: e7171dfbebe2_2

- source: `.venv-lab/Lib/site-packages/urllib3/contrib/emscripten/fetch.py`
- lines: 169-244
- chunk: 3/9

```
buffer[0]
            if data_len > 0:
                self.read_len = data_len
                self.read_pos = 0
            elif data_len == ERROR_EXCEPTION:
                string_len = self.int_buffer[1]
                # decode the error string
                js_decoder = js.TextDecoder.new()
                json_str = js_decoder.decode(self.byte_buffer.slice(0, string_len))
                raise _StreamingError(
                    f"Exception thrown in fetch: {json_str}",
                    request=self.request,
                    response=None,
                )
            else:
                # EOF, free the buffers and return zero
                # and free the request
                self.is_live = False
                self.close()
                return 0
        # copy from int32array to python bytes
        ret_length = min(self.read_len, len(memoryview(byte_obj)))
        subarray = self.byte_buffer.subarray(
            self.read_pos, self.read_pos + ret_length
        ).to_py()
        memoryview(byte_obj)[0:ret_length] = subarray
        self.read_len -= ret_length
        self.read_pos += ret_length
        return ret_length


class _StreamingFetcher:
    def __init__(self) -> None:
        # make web-worker and data buffer on startup
        self.streaming_ready = False
        streaming_worker_code = (
            files(__package__)
            .joinpath("emscripten_fetch_worker.js")
            .read_text(encoding="utf-8")
        )
        js_data_blob = js.Blob.new(
            to_js([streaming_worker_code], create_pyproxies=False),
            _obj_from_dict({"type": "application/javascript"}),
        )

        def promise_resolver(js_resolve_fn: JsProxy, js_reject_fn: JsProxy) -> None:
            def onMsg(e: JsProxy) -> None:
                self.streaming_ready = True
                js_resolve_fn(e)

            def onErr(e: JsProxy) -> None:
                js_reject_fn(e)  # Defensive: never happens in ci

            self.js_worker.onmessage = onMsg
            self.js_worker.onerror = onErr

        js_data_url = js.URL.createObjectURL(js_data_blob)
        self.js_worker = js.globalThis.Worker.new(js_data_url)
        self.js_worker_ready_promise = js.globalThis.Promise.new(promise_resolver)

    def send(self, request: EmscriptenRequest) -> EmscriptenResponse:
        headers = {
            k: v for k, v in request.headers.items() if k not in HEADERS_TO_IGNORE
        }

        body = request.body
        fetch_data = {"headers": headers, "body": to_js(body), "method": request.method}
        # start the request off in the worker
        timeout = int(1000 * request.timeout) if request.timeout > 0 else None
        js_shared_buffer = js.SharedArrayBuffer.new(1048576)
        js_int_buffer = js.Int32Array.new(js_shared_buffer)
        js_byte_buffer = js.Uint8Array.new(js_shared_buffer, 8)

        js.Atomics.store(js_int_buffer, 0, ERROR_TIMEOUT)
        js.Atomics.notify(js_int_buffer, 0)
```
