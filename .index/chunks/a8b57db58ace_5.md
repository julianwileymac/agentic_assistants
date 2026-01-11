# Chunk: a8b57db58ace_5

- source: `.venv-lab/Lib/site-packages/websocket/tests/test_ssl_edge_cases.py`
- lines: 351-425
- chunk: 6/10

```
 patch("ssl.SSLContext") as mock_ssl_context:
                mock_context = Mock()
                mock_ssl_context.return_value = mock_context
                mock_context.wrap_socket.return_value = Mock()

                sslopt = {}
                _ssl_socket(mock_sock, sslopt, "example.com")

                # Should set keylog_filename
                self.assertEqual(mock_context.keylog_filename, "/tmp/ssl_keys.log")

    def test_ssl_context_verification_modes(self):
        """Test different SSL verification mode combinations"""
        mock_sock = Mock()

        test_cases = [
            # (cert_reqs, check_hostname, expected_verify_mode, expected_check_hostname)
            (ssl.CERT_NONE, False, ssl.CERT_NONE, False),
            (ssl.CERT_REQUIRED, False, ssl.CERT_REQUIRED, False),
            (ssl.CERT_REQUIRED, True, ssl.CERT_REQUIRED, True),
        ]

        for cert_reqs, check_hostname, expected_verify, expected_check in test_cases:
            with self.subTest(cert_reqs=cert_reqs, check_hostname=check_hostname):
                with patch("ssl.SSLContext") as mock_ssl_context:
                    mock_context = Mock()
                    mock_ssl_context.return_value = mock_context
                    mock_context.wrap_socket.return_value = Mock()

                    sslopt = {"cert_reqs": cert_reqs, "check_hostname": check_hostname}
                    _ssl_socket(mock_sock, sslopt, "example.com")

                    self.assertEqual(mock_context.verify_mode, expected_verify)
                    self.assertEqual(mock_context.check_hostname, expected_check)

    def test_ssl_socket_shutdown_edge_cases(self):
        """Test SSL socket shutdown edge cases"""
        from websocket._core import WebSocket

        mock_ssl_sock = Mock()
        mock_ssl_sock.shutdown.side_effect = SSLError("SSL shutdown failed")

        ws = WebSocket()
        ws.sock = mock_ssl_sock
        ws.connected = True

        # Should handle SSL shutdown errors gracefully
        try:
            ws.close()
        except SSLError:
            self.fail("SSL shutdown error should be handled gracefully")

    def test_ssl_socket_close_during_operation(self):
        """Test SSL socket being closed during ongoing operations"""
        mock_sock = Mock()

        # Simulate SSL socket being closed during recv
        mock_sock.recv.side_effect = SSLError(
            "SSL connection has been closed unexpectedly"
        )
        mock_sock.gettimeout.return_value = 30.0

        from websocket._exceptions import WebSocketConnectionClosedException

        # Should handle unexpected SSL closure
        with self.assertRaises((SSLError, WebSocketConnectionClosedException)):
            recv(mock_sock, 100)

    def test_ssl_compression_edge_cases(self):
        """Test SSL compression configuration edge cases"""
        mock_sock = Mock()

        with patch("ssl.SSLContext") as mock_ssl_context:
            mock_context = Mock()
```
