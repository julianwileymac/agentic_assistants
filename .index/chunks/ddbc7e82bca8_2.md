# Chunk: ddbc7e82bca8_2

- source: `.venv-lab/Lib/site-packages/pip/_vendor/packaging/licenses/__init__.py`
- lines: 135-146
- chunk: 3/3

```
en not in LICENSES:
                    message = f"Unknown license: {final_token!r}"
                    raise InvalidLicenseExpression(message)
                normalized_tokens.append(LICENSES[final_token]["id"] + suffix)

    normalized_expression = " ".join(normalized_tokens)

    return cast(
        NormalizedLicenseExpression,
        normalized_expression.replace("( ", "(").replace(" )", ")"),
    )
```
