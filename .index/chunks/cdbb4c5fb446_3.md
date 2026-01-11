# Chunk: cdbb4c5fb446_3

- source: `.venv-lab/Lib/site-packages/websocket/tests/test_http.py`
- lines: 249-320
- chunk: 4/5

```
            f"ws://127.0.0.1:{LOCAL_WS_SERVER_PORT}",
            http_proxy_host="127.0.0.1",
            http_proxy_port="8899",
            proxy_type="http",
        )
        ws.send("Hello, Server")
        server_response = ws.recv()
        self.assertEqual(server_response, "Hello, Server")
        # self.assertEqual(_start_proxied_socket("wss://api.bitfinex.com/ws/2", OptsList(), proxy_info(http_proxy_host="127.0.0.1", http_proxy_port="8899", proxy_type="http"))[1], ("api.bitfinex.com", 443, '/ws/2'))
        self.assertEqual(
            _get_addrinfo_list(
                "api.bitfinex.com",
                443,
                True,
                proxy_info(
                    http_proxy_host="127.0.0.1",
                    http_proxy_port="8899",
                    proxy_type="http",
                ),
            ),
            (
                socket.getaddrinfo(
                    "127.0.0.1", 8899, 0, socket.SOCK_STREAM, socket.SOL_TCP
                ),
                True,
                None,
            ),
        )
        self.assertEqual(
            connect(
                "wss://api.bitfinex.com/ws/2",
                OptsList(),
                proxy_info(
                    http_proxy_host="127.0.0.1", http_proxy_port=8899, proxy_type="http"
                ),
                None,
            )[1],
            ("api.bitfinex.com", 443, "/ws/2"),
        )
        # TODO: Test SOCKS4 and SOCK5 proxies with unit tests

    @unittest.skipUnless(TEST_WITH_INTERNET, "Internet-requiring tests are disabled")
    def test_sslopt(self):
        ssloptions = {
            "check_hostname": False,
            "server_hostname": "ServerName",
            "ssl_version": ssl.PROTOCOL_TLS_CLIENT,
            "ciphers": "TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256:\
                        TLS_AES_128_GCM_SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:\
                        ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384:\
                        ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:\
                        DHE-RSA-CHACHA20-POLY1305:ECDHE-ECDSA-AES128-GCM-SHA256:\
                        ECDHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES128-GCM-SHA256:\
                        ECDHE-ECDSA-AES256-SHA384:ECDHE-RSA-AES256-SHA384:\
                        DHE-RSA-AES256-SHA256:ECDHE-ECDSA-AES128-SHA256:\
                        ECDHE-RSA-AES128-SHA256:DHE-RSA-AES128-SHA256:\
                        ECDHE-ECDSA-AES256-SHA:ECDHE-RSA-AES256-SHA",
            "ecdh_curve": "prime256v1",
        }
        ws_ssl1 = websocket.WebSocket(sslopt=ssloptions)
        ws_ssl1.connect("wss://api.bitfinex.com/ws/2")
        ws_ssl1.send("Hello")
        ws_ssl1.close()

        ws_ssl2 = websocket.WebSocket(sslopt={"check_hostname": True})
        ws_ssl2.connect("wss://api.bitfinex.com/ws/2")
        ws_ssl2.close

    def test_proxy_info(self):
        self.assertEqual(
            proxy_info(
```
