# Chunk: a8b57db58ace_0

- source: `.venv-lab/Lib/site-packages/websocket/tests/test_ssl_edge_cases.py`
- lines: 1-89
- chunk: 1/10

```
# -*- coding: utf-8 -*-
import unittest
import socket
import ssl
from unittest.mock import Mock, patch, MagicMock

from websocket._ssl_compat import (
    SSLError,
    SSLEOFError,
    SSLWantReadError,
    SSLWantWriteError,
    HAVE_SSL,
)
from websocket._http import _ssl_socket, _wrap_sni_socket
from websocket._exceptions import WebSocketException
from websocket._socket import recv, send

"""
test_ssl_edge_cases.py
websocket - WebSocket client library for Python

Copyright 2025 engn33r

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

class SSLEdgeCasesTest(unittest.TestCase):

    def setUp(self):
        if not HAVE_SSL:
            self.skipTest("SSL not available")

    def test_ssl_handshake_failure(self):
        """Test SSL handshake failure scenarios"""
        mock_sock = Mock()

        # Test SSL handshake timeout
        with patch("ssl.SSLContext") as mock_ssl_context:
            mock_context = Mock()
            mock_ssl_context.return_value = mock_context
            mock_context.wrap_socket.side_effect = socket.timeout(
                "SSL handshake timeout"
            )

            sslopt = {"cert_reqs": ssl.CERT_REQUIRED}

            with self.assertRaises(socket.timeout):
                _ssl_socket(mock_sock, sslopt, "example.com")

    def test_ssl_certificate_verification_failures(self):
        """Test various SSL certificate verification failure scenarios"""
        mock_sock = Mock()

        # Test certificate verification failure
        with patch("ssl.SSLContext") as mock_ssl_context:
            mock_context = Mock()
            mock_ssl_context.return_value = mock_context
            mock_context.wrap_socket.side_effect = ssl.SSLCertVerificationError(
                "Certificate verification failed"
            )

            sslopt = {"cert_reqs": ssl.CERT_REQUIRED, "check_hostname": True}

            with self.assertRaises(ssl.SSLCertVerificationError):
                _ssl_socket(mock_sock, sslopt, "badssl.example")

    def test_ssl_context_configuration_edge_cases(self):
        """Test SSL context configuration with various edge cases"""
        mock_sock = Mock()

        # Test with pre-created SSL context
        with patch("ssl.SSLContext") as mock_ssl_context:
            existing_context = Mock()
            existing_context.wrap_socket.return_value = Mock()
            mock_ssl_context.return_value = existing_context

            sslopt = {"context": existing_context}
```
