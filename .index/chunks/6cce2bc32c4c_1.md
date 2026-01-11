# Chunk: 6cce2bc32c4c_1

- source: `.venv-lab/Lib/site-packages/notebook/static/4843.7eed3c5267c10f3eb786.js`
- lines: 53-142
- chunk: 2/3

```
lour", "textbgcolor", "textbgcolour", "arclinecolor", "arclinecolour", "arctextcolor", "arctextcolour", "arctextbgcolor", "arctextbgcolour", "arcskip", "title", "deactivate", "activate", "activation"],
  "brackets" : ["\\{", "\\}"],  // [ and  ] are brackets too, but these get handled in with lists
  "arcsWords" : ["note", "abox", "rbox", "box", "alt", "else", "opt", "break", "par", "seq", "strict", "neg", "critical", "ignore", "consider", "assert", "loop", "ref", "exc"],
  "arcsOthers" : ["\\|\\|\\|", "\\.\\.\\.", "---", "--", "<->", "==", "<<=>>", "<=>", "\\.\\.", "<<>>", "::", "<:>", "->", "=>>", "=>", ">>", ":>", "<-", "<<=", "<=", "<<", "<:", "x-", "-x"],
  "singlecomment" : ["//", "#"],
  "operators" : ["="]
})

function wordRegexpBoundary(pWords) {
  return new RegExp("^\\b(" + pWords.join("|") + ")\\b", "i");
}

function wordRegexp(pWords) {
  return new RegExp("^(?:" + pWords.join("|") + ")", "i");
}

function startStateFn() {
  return {
    inComment : false,
    inString : false,
    inAttributeList : false,
    inScript : false
  };
}

function copyStateFn(pState) {
  return {
    inComment : pState.inComment,
    inString : pState.inString,
    inAttributeList : pState.inAttributeList,
    inScript : pState.inScript
  };
}

function produceTokenFunction(pConfig) {
  return function(pStream, pState) {
    if (pStream.match(wordRegexp(pConfig.brackets), true, true)) {
      return "bracket";
    }
    /* comments */
    if (!pState.inComment) {
      if (pStream.match(/\/\*[^\*\/]*/, true, true)) {
        pState.inComment = true;
        return "comment";
      }
      if (pStream.match(wordRegexp(pConfig.singlecomment), true, true)) {
        pStream.skipToEnd();
        return "comment";
      }
    }
    if (pState.inComment) {
      if (pStream.match(/[^\*\/]*\*\//, true, true))
        pState.inComment = false;
      else
        pStream.skipToEnd();
      return "comment";
    }
    /* strings */
    if (!pState.inString && pStream.match(/\"(\\\"|[^\"])*/, true, true)) {
      pState.inString = true;
      return "string";
    }
    if (pState.inString) {
      if (pStream.match(/[^\"]*\"/, true, true))
        pState.inString = false;
      else
        pStream.skipToEnd();
      return "string";
    }
    /* keywords & operators */
    if (!!pConfig.keywords && pStream.match(wordRegexpBoundary(pConfig.keywords), true, true))
      return "keyword";

    if (pStream.match(wordRegexpBoundary(pConfig.options), true, true))
      return "keyword";

    if (pStream.match(wordRegexpBoundary(pConfig.arcsWords), true, true))
      return "keyword";

    if (pStream.match(wordRegexp(pConfig.arcsOthers), true, true))
      return "keyword";

    if (!!pConfig.operators && pStream.match(wordRegexp(pConfig.operators), true, true))
      return "operator";

    if (!!pConfig.constants && pStream.match(wordRegexp(pConfig.constants), true, true))
      return "variable";

    /* attribute lists */
```
