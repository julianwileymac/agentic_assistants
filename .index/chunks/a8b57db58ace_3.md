# Chunk: a8b57db58ace_3

- source: `.venv-lab/Lib/site-packages/websocket/tests/test_ssl_edge_cases.py`
- lines: 209-291
- chunk: 4/10

```
elf.assertEqual(result, b"data after retries")
            self.assertEqual(read_attempts[0], 2)
            # Should have used selector for retry
            mock_selector.register.assert_called()
            mock_selector.select.assert_called()

    def test_ssl_want_write_retry_edge_cases(self):
        """Test SSL want write retry edge cases"""
        mock_sock = Mock()

        # Test SSLWantWriteError with multiple retries before success
        write_attempts = [0]  # Use list for mutable reference

        def mock_send(data):
            write_attempts[0] += 1
            if write_attempts[0] == 1:
                raise SSLWantWriteError("The operation did not complete")
            elif write_attempts[0] == 2:
                return len(data)
            else:
                return 0

        mock_sock.send.side_effect = mock_send
        mock_sock.gettimeout.return_value = 30.0

        with patch("selectors.DefaultSelector") as mock_selector_class:
            mock_selector = Mock()
            mock_selector_class.return_value = mock_selector
            mock_selector.select.return_value = [True]  # Always ready

            result = send(mock_sock, b"test data")

            self.assertEqual(result, 9)  # len("test data")
            self.assertEqual(write_attempts[0], 2)

    def test_ssl_eof_error_edge_cases(self):
        """Test SSL EOF error edge cases"""
        mock_sock = Mock()

        # Test SSLEOFError during send
        mock_sock.send.side_effect = SSLEOFError("SSL connection has been closed")
        mock_sock.gettimeout.return_value = 30.0

        from websocket._exceptions import WebSocketConnectionClosedException

        with self.assertRaises(WebSocketConnectionClosedException):
            send(mock_sock, b"test data")

    def test_ssl_pending_data_edge_cases(self):
        """Test SSL pending data scenarios"""
        from websocket._dispatcher import SSLDispatcher
        from websocket._app import WebSocketApp

        # Mock SSL socket with pending data
        mock_ssl_sock = Mock()
        mock_ssl_sock.pending.return_value = 1024  # Simulates pending SSL data

        # Mock WebSocketApp
        mock_app = Mock(spec=WebSocketApp)
        mock_app.sock = Mock()
        mock_app.sock.sock = mock_ssl_sock

        dispatcher = SSLDispatcher(mock_app, 5.0)

        # When there's pending data, should return immediately without selector
        result = dispatcher.select(mock_ssl_sock, Mock())

        # Should return the socket list when there's pending data
        self.assertEqual(result, [mock_ssl_sock])
        mock_ssl_sock.pending.assert_called_once()

    def test_ssl_renegotiation_edge_cases(self):
        """Test SSL renegotiation scenarios"""
        mock_sock = Mock()

        # Simulate SSL renegotiation during read
        call_count = 0

        def mock_recv(bufsize):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
```
