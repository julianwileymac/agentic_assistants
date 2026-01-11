# Chunk: a8b57db58ace_4

- source: `.venv-lab/Lib/site-packages/websocket/tests/test_ssl_edge_cases.py`
- lines: 280-359
- chunk: 5/10

```
gotiation_edge_cases(self):
        """Test SSL renegotiation scenarios"""
        mock_sock = Mock()

        # Simulate SSL renegotiation during read
        call_count = 0

        def mock_recv(bufsize):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise SSLWantReadError("SSL renegotiation required")
            return b"data after renegotiation"

        mock_sock.recv.side_effect = mock_recv
        mock_sock.gettimeout.return_value = 30.0

        with patch("selectors.DefaultSelector") as mock_selector_class:
            mock_selector = Mock()
            mock_selector_class.return_value = mock_selector
            mock_selector.select.return_value = [True]

            result = recv(mock_sock, 100)

            self.assertEqual(result, b"data after renegotiation")
            self.assertEqual(call_count, 2)

    def test_ssl_server_hostname_override(self):
        """Test SSL server hostname override scenarios"""
        mock_sock = Mock()

        with patch("ssl.SSLContext") as mock_ssl_context:
            mock_context = Mock()
            mock_ssl_context.return_value = mock_context
            mock_context.wrap_socket.return_value = Mock()

            # Test server_hostname override
            sslopt = {"server_hostname": "override.example.com"}
            _ssl_socket(mock_sock, sslopt, "original.example.com")

            # Should use override hostname in wrap_socket call
            mock_context.wrap_socket.assert_called_with(
                mock_sock,
                do_handshake_on_connect=True,
                suppress_ragged_eofs=True,
                server_hostname="override.example.com",
            )

    def test_ssl_protocol_version_edge_cases(self):
        """Test SSL protocol version edge cases"""
        mock_sock = Mock()

        # Test with deprecated SSL version
        with patch("ssl.SSLContext") as mock_ssl_context:
            mock_context = Mock()
            mock_ssl_context.return_value = mock_context
            mock_context.wrap_socket.return_value = Mock()

            # Test that deprecated ssl_version is still handled
            if hasattr(ssl, "PROTOCOL_TLS"):
                sslopt = {"ssl_version": ssl.PROTOCOL_TLS}
                _ssl_socket(mock_sock, sslopt, "example.com")

                mock_ssl_context.assert_called_with(ssl.PROTOCOL_TLS)

    def test_ssl_keylog_file_edge_cases(self):
        """Test SSL keylog file configuration edge cases"""
        mock_sock = Mock()

        # Test with SSLKEYLOGFILE environment variable
        with patch.dict("os.environ", {"SSLKEYLOGFILE": "/tmp/ssl_keys.log"}):
            with patch("ssl.SSLContext") as mock_ssl_context:
                mock_context = Mock()
                mock_ssl_context.return_value = mock_context
                mock_context.wrap_socket.return_value = Mock()

                sslopt = {}
                _ssl_socket(mock_sock, sslopt, "example.com")
```
