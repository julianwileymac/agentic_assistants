# Chunk: a8b57db58ace_2

- source: `.venv-lab/Lib/site-packages/websocket/tests/test_ssl_edge_cases.py`
- lines: 140-216
- chunk: 3/10

```
_context
            mock_context.set_ciphers.side_effect = ssl.SSLError(
                "No cipher can be selected"
            )
            mock_context.wrap_socket.return_value = Mock()

            sslopt = {"ciphers": "INVALID_CIPHER"}

            with self.assertRaises(WebSocketException):
                _ssl_socket(mock_sock, sslopt, "example.com")

    def test_ssl_ecdh_curve_edge_cases(self):
        """Test ECDH curve configuration edge cases"""
        mock_sock = Mock()

        # Test with invalid ECDH curve
        with patch("ssl.SSLContext") as mock_ssl_context:
            mock_context = Mock()
            mock_ssl_context.return_value = mock_context
            mock_context.set_ecdh_curve.side_effect = ValueError("unknown curve name")
            mock_context.wrap_socket.return_value = Mock()

            sslopt = {"ecdh_curve": "invalid_curve"}

            with self.assertRaises(WebSocketException):
                _ssl_socket(mock_sock, sslopt, "example.com")

    def test_ssl_client_certificate_edge_cases(self):
        """Test client certificate configuration edge cases"""
        mock_sock = Mock()

        # Test with non-existent client certificate
        with patch("ssl.SSLContext") as mock_ssl_context:
            mock_context = Mock()
            mock_ssl_context.return_value = mock_context
            mock_context.load_cert_chain.side_effect = FileNotFoundError("No such file")
            mock_context.wrap_socket.return_value = Mock()

            sslopt = {"certfile": "/nonexistent/client.crt"}

            with self.assertRaises(WebSocketException):
                _ssl_socket(mock_sock, sslopt, "example.com")

    def test_ssl_want_read_write_retry_edge_cases(self):
        """Test SSL want read/write retry edge cases"""
        mock_sock = Mock()

        # Test SSLWantReadError with multiple retries before success
        read_attempts = [0]  # Use list for mutable reference

        def mock_recv(bufsize):
            read_attempts[0] += 1
            if read_attempts[0] == 1:
                raise SSLWantReadError("The operation did not complete")
            elif read_attempts[0] == 2:
                return b"data after retries"
            else:
                return b""

        mock_sock.recv.side_effect = mock_recv
        mock_sock.gettimeout.return_value = 30.0

        with patch("selectors.DefaultSelector") as mock_selector_class:
            mock_selector = Mock()
            mock_selector_class.return_value = mock_selector
            mock_selector.select.return_value = [True]  # Always ready

            result = recv(mock_sock, 100)

            self.assertEqual(result, b"data after retries")
            self.assertEqual(read_attempts[0], 2)
            # Should have used selector for retry
            mock_selector.register.assert_called()
            mock_selector.select.assert_called()

    def test_ssl_want_write_retry_edge_cases(self):
```
