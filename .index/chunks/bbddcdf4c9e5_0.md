# Chunk: bbddcdf4c9e5_0

- source: `.venv-lab/Lib/site-packages/jupyter_lsp/specs/config/typescript-language-server.schema.json`
- lines: 1-21
- chunk: 1/1

```
{
  "title": "TypeScript Language Server Configuration",
  "description": "Based on https://github.com/typescript-language-server/typescript-language-server; TODO: add formatting preferences once formatting is supported.",
  "type": "object",
  "properties": {
    "diagnostics.ignoredCodes": {
      "type": "array",
      "items": {
        "type": "number"
      },
      "default": [],
      "description": "Diagnostics code to be omitted when reporting diagnostics. See https://github.com/microsoft/TypeScript/blob/master/src/compiler/diagnosticMessages.json for a full list of valid codes."
    },
    "completions.completeFunctionCalls": {
      "type": "boolean",
      "default": false,
      "description": "Complete functions with their parameter signature."
    }
  }
}
```
