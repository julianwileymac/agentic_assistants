# Chunk: 7aaa1bfbe6fa_74

- source: `.venv-lab/Lib/site-packages/notebook/static/306.dd9ffcf982b0c863872b.js.map`
- lines: 1-1
- chunk: 75/75

```
ally\",\n    \"for\", \"function\", \"if\", \"return\", \"switch\", \"throw\", \"try\", \"var\", \"while\", \"with\",\n    \"null\", \"true\", \"false\", \"instanceof\", \"typeof\", \"void\", \"delete\", \"new\", \"in\", \"this\",\n    \"const\", \"class\", \"extends\", \"export\", \"import\", \"super\", \"enum\", \"implements\", \"interface\",\n    \"let\", \"package\", \"private\", \"protected\", \"public\", \"static\", \"yield\", \"require\"];\n/**\nBuild the code that represents the parser tables for a given\ngrammar description. The `parser` property in the return value\nholds the main file that exports the `Parser` instance. The\n`terms` property holds a declaration file that defines constants\nfor all of the named terms in grammar, holding their ids as value.\nThis is useful when external code, such as a tokenizer, needs to\nbe able to use these ids. It is recommended to run a tree-shaking\nbundler when importing this file, since you usually only need a\nhandful of the many terms in your code.\n*/\nfunction buildParserFile(text, options = {}) {\n    return new Builder(text, options).getParserFile();\n}\nfunction ignored(name) {\n    let first = name[0];\n    return first == \"_\" || first.toUpperCase() != first;\n}\nfunction isExported(rule) {\n    return rule.props.some(p => p.at && p.name == \"export\");\n}\n\nexport { GenError, buildParser, buildParserFile };\n"],"names":[],"sourceRoot":""}
```
