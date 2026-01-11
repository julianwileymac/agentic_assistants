# Chunk: 3ddd1ca9d85b_0

- source: `.venv-lab/Lib/site-packages/websocket/tests/test_dispatcher.py`
- lines: 1-109
- chunk: 1/5

```
# -*- coding: utf-8 -*-
import socket
import unittest
from unittest.mock import Mock, patch, MagicMock
import threading
import time

import websocket
from websocket._dispatcher import (
    Dispatcher,
    DispatcherBase,
    SSLDispatcher,
    WrappedDispatcher,
)

"""
test_dispatcher.py
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

class MockApp:
    """Mock WebSocketApp for testing"""

    def __init__(self):
        self.keep_running = True
        self.sock = Mock()
        self.sock.sock = Mock()


class MockSocket:
    """Mock socket for testing"""

    def __init__(self):
        self.pending_return = False

    def pending(self):
        return self.pending_return


class MockDispatcher:
    """Mock external dispatcher for WrappedDispatcher testing"""

    def __init__(self):
        self.signal_calls = []
        self.abort_calls = []
        self.read_calls = []
        self.buffwrite_calls = []
        self.timeout_calls = []

    def signal(self, sig, handler):
        self.signal_calls.append((sig, handler))

    def abort(self):
        self.abort_calls.append(True)

    def read(self, sock, callback):
        self.read_calls.append((sock, callback))

    def buffwrite(self, sock, data, send_func, disconnect_handler):
        self.buffwrite_calls.append((sock, data, send_func, disconnect_handler))

    def timeout(self, seconds, callback, *args):
        self.timeout_calls.append((seconds, callback, args))


class DispatcherTest(unittest.TestCase):
    def setUp(self):
        self.app = MockApp()

    def test_dispatcher_base_init(self):
        """Test DispatcherBase initialization"""
        dispatcher = DispatcherBase(self.app, 30.0)

        self.assertEqual(dispatcher.app, self.app)
        self.assertEqual(dispatcher.ping_timeout, 30.0)

    def test_dispatcher_base_timeout(self):
        """Test DispatcherBase timeout method"""
        dispatcher = DispatcherBase(self.app, 30.0)
        callback = Mock()

        # Test with seconds=None (should call callback immediately)
        dispatcher.timeout(None, callback)
        callback.assert_called_once()

        # Test with seconds > 0 (would sleep in real implementation)
        callback.reset_mock()
        start_time = time.time()
        dispatcher.timeout(0.1, callback)
        elapsed = time.time() - start_time

        callback.assert_called_once()
        self.assertGreaterEqual(elapsed, 0.05)  # Allow some tolerance
```
