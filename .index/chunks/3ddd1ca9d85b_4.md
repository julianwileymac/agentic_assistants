# Chunk: 3ddd1ca9d85b_4

- source: `.venv-lab/Lib/site-packages/websocket/tests/test_dispatcher.py`
- lines: 311-386
- chunk: 5/5

```
ck_dispatcher, handle_disconnect)

        mock_sock = Mock()
        read_callback = Mock()
        check_callback = Mock()

        wrapped.read(mock_sock, read_callback, check_callback)

        # Should delegate to wrapped dispatcher
        self.assertEqual(len(mock_dispatcher.read_calls), 1)

        # Should NOT call timeout when ping_timeout is None
        self.assertEqual(len(mock_dispatcher.timeout_calls), 0)

    def test_wrapped_dispatcher_send(self):
        """Test WrappedDispatcher send method"""
        mock_dispatcher = MockDispatcher()
        handle_disconnect = Mock()
        wrapped = WrappedDispatcher(self.app, 10.0, mock_dispatcher, handle_disconnect)

        mock_sock = Mock()
        test_data = b"test data"

        with patch("websocket._dispatcher.send") as mock_send:
            result = wrapped.send(mock_sock, test_data)

            # Should delegate to dispatcher.buffwrite
            self.assertEqual(len(mock_dispatcher.buffwrite_calls), 1)
            call = mock_dispatcher.buffwrite_calls[0]
            self.assertEqual(call[0], mock_sock)
            self.assertEqual(call[1], test_data)
            self.assertEqual(call[2], mock_send)
            self.assertEqual(call[3], handle_disconnect)

            # Should return data length
            self.assertEqual(result, len(test_data))

    def test_wrapped_dispatcher_timeout(self):
        """Test WrappedDispatcher timeout method"""
        mock_dispatcher = MockDispatcher()
        handle_disconnect = Mock()
        wrapped = WrappedDispatcher(self.app, 10.0, mock_dispatcher, handle_disconnect)

        callback = Mock()
        args = ("arg1", "arg2")

        wrapped.timeout(5.0, callback, *args)

        # Should delegate to wrapped dispatcher
        self.assertEqual(len(mock_dispatcher.timeout_calls), 1)
        call = mock_dispatcher.timeout_calls[0]
        self.assertEqual(call[0], 5.0)
        self.assertEqual(call[1], callback)
        self.assertEqual(call[2], args)

    def test_wrapped_dispatcher_reconnect(self):
        """Test WrappedDispatcher reconnect method"""
        mock_dispatcher = MockDispatcher()
        handle_disconnect = Mock()
        wrapped = WrappedDispatcher(self.app, 10.0, mock_dispatcher, handle_disconnect)

        reconnector = Mock()

        wrapped.reconnect(3, reconnector)

        # Should delegate to timeout method with reconnect=True
        self.assertEqual(len(mock_dispatcher.timeout_calls), 1)
        call = mock_dispatcher.timeout_calls[0]
        self.assertEqual(call[0], 3)
        self.assertEqual(call[1], reconnector)
        self.assertEqual(call[2], (True,))


if __name__ == "__main__":
    unittest.main()
```
