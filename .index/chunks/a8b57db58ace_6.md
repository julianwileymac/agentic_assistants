# Chunk: a8b57db58ace_6

- source: `.venv-lab/Lib/site-packages/websocket/tests/test_ssl_edge_cases.py`
- lines: 416-492
- chunk: 7/10

```
 WebSocketConnectionClosedException)):
            recv(mock_sock, 100)

    def test_ssl_compression_edge_cases(self):
        """Test SSL compression configuration edge cases"""
        mock_sock = Mock()

        with patch("ssl.SSLContext") as mock_ssl_context:
            mock_context = Mock()
            mock_ssl_context.return_value = mock_context
            mock_context.wrap_socket.return_value = Mock()

            # Test SSL compression options (if available)
            sslopt = {"compression": False}  # Some SSL contexts support this

            try:
                _ssl_socket(mock_sock, sslopt, "example.com")
                # Should not fail even if compression option is not supported
            except AttributeError:
                # Expected if SSL context doesn't support compression option
                pass

    def test_ssl_session_reuse_edge_cases(self):
        """Test SSL session reuse scenarios"""
        mock_sock = Mock()

        with patch("ssl.SSLContext") as mock_ssl_context:
            mock_context = Mock()
            mock_ssl_context.return_value = mock_context
            mock_ssl_sock = Mock()
            mock_context.wrap_socket.return_value = mock_ssl_sock

            # Test session reuse
            mock_ssl_sock.session = "mock_session"
            mock_ssl_sock.session_reused = True

            result = _ssl_socket(mock_sock, {}, "example.com")

            # Should handle session reuse without issues
            self.assertIsNotNone(result)

    def test_ssl_alpn_protocol_edge_cases(self):
        """Test SSL ALPN (Application Layer Protocol Negotiation) edge cases"""
        mock_sock = Mock()

        with patch("ssl.SSLContext") as mock_ssl_context:
            mock_context = Mock()
            mock_ssl_context.return_value = mock_context
            mock_context.wrap_socket.return_value = Mock()

            # Test ALPN configuration
            sslopt = {"alpn_protocols": ["http/1.1", "h2"]}

            # ALPN protocols are not currently supported in the SSL wrapper
            # but the test should not fail
            result = _ssl_socket(mock_sock, sslopt, "example.com")
            self.assertIsNotNone(result)
            # ALPN would need to be implemented in _wrap_sni_socket function

    def test_ssl_sni_edge_cases(self):
        """Test SSL SNI (Server Name Indication) edge cases"""
        mock_sock = Mock()

        # Test with IPv6 address (should not use SNI)
        with patch("ssl.SSLContext") as mock_ssl_context:
            mock_context = Mock()
            mock_ssl_context.return_value = mock_context
            mock_context.wrap_socket.return_value = Mock()

            # IPv6 addresses should not be used for SNI
            ipv6_hostname = "2001:db8::1"
            _ssl_socket(mock_sock, {}, ipv6_hostname)

            # Should use IPv6 address as server_hostname
            mock_context.wrap_socket.assert_called_with(
                mock_sock,
```
