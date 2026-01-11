# Chunk: 3ddd1ca9d85b_3

- source: `.venv-lab/Lib/site-packages/websocket/tests/test_dispatcher.py`
- lines: 247-322
- chunk: 4/5

```
, mock_selector)

        # Should return the first element of first result tuple
        self.assertEqual(result, mock_ssl_sock)
        mock_selector.select.assert_called_with(5.0)

    def test_ssl_dispatcher_select_no_results(self):
        """Test SSLDispatcher select method with no results"""
        dispatcher = SSLDispatcher(self.app, 5.0)
        mock_ssl_sock = MockSocket()
        mock_ssl_sock.pending_return = False
        self.app.sock.sock = mock_ssl_sock
        mock_selector = Mock()
        mock_selector.select.return_value = []

        result = dispatcher.select(None, mock_selector)

        # Should return None when no results (function doesn't return anything when len(r) == 0)
        self.assertIsNone(result)

    def test_wrapped_dispatcher_init(self):
        """Test WrappedDispatcher initialization"""
        mock_dispatcher = MockDispatcher()
        handle_disconnect = Mock()

        wrapped = WrappedDispatcher(self.app, 10.0, mock_dispatcher, handle_disconnect)

        self.assertEqual(wrapped.app, self.app)
        self.assertEqual(wrapped.ping_timeout, 10.0)
        self.assertEqual(wrapped.dispatcher, mock_dispatcher)
        self.assertEqual(wrapped.handleDisconnect, handle_disconnect)

        # Should have set up signal handler
        self.assertEqual(len(mock_dispatcher.signal_calls), 1)
        sig, handler = mock_dispatcher.signal_calls[0]
        self.assertEqual(sig, 2)  # SIGINT
        self.assertEqual(handler, mock_dispatcher.abort)

    def test_wrapped_dispatcher_read(self):
        """Test WrappedDispatcher read method"""
        mock_dispatcher = MockDispatcher()
        handle_disconnect = Mock()
        wrapped = WrappedDispatcher(self.app, 10.0, mock_dispatcher, handle_disconnect)

        mock_sock = Mock()
        read_callback = Mock()
        check_callback = Mock()

        wrapped.read(mock_sock, read_callback, check_callback)

        # Should delegate to wrapped dispatcher
        self.assertEqual(len(mock_dispatcher.read_calls), 1)
        self.assertEqual(mock_dispatcher.read_calls[0], (mock_sock, read_callback))

        # Should call timeout for ping_timeout
        self.assertEqual(len(mock_dispatcher.timeout_calls), 1)
        timeout_call = mock_dispatcher.timeout_calls[0]
        self.assertEqual(timeout_call[0], 10.0)  # timeout seconds
        self.assertEqual(timeout_call[1], check_callback)  # callback

    def test_wrapped_dispatcher_read_no_ping_timeout(self):
        """Test WrappedDispatcher read method without ping timeout"""
        mock_dispatcher = MockDispatcher()
        handle_disconnect = Mock()
        wrapped = WrappedDispatcher(self.app, None, mock_dispatcher, handle_disconnect)

        mock_sock = Mock()
        read_callback = Mock()
        check_callback = Mock()

        wrapped.read(mock_sock, read_callback, check_callback)

        # Should delegate to wrapped dispatcher
        self.assertEqual(len(mock_dispatcher.read_calls), 1)
```
