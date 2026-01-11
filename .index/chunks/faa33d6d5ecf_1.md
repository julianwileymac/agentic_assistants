# Chunk: faa33d6d5ecf_1

- source: `.venv-lab/Lib/site-packages/httpcore/_async/http11.py`
- lines: 91-170
- chunk: 2/6

```
      # then we supress this error and move on to attempting to
                # read the response. Servers can sometimes close the request
                # pre-emptively and then respond with a well formed HTTP
                # error response.
                pass

            async with Trace(
                "receive_response_headers", logger, request, kwargs
            ) as trace:
                (
                    http_version,
                    status,
                    reason_phrase,
                    headers,
                    trailing_data,
                ) = await self._receive_response_headers(**kwargs)
                trace.return_value = (
                    http_version,
                    status,
                    reason_phrase,
                    headers,
                )

            network_stream = self._network_stream

            # CONNECT or Upgrade request
            if (status == 101) or (
                (request.method == b"CONNECT") and (200 <= status < 300)
            ):
                network_stream = AsyncHTTP11UpgradeStream(network_stream, trailing_data)

            return Response(
                status=status,
                headers=headers,
                content=HTTP11ConnectionByteStream(self, request),
                extensions={
                    "http_version": http_version,
                    "reason_phrase": reason_phrase,
                    "network_stream": network_stream,
                },
            )
        except BaseException as exc:
            with AsyncShieldCancellation():
                async with Trace("response_closed", logger, request) as trace:
                    await self._response_closed()
            raise exc

    # Sending the request...

    async def _send_request_headers(self, request: Request) -> None:
        timeouts = request.extensions.get("timeout", {})
        timeout = timeouts.get("write", None)

        with map_exceptions({h11.LocalProtocolError: LocalProtocolError}):
            event = h11.Request(
                method=request.method,
                target=request.url.target,
                headers=request.headers,
            )
        await self._send_event(event, timeout=timeout)

    async def _send_request_body(self, request: Request) -> None:
        timeouts = request.extensions.get("timeout", {})
        timeout = timeouts.get("write", None)

        assert isinstance(request.stream, typing.AsyncIterable)
        async for chunk in request.stream:
            event = h11.Data(data=chunk)
            await self._send_event(event, timeout=timeout)

        await self._send_event(h11.EndOfMessage(), timeout=timeout)

    async def _send_event(self, event: h11.Event, timeout: float | None = None) -> None:
        bytes_to_send = self._h11_state.send(event)
        if bytes_to_send is not None:
            await self._network_stream.write(bytes_to_send, timeout=timeout)

    # Receiving the response...
```
