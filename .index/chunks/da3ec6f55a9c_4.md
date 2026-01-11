# Chunk: da3ec6f55a9c_4

- source: `.venv-lab/Lib/site-packages/notebook/static/4002.7d2089cf976c84095255.js`
- lines: 129-175
- chunk: 5/7

```
"vary-meta", "vec", "vector", "vector-of",
                   "vector?", "volatile!", "volatile?", "vreset!", "vswap!", "when",
                   "when-first", "when-let", "when-not", "when-some", "while",
                   "with-bindings", "with-bindings*", "with-in-str", "with-loading-context",
                   "with-local-vars", "with-meta", "with-open", "with-out-str",
                   "with-precision", "with-redefs", "with-redefs-fn", "xml-seq", "zero?",
                   "zipmap"];
var haveBodyParameter = [
  "->", "->>", "as->", "binding", "bound-fn", "case", "catch", "comment",
  "cond", "cond->", "cond->>", "condp", "def", "definterface", "defmethod",
  "defn", "defmacro", "defprotocol", "defrecord", "defstruct", "deftype",
  "do", "doseq", "dotimes", "doto", "extend", "extend-protocol",
  "extend-type", "fn", "for", "future", "if", "if-let", "if-not", "if-some",
  "let", "letfn", "locking", "loop", "ns", "proxy", "reify", "struct-map",
  "some->", "some->>", "try", "when", "when-first", "when-let", "when-not",
  "when-some", "while", "with-bindings", "with-bindings*", "with-in-str",
  "with-loading-context", "with-local-vars", "with-meta", "with-open",
  "with-out-str", "with-precision", "with-redefs", "with-redefs-fn"];

var atom = createLookupMap(atoms);
var specialForm = createLookupMap(specialForms);
var coreSymbol = createLookupMap(coreSymbols);
var hasBodyParameter = createLookupMap(haveBodyParameter);
var delimiter = /^(?:[\\\[\]\s"(),;@^`{}~]|$)/;
var numberLiteral = /^(?:[+\-]?\d+(?:(?:N|(?:[eE][+\-]?\d+))|(?:\.?\d*(?:M|(?:[eE][+\-]?\d+))?)|\/\d+|[xX][0-9a-fA-F]+|r[0-9a-zA-Z]+)?(?=[\\\[\]\s"#'(),;@^`{}~]|$))/;
var characterLiteral = /^(?:\\(?:backspace|formfeed|newline|return|space|tab|o[0-7]{3}|u[0-9A-Fa-f]{4}|x[0-9A-Fa-f]{4}|.)?(?=[\\\[\]\s"(),;@^`{}~]|$))/;

// simple-namespace := /^[^\\\/\[\]\d\s"#'(),;@^`{}~.][^\\\[\]\s"(),;@^`{}~.\/]*/
// simple-symbol    := /^(?:\/|[^\\\/\[\]\d\s"#'(),;@^`{}~][^\\\[\]\s"(),;@^`{}~]*)/
// qualified-symbol := (<simple-namespace>(<.><simple-namespace>)*</>)?<simple-symbol>
var qualifiedSymbol = /^(?:(?:[^\\\/\[\]\d\s"#'(),;@^`{}~.][^\\\[\]\s"(),;@^`{}~.\/]*(?:\.[^\\\/\[\]\d\s"#'(),;@^`{}~.][^\\\[\]\s"(),;@^`{}~.\/]*)*\/)?(?:\/|[^\\\/\[\]\d\s"#'(),;@^`{}~][^\\\[\]\s"(),;@^`{}~]*)*(?=[\\\[\]\s"(),;@^`{}~]|$))/;

function base(stream, state) {
  if (stream.eatSpace() || stream.eat(",")) return ["space", null];
  if (stream.match(numberLiteral)) return [null, "number"];
  if (stream.match(characterLiteral)) return [null, "string.special"];
  if (stream.eat(/^"/)) return (state.tokenize = inString)(stream, state);
  if (stream.eat(/^[(\[{]/)) return ["open", "bracket"];
  if (stream.eat(/^[)\]}]/)) return ["close", "bracket"];
  if (stream.eat(/^;/)) {stream.skipToEnd(); return ["space", "comment"];}
  if (stream.eat(/^[#'@^`~]/)) return [null, "meta"];

  var matches = stream.match(qualifiedSymbol);
  var symbol = matches && matches[0];

  if (!symbol) {
```
