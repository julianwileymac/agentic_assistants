# Chunk: cdbb4c5fb446_0

- source: `.venv-lab/Lib/site-packages/websocket/tests/test_http.py`
- lines: 1-108
- chunk: 1/5

```
# -*- coding: utf-8 -*-
#
import os
import os.path
import socket
import ssl
import unittest

import websocket
from websocket._exceptions import WebSocketProxyException, WebSocketException
from websocket._http import (
    _get_addrinfo_list,
    _start_proxied_socket,
    _tunnel,
    connect,
    proxy_info,
    read_headers,
    HAVE_PYTHON_SOCKS,
)

"""
test_http.py
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

try:
    from python_socks._errors import ProxyConnectionError, ProxyError, ProxyTimeoutError
except:
    from websocket._http import ProxyConnectionError, ProxyError, ProxyTimeoutError

# Skip test to access the internet unless TEST_WITH_INTERNET == 1
TEST_WITH_INTERNET = os.environ.get("TEST_WITH_INTERNET", "0") == "1"
TEST_WITH_PROXY = os.environ.get("TEST_WITH_PROXY", "0") == "1"
# Skip tests relying on local websockets server unless LOCAL_WS_SERVER_PORT != -1
LOCAL_WS_SERVER_PORT = os.environ.get("LOCAL_WS_SERVER_PORT", "-1")
TEST_WITH_LOCAL_SERVER = LOCAL_WS_SERVER_PORT != "-1"


class SockMock:
    def __init__(self):
        self.data = []
        self.sent = []

    def add_packet(self, data):
        self.data.append(data)

    def gettimeout(self):
        return None

    def recv(self, bufsize):
        if self.data:
            e = self.data.pop(0)
            if isinstance(e, Exception):
                raise e
            if len(e) > bufsize:
                self.data.insert(0, e[bufsize:])
            return e[:bufsize]

    def send(self, data):
        self.sent.append(data)
        return len(data)

    def close(self):
        pass


class HeaderSockMock(SockMock):
    def __init__(self, fname):
        SockMock.__init__(self)
        path = os.path.join(os.path.dirname(__file__), fname)
        with open(path, "rb") as f:
            self.add_packet(f.read())


class OptsList:
    def __init__(self):
        self.timeout = 1
        self.sockopt = []
        self.sslopt = {"cert_reqs": ssl.CERT_NONE}


class HttpTest(unittest.TestCase):
    def test_read_header(self):
        status, header, _ = read_headers(HeaderSockMock("data/header01.txt"))
        self.assertEqual(status, 101)
        self.assertEqual(header["connection"], "Upgrade")
        # header02.txt is intentionally malformed
        self.assertRaises(
            WebSocketException, read_headers, HeaderSockMock("data/header02.txt")
        )

    def test_tunnel(self):
        self.assertRaises(
```
