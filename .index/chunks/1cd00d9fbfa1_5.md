# Chunk: 1cd00d9fbfa1_5

- source: `.venv-lab/Lib/site-packages/pip/_internal/cli/req_command.py`
- lines: 360-372
- chunk: 6/6

```
e,
            format_control=options.format_control,
            allow_all_prereleases=options.pre,
            prefer_binary=options.prefer_binary,
            ignore_requires_python=ignore_requires_python,
        )

        return PackageFinder.create(
            link_collector=link_collector,
            selection_prefs=selection_prefs,
            target_python=target_python,
        )
```
