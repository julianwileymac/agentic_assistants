# Chunk: fda97fe9caca_4

- source: `.venv-lab/Lib/site-packages/httpcore/_sync/http_proxy.py`
- lines: 271-339
- chunk: 5/6

```
" % (self._remote_origin.host, self._remote_origin.port)

                connect_url = URL(
                    scheme=self._proxy_origin.scheme,
                    host=self._proxy_origin.host,
                    port=self._proxy_origin.port,
                    target=target,
                )
                connect_headers = merge_headers(
                    [(b"Host", target), (b"Accept", b"*/*")], self._proxy_headers
                )
                connect_request = Request(
                    method=b"CONNECT",
                    url=connect_url,
                    headers=connect_headers,
                    extensions=request.extensions,
                )
                connect_response = self._connection.handle_request(
                    connect_request
                )

                if connect_response.status < 200 or connect_response.status > 299:
                    reason_bytes = connect_response.extensions.get("reason_phrase", b"")
                    reason_str = reason_bytes.decode("ascii", errors="ignore")
                    msg = "%d %s" % (connect_response.status, reason_str)
                    self._connection.close()
                    raise ProxyError(msg)

                stream = connect_response.extensions["network_stream"]

                # Upgrade the stream to SSL
                ssl_context = (
                    default_ssl_context()
                    if self._ssl_context is None
                    else self._ssl_context
                )
                alpn_protocols = ["http/1.1", "h2"] if self._http2 else ["http/1.1"]
                ssl_context.set_alpn_protocols(alpn_protocols)

                kwargs = {
                    "ssl_context": ssl_context,
                    "server_hostname": self._remote_origin.host.decode("ascii"),
                    "timeout": timeout,
                }
                with Trace("start_tls", logger, request, kwargs) as trace:
                    stream = stream.start_tls(**kwargs)
                    trace.return_value = stream

                # Determine if we should be using HTTP/1.1 or HTTP/2
                ssl_object = stream.get_extra_info("ssl_object")
                http2_negotiated = (
                    ssl_object is not None
                    and ssl_object.selected_alpn_protocol() == "h2"
                )

                # Create the HTTP/1.1 or HTTP/2 connection
                if http2_negotiated or (self._http2 and not self._http1):
                    from .http2 import HTTP2Connection

                    self._connection = HTTP2Connection(
                        origin=self._remote_origin,
                        stream=stream,
                        keepalive_expiry=self._keepalive_expiry,
                    )
                else:
                    self._connection = HTTP11Connection(
                        origin=self._remote_origin,
                        stream=stream,
```
