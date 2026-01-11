# Chunk: cdbb4c5fb446_2

- source: `.venv-lab/Lib/site-packages/websocket/tests/test_http.py`
- lines: 171-257
- chunk: 3/5

```
       proxy_info(
                    http_proxy_host="example.com",
                    http_proxy_port="8080",
                    proxy_type="socks5h",
                    http_proxy_timeout=1,
                ),
            )
            self.assertRaises(
                ProxyConnectionError,
                connect,
                "wss://example.com",
                OptsList(),
                proxy_info(
                    http_proxy_host="127.0.0.1",
                    http_proxy_port=9999,
                    proxy_type="socks4",
                    http_proxy_timeout=1,
                ),
                None,
            )

        self.assertRaises(
            TypeError,
            _get_addrinfo_list,
            None,
            80,
            True,
            proxy_info(
                http_proxy_host="127.0.0.1", http_proxy_port="9999", proxy_type="http"
            ),
        )
        self.assertRaises(
            TypeError,
            _get_addrinfo_list,
            None,
            80,
            True,
            proxy_info(
                http_proxy_host="127.0.0.1", http_proxy_port="9999", proxy_type="http"
            ),
        )
        self.assertRaises(
            socket.timeout,
            connect,
            "wss://google.com",
            OptsList(),
            proxy_info(
                http_proxy_host="8.8.8.8",
                http_proxy_port=9999,
                proxy_type="http",
                http_proxy_timeout=1,
            ),
            None,
        )
        self.assertEqual(
            connect(
                "wss://google.com",
                OptsList(),
                proxy_info(
                    http_proxy_host="8.8.8.8", http_proxy_port=8080, proxy_type="http"
                ),
                True,
            ),
            (True, ("google.com", 443, "/")),
        )
        # The following test fails on Mac OS with a gaierror, not an OverflowError
        # self.assertRaises(OverflowError, connect, "wss://example.com", OptsList(), proxy_info(http_proxy_host="127.0.0.1", http_proxy_port=99999, proxy_type="socks4", timeout=2), False)

    @unittest.skipUnless(TEST_WITH_INTERNET, "Internet-requiring tests are disabled")
    @unittest.skipUnless(
        TEST_WITH_PROXY, "This test requires a HTTP proxy to be running on port 8899"
    )
    @unittest.skipUnless(
        TEST_WITH_LOCAL_SERVER, "Tests using local websocket server are disabled"
    )
    def test_proxy_connect(self):
        ws = websocket.WebSocket()
        ws.connect(
            f"ws://127.0.0.1:{LOCAL_WS_SERVER_PORT}",
            http_proxy_host="127.0.0.1",
            http_proxy_port="8899",
            proxy_type="http",
        )
        ws.send("Hello, Server")
        server_response = ws.recv()
        self.assertEqual(server_response, "Hello, Server")
```
