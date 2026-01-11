# Chunk: 3ddd1ca9d85b_1

- source: `.venv-lab/Lib/site-packages/websocket/tests/test_dispatcher.py`
- lines: 100-182
- chunk: 2/5

```
> 0 (would sleep in real implementation)
        callback.reset_mock()
        start_time = time.time()
        dispatcher.timeout(0.1, callback)
        elapsed = time.time() - start_time

        callback.assert_called_once()
        self.assertGreaterEqual(elapsed, 0.05)  # Allow some tolerance

    def test_dispatcher_base_reconnect(self):
        """Test DispatcherBase reconnect method"""
        dispatcher = DispatcherBase(self.app, 30.0)
        reconnector = Mock()

        # Test normal reconnect
        dispatcher.reconnect(1, reconnector)
        reconnector.assert_called_once_with(reconnecting=True)

        # Test reconnect with KeyboardInterrupt
        reconnector.reset_mock()
        reconnector.side_effect = KeyboardInterrupt("User interrupted")

        with self.assertRaises(KeyboardInterrupt):
            dispatcher.reconnect(1, reconnector)

    def test_dispatcher_base_send(self):
        """Test DispatcherBase send method"""
        dispatcher = DispatcherBase(self.app, 30.0)
        mock_sock = Mock()
        test_data = b"test data"

        with patch("websocket._dispatcher.send") as mock_send:
            mock_send.return_value = len(test_data)
            result = dispatcher.send(mock_sock, test_data)

            mock_send.assert_called_once_with(mock_sock, test_data)
            self.assertEqual(result, len(test_data))

    def test_dispatcher_read(self):
        """Test Dispatcher read method"""
        dispatcher = Dispatcher(self.app, 5.0)
        read_callback = Mock(return_value=True)
        check_callback = Mock()
        mock_sock = Mock()

        # Mock the selector to control the loop
        with patch("selectors.DefaultSelector") as mock_selector_class:
            mock_selector = Mock()
            mock_selector_class.return_value = mock_selector

            # Make select return immediately (timeout)
            mock_selector.select.return_value = []

            # Stop after first iteration
            def side_effect(*args):
                self.app.keep_running = False
                return []

            mock_selector.select.side_effect = side_effect

            dispatcher.read(mock_sock, read_callback, check_callback)

            # Verify selector was used correctly
            mock_selector.register.assert_called()
            mock_selector.select.assert_called_with(5.0)
            mock_selector.close.assert_called()
            check_callback.assert_called()

    def test_dispatcher_read_with_data(self):
        """Test Dispatcher read method when data is available"""
        dispatcher = Dispatcher(self.app, 5.0)
        read_callback = Mock(return_value=True)
        check_callback = Mock()
        mock_sock = Mock()

        with patch("selectors.DefaultSelector") as mock_selector_class:
            mock_selector = Mock()
            mock_selector_class.return_value = mock_selector

            # First call returns data, second call stops the loop
            call_count = 0
```
