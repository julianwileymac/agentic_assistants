# Chunk: ddeb8628fe6c_3

- source: `.venv-lab/Lib/site-packages/pip/_vendor/rich/markup.py`
- lines: 238-252
- chunk: 4/4

```
]italic[/italic]",
        "Click [link=https://www.willmcgugan.com]here[/link] to visit my Blog",
        ":warning-emoji: [bold red blink] DANGER![/]",
    ]

    from pip._vendor.rich import print
    from pip._vendor.rich.table import Table

    grid = Table("Markup", "Result", padding=(0, 1))

    for markup in MARKUP:
        grid.add_row(Text(markup), markup)

    print(grid)
```
