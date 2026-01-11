# Chunk: 9e6ffdd02af2_1

- source: `.venv-lab/Lib/site-packages/mistune/__main__.py`
- lines: 112-136
- chunk: 2/2

```

        text = md(message)
        assert isinstance(text, str)
        _output(text, args)
    elif args.file:
        md = _md(args)
        text = md.read(args.file)[0]
        assert isinstance(text, str)
        _output(text, args)
    else:
        print("You MUST specify a message or file")
        sys.exit(1)


def read_stdin() -> Optional[str]:
    is_stdin_pipe = not sys.stdin.isatty()
    if is_stdin_pipe:
        return sys.stdin.read()
    else:
        return None


if __name__ == "__main__":
    cli()
```
