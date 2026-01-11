# Chunk: a8b57db58ace_1

- source: `.venv-lab/Lib/site-packages/websocket/tests/test_ssl_edge_cases.py`
- lines: 81-149
- chunk: 2/10

```
th pre-created SSL context
        with patch("ssl.SSLContext") as mock_ssl_context:
            existing_context = Mock()
            existing_context.wrap_socket.return_value = Mock()
            mock_ssl_context.return_value = existing_context

            sslopt = {"context": existing_context}

            # Call _ssl_socket which should use the existing context
            _ssl_socket(mock_sock, sslopt, "example.com")

            # Should use the provided context, not create a new one
            existing_context.wrap_socket.assert_called_once()

    def test_ssl_ca_bundle_environment_edge_cases(self):
        """Test CA bundle environment variable edge cases"""
        mock_sock = Mock()

        # Test with non-existent CA bundle file
        with patch.dict(
            "os.environ", {"WEBSOCKET_CLIENT_CA_BUNDLE": "/nonexistent/ca-bundle.crt"}
        ):
            with patch("os.path.isfile", return_value=False):
                with patch("os.path.isdir", return_value=False):
                    with patch("ssl.SSLContext") as mock_ssl_context:
                        mock_context = Mock()
                        mock_ssl_context.return_value = mock_context
                        mock_context.wrap_socket.return_value = Mock()

                        sslopt = {}
                        _ssl_socket(mock_sock, sslopt, "example.com")

                        # Should not try to load non-existent CA bundle
                        mock_context.load_verify_locations.assert_not_called()

        # Test with CA bundle directory
        with patch.dict("os.environ", {"WEBSOCKET_CLIENT_CA_BUNDLE": "/etc/ssl/certs"}):
            with patch("os.path.isfile", return_value=False):
                with patch("os.path.isdir", return_value=True):
                    with patch("ssl.SSLContext") as mock_ssl_context:
                        mock_context = Mock()
                        mock_ssl_context.return_value = mock_context
                        mock_context.wrap_socket.return_value = Mock()

                        sslopt = {}
                        _ssl_socket(mock_sock, sslopt, "example.com")

                        # Should load CA directory
                        mock_context.load_verify_locations.assert_called_with(
                            cafile=None, capath="/etc/ssl/certs"
                        )

    def test_ssl_cipher_configuration_edge_cases(self):
        """Test SSL cipher configuration edge cases"""
        mock_sock = Mock()

        # Test with invalid cipher suite
        with patch("ssl.SSLContext") as mock_ssl_context:
            mock_context = Mock()
            mock_ssl_context.return_value = mock_context
            mock_context.set_ciphers.side_effect = ssl.SSLError(
                "No cipher can be selected"
            )
            mock_context.wrap_socket.return_value = Mock()

            sslopt = {"ciphers": "INVALID_CIPHER"}

            with self.assertRaises(WebSocketException):
```
