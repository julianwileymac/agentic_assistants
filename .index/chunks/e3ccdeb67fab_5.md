# Chunk: e3ccdeb67fab_5

- source: `.venv-lab/Lib/site-packages/notebook/static/9250.a4dfe77db702bf7a316c.js`
- lines: 251-290
- chunk: 6/6

```
tream.match(/^[+-]?0x[0-9a-fA-F]+/))
      return 'number';
    if (stream.match(/^[+-]?\d*\.\d+([EeDd][+-]?\d+)?/))
      return 'number';
    if (stream.match(/^[+-]?\d+([EeDd][+-]?\d+)?/))
      return 'number';
  }

  // Handle Strings
  if (stream.match(/^"([^"]|(""))*"/)) { return 'string'; }
  if (stream.match(/^'([^']|(''))*'/)) { return 'string'; }

  // Handle words
  if (stream.match(keywords)) { return 'keyword'; }
  if (stream.match(builtins)) { return 'builtin'; }
  if (stream.match(identifiers)) { return 'variable'; }

  if (stream.match(singleOperators) || stream.match(boolOperators)) {
    return 'operator'; }

  // Handle non-detected items
  stream.next();
  return null;
};

const idl = {
  name: "idl",
  token: function(stream) {
    return tokenBase(stream);
  },
  languageData: {
    autocomplete: builtinArray.concat(keywordArray)
  }
}


/***/ })

}]);
//# sourceMappingURL=9250.a4dfe77db702bf7a316c.js.map?v=a4dfe77db702bf7a316c
```
