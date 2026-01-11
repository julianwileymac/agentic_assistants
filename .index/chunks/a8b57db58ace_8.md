# Chunk: a8b57db58ace_8

- source: `.venv-lab/Lib/site-packages/websocket/tests/test_ssl_edge_cases.py`
- lines: 553-623
- chunk: 9/10

```
expired.badssl.com")

    def test_ssl_weak_cipher_rejection(self):
        """Test SSL weak cipher rejection scenarios"""
        mock_sock = Mock()

        with patch("ssl.SSLContext") as mock_ssl_context:
            mock_context = Mock()
            mock_ssl_context.return_value = mock_context
            mock_context.wrap_socket.side_effect = ssl.SSLError("no shared cipher")

            sslopt = {"ciphers": "RC4-MD5"}  # Intentionally weak cipher

            # Should fail with weak ciphers (SSL error is not wrapped by our code)
            with self.assertRaises(ssl.SSLError):
                _ssl_socket(mock_sock, sslopt, "example.com")

    def test_ssl_hostname_verification_edge_cases(self):
        """Test SSL hostname verification edge cases"""
        mock_sock = Mock()

        # Test with wildcard certificate scenarios
        test_cases = [
            ("*.example.com", "subdomain.example.com"),  # Valid wildcard
            ("*.example.com", "sub.subdomain.example.com"),  # Invalid wildcard depth
            ("example.com", "www.example.com"),  # Hostname mismatch
        ]

        for cert_hostname, connect_hostname in test_cases:
            with self.subTest(cert=cert_hostname, hostname=connect_hostname):
                with patch("ssl.SSLContext") as mock_ssl_context:
                    mock_context = Mock()
                    mock_ssl_context.return_value = mock_context

                    if (
                        cert_hostname != connect_hostname
                        and "sub.subdomain" in connect_hostname
                    ):
                        # Simulate hostname verification failure for invalid wildcard
                        mock_context.wrap_socket.side_effect = ssl.SSLCertVerificationError(
                            f"hostname '{connect_hostname}' doesn't match '{cert_hostname}'"
                        )

                        sslopt = {
                            "cert_reqs": ssl.CERT_REQUIRED,
                            "check_hostname": True,
                        }

                        with self.assertRaises(ssl.SSLCertVerificationError):
                            _ssl_socket(mock_sock, sslopt, connect_hostname)
                    else:
                        mock_context.wrap_socket.return_value = Mock()
                        sslopt = {
                            "cert_reqs": ssl.CERT_REQUIRED,
                            "check_hostname": True,
                        }

                        # Should succeed for valid cases
                        result = _ssl_socket(mock_sock, sslopt, connect_hostname)
                        self.assertIsNotNone(result)

    def test_ssl_memory_bio_edge_cases(self):
        """Test SSL memory BIO edge cases"""
        mock_sock = Mock()

        # Test SSL memory BIO scenarios (if available)
        try:
            import ssl

            if hasattr(ssl, "MemoryBIO"):
```
