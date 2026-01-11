# Chunk: 37ec0a80dfdb_1

- source: `.venv-lab/Lib/site-packages/websocket/tests/test_ssl_compat.py`
- lines: 71-92
- chunk: 2/2

```
   self.assertIsInstance(ssl_error, Exception)
            self.assertEqual(str(ssl_error), "test error")

            ssl_eof_error = ssl_compat.SSLEOFError("test eof")
            self.assertIsInstance(ssl_eof_error, Exception)

            ssl_want_read = ssl_compat.SSLWantReadError("test read")
            self.assertIsInstance(ssl_want_read, Exception)

            ssl_want_write = ssl_compat.SSLWantWriteError("test write")
            self.assertIsInstance(ssl_want_write, Exception)

    def tearDown(self):
        """Clean up after tests"""
        # Ensure ssl_compat is reimported fresh for next test
        if "websocket._ssl_compat" in sys.modules:
            del sys.modules["websocket._ssl_compat"]


if __name__ == "__main__":
    unittest.main()
```
