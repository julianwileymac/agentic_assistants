# Chunk: bd7961effef1_1

- source: `.venv-lab/Lib/site-packages/jupyter_lsp/specs/config/julia-language-server.schema.json`
- lines: 58-89
- chunk: 2/2

```
where` statements or datatype declarations are used."
    },
    "julia.lint.modname": {
      "type": "boolean",
      "default": true,
      "description": "Check submodule names do not shadow their parent's name."
    },
    "julia.lint.pirates": {
      "type": "boolean",
      "default": true,
      "description": "Check for type piracy - the overloading of external functions with methods specified for external datatypes. 'External' here refers to imported code."
    },
    "julia.lint.useoffuncargs": {
      "type": "boolean",
      "default": true,
      "description": "Check that all declared arguments are used within the function body."
    },
    "julia.completionmode": {
      "type": "string",
      "default": "qualify",
      "description": "Sets the mode for completions.",
      "enum": ["exportedonly", "import", "qualify"],
      "enumDescriptions": [
        "Show completions for the current namespace.",
        "Show completions for the current namespace and unexported variables of `using`ed modules. Selection of an unexported variable will result in the automatic insertion of an explicit `using` statement.",
        "Show completions for the current namespace and unexported variables of `using`ed modules. Selection of an unexported variable will complete to a qualified variable name."
      ],
      "scope": "window"
    }
  }
}
```
