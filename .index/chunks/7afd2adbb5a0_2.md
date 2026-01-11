# Chunk: 7afd2adbb5a0_2

- source: `.venv-lab/Lib/site-packages/notebook/static/3562.3b759e4fdd798f9dca94.js`
- lines: 96-187
- chunk: 3/3

```
ound", "umask", "unlink",
                      "unpack", "verify", "xor", "zabs", "zcos", "zexp",
                      "zlog", "zsin", "zsqrt"]);

var dataTypes =  words(["c_bool", "c_char", "c_double", "c_double_complex",
                        "c_float", "c_float_complex", "c_funptr", "c_int",
                        "c_int16_t", "c_int32_t", "c_int64_t", "c_int8_t",
                        "c_int_fast16_t", "c_int_fast32_t", "c_int_fast64_t",
                        "c_int_fast8_t", "c_int_least16_t", "c_int_least32_t",
                        "c_int_least64_t", "c_int_least8_t", "c_intmax_t",
                        "c_intptr_t", "c_long", "c_long_double",
                        "c_long_double_complex", "c_long_long", "c_ptr",
                        "c_short", "c_signed_char", "c_size_t", "character",
                        "complex", "double", "integer", "logical", "real"]);
var isOperatorChar = /[+\-*&=<>\/\:]/;
var litOperator = /^\.(and|or|eq|lt|le|gt|ge|ne|not|eqv|neqv)\./i;

function tokenBase(stream, state) {

  if (stream.match(litOperator)){
    return 'operator';
  }

  var ch = stream.next();
  if (ch == "!") {
    stream.skipToEnd();
    return "comment";
  }
  if (ch == '"' || ch == "'") {
    state.tokenize = tokenString(ch);
    return state.tokenize(stream, state);
  }
  if (/[\[\]\(\),]/.test(ch)) {
    return null;
  }
  if (/\d/.test(ch)) {
    stream.eatWhile(/[\w\.]/);
    return "number";
  }
  if (isOperatorChar.test(ch)) {
    stream.eatWhile(isOperatorChar);
    return "operator";
  }
  stream.eatWhile(/[\w\$_]/);
  var word = stream.current().toLowerCase();

  if (keywords.hasOwnProperty(word)){
    return 'keyword';
  }
  if (builtins.hasOwnProperty(word) || dataTypes.hasOwnProperty(word)) {
    return 'builtin';
  }
  return "variable";
}

function tokenString(quote) {
  return function(stream, state) {
    var escaped = false, next, end = false;
    while ((next = stream.next()) != null) {
      if (next == quote && !escaped) {
        end = true;
        break;
      }
      escaped = !escaped && next == "\\";
    }
    if (end || !escaped) state.tokenize = null;
    return "string";
  };
}

// Interface

const fortran = {
  name: "fortran",
  startState: function() {
    return {tokenize: null};
  },

  token: function(stream, state) {
    if (stream.eatSpace()) return null;
    var style = (state.tokenize || tokenBase)(stream, state);
    if (style == "comment" || style == "meta") return style;
    return style;
  }
};



/***/ })

}]);
//# sourceMappingURL=3562.3b759e4fdd798f9dca94.js.map?v=3b759e4fdd798f9dca94
```
