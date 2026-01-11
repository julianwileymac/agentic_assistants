# Chunk: b8fbc894ff0b_2

- source: `.venv-lab/Lib/site-packages/terminado-0.18.1.dist-info/METADATA`
- lines: 131-147
- chunk: 3/3

```
    # work, but it will listen on the public network interface as well.
    # Given what terminado does, that would be rather a security hole.
    app.listen(8765, "localhost")
    try:
        tornado.ioloop.IOLoop.instance().start()
    finally:
        term_manager.shutdown()
```

See the [demos
directory](https://github.com/takluyver/terminado/tree/master/demos) for
more examples. This is a simplified version of the `single.py` demo.

Run the unit tests with:

> $ pytest
```
