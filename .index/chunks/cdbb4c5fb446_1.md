# Chunk: cdbb4c5fb446_1

- source: `.venv-lab/Lib/site-packages/websocket/tests/test_http.py`
- lines: 99-180
- chunk: 2/5

```
qual(status, 101)
        self.assertEqual(header["connection"], "Upgrade")
        # header02.txt is intentionally malformed
        self.assertRaises(
            WebSocketException, read_headers, HeaderSockMock("data/header02.txt")
        )

    def test_tunnel(self):
        self.assertRaises(
            WebSocketProxyException,
            _tunnel,
            HeaderSockMock("data/header01.txt"),
            "example.com",
            80,
            ("username", "password"),
        )
        self.assertRaises(
            WebSocketProxyException,
            _tunnel,
            HeaderSockMock("data/header02.txt"),
            "example.com",
            80,
            ("username", "password"),
        )

    @unittest.skipUnless(TEST_WITH_INTERNET, "Internet-requiring tests are disabled")
    def test_connect(self):
        # Not currently testing an actual proxy connection, so just check whether proxy errors are raised. This requires internet for a DNS lookup
        if HAVE_PYTHON_SOCKS:
            # Need this check, otherwise case where python_socks is not installed triggers
            # websocket._exceptions.WebSocketException: Python Socks is needed for SOCKS proxying but is not available
            self.assertRaises(
                (ProxyTimeoutError, OSError),
                _start_proxied_socket,
                "wss://example.com",
                OptsList(),
                proxy_info(
                    http_proxy_host="example.com",
                    http_proxy_port="8080",
                    proxy_type="socks4",
                    http_proxy_timeout=1,
                ),
            )
            self.assertRaises(
                (ProxyTimeoutError, OSError),
                _start_proxied_socket,
                "wss://example.com",
                OptsList(),
                proxy_info(
                    http_proxy_host="example.com",
                    http_proxy_port="8080",
                    proxy_type="socks4a",
                    http_proxy_timeout=1,
                ),
            )
            self.assertRaises(
                (ProxyTimeoutError, OSError),
                _start_proxied_socket,
                "wss://example.com",
                OptsList(),
                proxy_info(
                    http_proxy_host="example.com",
                    http_proxy_port="8080",
                    proxy_type="socks5",
                    http_proxy_timeout=1,
                ),
            )
            self.assertRaises(
                (ProxyTimeoutError, OSError),
                _start_proxied_socket,
                "wss://example.com",
                OptsList(),
                proxy_info(
                    http_proxy_host="example.com",
                    http_proxy_port="8080",
                    proxy_type="socks5h",
                    http_proxy_timeout=1,
                ),
            )
            self.assertRaises(
                ProxyConnectionError,
```
