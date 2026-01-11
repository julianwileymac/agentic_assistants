# Chunk: a8b57db58ace_7

- source: `.venv-lab/Lib/site-packages/websocket/tests/test_ssl_edge_cases.py`
- lines: 483-562
- chunk: 8/10

```
ck()

            # IPv6 addresses should not be used for SNI
            ipv6_hostname = "2001:db8::1"
            _ssl_socket(mock_sock, {}, ipv6_hostname)

            # Should use IPv6 address as server_hostname
            mock_context.wrap_socket.assert_called_with(
                mock_sock,
                do_handshake_on_connect=True,
                suppress_ragged_eofs=True,
                server_hostname=ipv6_hostname,
            )

    def test_ssl_buffer_size_edge_cases(self):
        """Test SSL buffer size related edge cases"""
        mock_sock = Mock()

        def mock_recv(bufsize):
            # SSL should never try to read more than 16KB at once
            if bufsize > 16384:
                raise SSLError("[SSL: BAD_LENGTH] buffer too large")
            return b"A" * min(bufsize, 1024)  # Return smaller chunks

        mock_sock.recv.side_effect = mock_recv
        mock_sock.gettimeout.return_value = 30.0

        from websocket._abnf import frame_buffer

        # Frame buffer should handle large requests by chunking
        fb = frame_buffer(lambda size: recv(mock_sock, size), skip_utf8_validation=True)

        # This should work even with large size due to chunking
        result = fb.recv_strict(16384)  # Exactly 16KB

        self.assertGreater(len(result), 0)

    def test_ssl_protocol_downgrade_protection(self):
        """Test SSL protocol downgrade protection"""
        mock_sock = Mock()

        with patch("ssl.SSLContext") as mock_ssl_context:
            mock_context = Mock()
            mock_ssl_context.return_value = mock_context
            mock_context.wrap_socket.side_effect = ssl.SSLError(
                "SSLV3_ALERT_HANDSHAKE_FAILURE"
            )

            sslopt = {"ssl_version": ssl.PROTOCOL_TLS_CLIENT}

            # Should propagate SSL protocol errors
            with self.assertRaises(ssl.SSLError):
                _ssl_socket(mock_sock, sslopt, "example.com")

    def test_ssl_certificate_chain_validation(self):
        """Test SSL certificate chain validation edge cases"""
        mock_sock = Mock()

        with patch("ssl.SSLContext") as mock_ssl_context:
            mock_context = Mock()
            mock_ssl_context.return_value = mock_context

            # Test certificate chain validation failure
            mock_context.wrap_socket.side_effect = ssl.SSLCertVerificationError(
                "certificate verify failed: certificate has expired"
            )

            sslopt = {"cert_reqs": ssl.CERT_REQUIRED, "check_hostname": True}

            with self.assertRaises(ssl.SSLCertVerificationError):
                _ssl_socket(mock_sock, sslopt, "expired.badssl.com")

    def test_ssl_weak_cipher_rejection(self):
        """Test SSL weak cipher rejection scenarios"""
        mock_sock = Mock()

        with patch("ssl.SSLContext") as mock_ssl_context:
            mock_context = Mock()
            mock_ssl_context.return_value = mock_context
```
