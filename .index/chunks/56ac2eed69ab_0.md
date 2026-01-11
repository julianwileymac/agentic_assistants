# Chunk: 56ac2eed69ab_0

- source: `.venv-lab/Lib/site-packages/notebook/static/3211.2e93fd406e5c4e53774f.js`
- lines: 1-83
- chunk: 1/3

```
"use strict";
(self["webpackChunk_JUPYTERLAB_CORE_OUTPUT"] = self["webpackChunk_JUPYTERLAB_CORE_OUTPUT"] || []).push([[3211],{

/***/ 3211:
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   liveScript: () => (/* binding */ liveScript)
/* harmony export */ });
var tokenBase = function(stream, state) {
  var next_rule = state.next || "start";
  if (next_rule) {
    state.next = state.next;
    var nr = Rules[next_rule];
    if (nr.splice) {
      for (var i$ = 0; i$ < nr.length; ++i$) {
        var r = nr[i$];
        if (r.regex && stream.match(r.regex)) {
          state.next = r.next || state.next;
          return r.token;
        }
      }
      stream.next();
      return 'error';
    }
    if (stream.match(r = Rules[next_rule])) {
      if (r.regex && stream.match(r.regex)) {
        state.next = r.next;
        return r.token;
      } else {
        stream.next();
        return 'error';
      }
    }
  }
  stream.next();
  return 'error';
};

var identifier = '(?![\\d\\s])[$\\w\\xAA-\\uFFDC](?:(?!\\s)[$\\w\\xAA-\\uFFDC]|-[A-Za-z])*';
var indenter = RegExp('(?:[({[=:]|[-~]>|\\b(?:e(?:lse|xport)|d(?:o|efault)|t(?:ry|hen)|finally|import(?:\\s*all)?|const|var|let|new|catch(?:\\s*' + identifier + ')?))\\s*$');
var keywordend = '(?![$\\w]|-[A-Za-z]|\\s*:(?![:=]))';
var stringfill = {
  token: 'string',
  regex: '.+'
};
var Rules = {
  start: [
    {
      token: 'docComment',
      regex: '/\\*',
      next: 'comment'
    }, {
      token: 'comment',
      regex: '#.*'
    }, {
      token: 'keyword',
      regex: '(?:t(?:h(?:is|row|en)|ry|ypeof!?)|c(?:on(?:tinue|st)|a(?:se|tch)|lass)|i(?:n(?:stanceof)?|mp(?:ort(?:\\s+all)?|lements)|[fs])|d(?:e(?:fault|lete|bugger)|o)|f(?:or(?:\\s+own)?|inally|unction)|s(?:uper|witch)|e(?:lse|x(?:tends|port)|val)|a(?:nd|rguments)|n(?:ew|ot)|un(?:less|til)|w(?:hile|ith)|o[fr]|return|break|let|var|loop)' + keywordend
    }, {
      token: 'atom',
      regex: '(?:true|false|yes|no|on|off|null|void|undefined)' + keywordend
    }, {
      token: 'invalid',
      regex: '(?:p(?:ackage|r(?:ivate|otected)|ublic)|i(?:mplements|nterface)|enum|static|yield)' + keywordend
    }, {
      token: 'className.standard',
      regex: '(?:R(?:e(?:gExp|ferenceError)|angeError)|S(?:tring|yntaxError)|E(?:rror|valError)|Array|Boolean|Date|Function|Number|Object|TypeError|URIError)' + keywordend
    }, {
      token: 'variableName.function.standard',
      regex: '(?:is(?:NaN|Finite)|parse(?:Int|Float)|Math|JSON|(?:en|de)codeURI(?:Component)?)' + keywordend
    }, {
      token: 'variableName.standard',
      regex: '(?:t(?:hat|il|o)|f(?:rom|allthrough)|it|by|e)' + keywordend
    }, {
      token: 'variableName',
      regex: identifier + '\\s*:(?![:=])'
    }, {
      token: 'variableName',
      regex: identifier
    }, {
      token: 'operatorKeyword',
```
