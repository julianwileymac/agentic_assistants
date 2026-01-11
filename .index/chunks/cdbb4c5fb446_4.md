# Chunk: cdbb4c5fb446_4

- source: `.venv-lab/Lib/site-packages/websocket/tests/test_http.py`
- lines: 309-371
- chunk: 5/5

```
nex.com/ws/2")
        ws_ssl1.send("Hello")
        ws_ssl1.close()

        ws_ssl2 = websocket.WebSocket(sslopt={"check_hostname": True})
        ws_ssl2.connect("wss://api.bitfinex.com/ws/2")
        ws_ssl2.close

    def test_proxy_info(self):
        self.assertEqual(
            proxy_info(
                http_proxy_host="127.0.0.1", http_proxy_port="8080", proxy_type="http"
            ).proxy_protocol,
            "http",
        )
        self.assertRaises(
            ProxyError,
            proxy_info,
            http_proxy_host="127.0.0.1",
            http_proxy_port="8080",
            proxy_type="badval",
        )
        self.assertEqual(
            proxy_info(
                http_proxy_host="example.com", http_proxy_port="8080", proxy_type="http"
            ).proxy_host,
            "example.com",
        )
        self.assertEqual(
            proxy_info(
                http_proxy_host="127.0.0.1", http_proxy_port="8080", proxy_type="http"
            ).proxy_port,
            "8080",
        )
        self.assertEqual(
            proxy_info(
                http_proxy_host="127.0.0.1", http_proxy_port="8080", proxy_type="http"
            ).auth,
            None,
        )
        self.assertEqual(
            proxy_info(
                http_proxy_host="127.0.0.1",
                http_proxy_port="8080",
                proxy_type="http",
                http_proxy_auth=("my_username123", "my_pass321"),
            ).auth[0],
            "my_username123",
        )
        self.assertEqual(
            proxy_info(
                http_proxy_host="127.0.0.1",
                http_proxy_port="8080",
                proxy_type="http",
                http_proxy_auth=("my_username123", "my_pass321"),
            ).auth[1],
            "my_pass321",
        )


if __name__ == "__main__":
    unittest.main()
```
