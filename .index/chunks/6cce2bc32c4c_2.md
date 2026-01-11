# Chunk: 6cce2bc32c4c_2

- source: `.venv-lab/Lib/site-packages/notebook/static/4843.7eed3c5267c10f3eb786.js`
- lines: 132-165
- chunk: 3/3

```
ers), true, true))
      return "keyword";

    if (!!pConfig.operators && pStream.match(wordRegexp(pConfig.operators), true, true))
      return "operator";

    if (!!pConfig.constants && pStream.match(wordRegexp(pConfig.constants), true, true))
      return "variable";

    /* attribute lists */
    if (!pConfig.inAttributeList && !!pConfig.attributes && pStream.match('[', true, true)) {
      pConfig.inAttributeList = true;
      return "bracket";
    }
    if (pConfig.inAttributeList) {
      if (pConfig.attributes !== null && pStream.match(wordRegexpBoundary(pConfig.attributes), true, true)) {
        return "attribute";
      }
      if (pStream.match(']', true, true)) {
        pConfig.inAttributeList = false;
        return "bracket";
      }
    }

    pStream.next();
    return null
  };
}


/***/ })

}]);
//# sourceMappingURL=4843.7eed3c5267c10f3eb786.js.map?v=7eed3c5267c10f3eb786
```
