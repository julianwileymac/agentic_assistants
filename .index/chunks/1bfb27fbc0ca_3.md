# Chunk: 1bfb27fbc0ca_3

- source: `.venv-lab/Lib/site-packages/pip/_vendor/rich/highlighter.py`
- lines: 194-233
- chunk: 4/4

```
:(?P<minute>[0-5][0-9]):(?P<second>[0-5][0-9])(?P<frac>\.[0-9]+)?)(?P<timezone>Z|[+-](?:2[0-3]|[01][0-9]):[0-5][0-9])?$",
        # Date and time, with optional fractional seconds and time zone (e.g., 2008-08-30T01:45:36 or 2008-08-30T01:45:36.123Z).
        # This is the XML Schema 'dateTime' type
        r"^(?P<date>(?P<year>-?(?:[1-9][0-9]*)?[0-9]{4})-(?P<month>1[0-2]|0[1-9])-(?P<day>3[01]|0[1-9]|[12][0-9]))T(?P<time>(?P<hour>2[0-3]|[01][0-9]):(?P<minute>[0-5][0-9]):(?P<second>[0-5][0-9])(?P<ms>\.[0-9]+)?)(?P<timezone>Z|[+-](?:2[0-3]|[01][0-9]):[0-5][0-9])?$",
    ]


if __name__ == "__main__":  # pragma: no cover
    from .console import Console

    console = Console()
    console.print("[bold green]hello world![/bold green]")
    console.print("'[bold green]hello world![/bold green]'")

    console.print(" /foo")
    console.print("/foo/")
    console.print("/foo/bar")
    console.print("foo/bar/baz")

    console.print("/foo/bar/baz?foo=bar+egg&egg=baz")
    console.print("/foo/bar/baz/")
    console.print("/foo/bar/baz/egg")
    console.print("/foo/bar/baz/egg.py")
    console.print("/foo/bar/baz/egg.py word")
    console.print(" /foo/bar/baz/egg.py word")
    console.print("foo /foo/bar/baz/egg.py word")
    console.print("foo /foo/bar/ba._++z/egg+.py word")
    console.print("https://example.org?foo=bar#header")

    console.print(1234567.34)
    console.print(1 / 2)
    console.print(-1 / 123123123123)

    console.print(
        "127.0.1.1 bar 192.168.1.4 2001:0db8:85a3:0000:0000:8a2e:0370:7334 foo"
    )
    import json

    console.print_json(json.dumps(obj={"name": "apple", "count": 1}), indent=None)
```
