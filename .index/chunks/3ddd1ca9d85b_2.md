# Chunk: 3ddd1ca9d85b_2

- source: `.venv-lab/Lib/site-packages/websocket/tests/test_dispatcher.py`
- lines: 172-255
- chunk: 3/5

```
= Mock()
        mock_sock = Mock()

        with patch("selectors.DefaultSelector") as mock_selector_class:
            mock_selector = Mock()
            mock_selector_class.return_value = mock_selector

            # First call returns data, second call stops the loop
            call_count = 0

            def select_side_effect(*args):
                nonlocal call_count
                call_count += 1
                if call_count == 1:
                    return [True]  # Data available
                else:
                    self.app.keep_running = False
                    return []

            mock_selector.select.side_effect = select_side_effect

            dispatcher.read(mock_sock, read_callback, check_callback)

            read_callback.assert_called()
            check_callback.assert_called()

    def test_ssl_dispatcher_read(self):
        """Test SSLDispatcher read method"""
        dispatcher = SSLDispatcher(self.app, 5.0)
        read_callback = Mock(return_value=True)
        check_callback = Mock()

        # Mock socket with pending data
        mock_ssl_sock = MockSocket()
        self.app.sock.sock = mock_ssl_sock

        with patch("selectors.DefaultSelector") as mock_selector_class:
            mock_selector = Mock()
            mock_selector_class.return_value = mock_selector
            mock_selector.select.return_value = []

            # Stop after first iteration
            def side_effect(*args):
                self.app.keep_running = False
                return []

            mock_selector.select.side_effect = side_effect

            dispatcher.read(None, read_callback, check_callback)

            mock_selector.register.assert_called()
            check_callback.assert_called()

    def test_ssl_dispatcher_select_with_pending(self):
        """Test SSLDispatcher select method with pending data"""
        dispatcher = SSLDispatcher(self.app, 5.0)
        mock_ssl_sock = MockSocket()
        mock_ssl_sock.pending_return = True
        self.app.sock.sock = mock_ssl_sock
        mock_selector = Mock()

        result = dispatcher.select(None, mock_selector)

        # When pending() returns True, should return [sock]
        self.assertEqual(result, [mock_ssl_sock])

    def test_ssl_dispatcher_select_without_pending(self):
        """Test SSLDispatcher select method without pending data"""
        dispatcher = SSLDispatcher(self.app, 5.0)
        mock_ssl_sock = MockSocket()
        mock_ssl_sock.pending_return = False
        self.app.sock.sock = mock_ssl_sock
        mock_selector = Mock()
        mock_selector.select.return_value = [(mock_ssl_sock, None)]

        result = dispatcher.select(None, mock_selector)

        # Should return the first element of first result tuple
        self.assertEqual(result, mock_ssl_sock)
        mock_selector.select.assert_called_with(5.0)

    def test_ssl_dispatcher_select_no_results(self):
        """Test SSLDispatcher select method with no results"""
```
