# Chunk: 7e99c46adabf_1

- source: `.venv-lab/Lib/site-packages/notebook/static/1618.da67fb30732c49b969ba.js`
- lines: 43-161
- chunk: 2/3

```

  var ch = stream.peek()
  if (ch == "/") {
    if (stream.match("//")) {
      stream.skipToEnd()
      return "comment"
    }
    if (stream.match("/*")) {
      state.tokenize.push(tokenComment)
      return tokenComment(stream, state)
    }
  }
  if (stream.match(instruction)) return "builtin"
  if (stream.match(attribute)) return "attribute"
  if (stream.match(binary)) return "number"
  if (stream.match(octal)) return "number"
  if (stream.match(hexadecimal)) return "number"
  if (stream.match(decimal)) return "number"
  if (stream.match(property)) return "property"
  if (operators.indexOf(ch) > -1) {
    stream.next()
    return "operator"
  }
  if (punc.indexOf(ch) > -1) {
    stream.next()
    stream.match("..")
    return "punctuation"
  }
  var stringMatch
  if (stringMatch = stream.match(/("""|"|')/)) {
    var tokenize = tokenString.bind(null, stringMatch[0])
    state.tokenize.push(tokenize)
    return tokenize(stream, state)
  }

  if (stream.match(identifier)) {
    var ident = stream.current()
    if (types.hasOwnProperty(ident)) return "type"
    if (atoms.hasOwnProperty(ident)) return "atom"
    if (keywords.hasOwnProperty(ident)) {
      if (definingKeywords.hasOwnProperty(ident))
        state.prev = "define"
      return "keyword"
    }
    if (prev == "define") return "def"
    return "variable"
  }

  stream.next()
  return null
}

function tokenUntilClosingParen() {
  var depth = 0
  return function(stream, state, prev) {
    var inner = tokenBase(stream, state, prev)
    if (inner == "punctuation") {
      if (stream.current() == "(") ++depth
      else if (stream.current() == ")") {
        if (depth == 0) {
          stream.backUp(1)
          state.tokenize.pop()
          return state.tokenize[state.tokenize.length - 1](stream, state)
        }
        else --depth
      }
    }
    return inner
  }
}

function tokenString(openQuote, stream, state) {
  var singleLine = openQuote.length == 1
  var ch, escaped = false
  while (ch = stream.peek()) {
    if (escaped) {
      stream.next()
      if (ch == "(") {
        state.tokenize.push(tokenUntilClosingParen())
        return "string"
      }
      escaped = false
    } else if (stream.match(openQuote)) {
      state.tokenize.pop()
      return "string"
    } else {
      stream.next()
      escaped = ch == "\\"
    }
  }
  if (singleLine) {
    state.tokenize.pop()
  }
  return "string"
}

function tokenComment(stream, state) {
  var ch
  while (ch = stream.next()) {
    if (ch === "/" && stream.eat("*")) {
      state.tokenize.push(tokenComment)
    } else if (ch === "*" && stream.eat("/")) {
      state.tokenize.pop()
      break
    }
  }
  return "comment"
}

function Context(prev, align, indented) {
  this.prev = prev
  this.align = align
  this.indented = indented
}

function pushContext(state, stream) {
  var align = stream.match(/^\s*($|\/[\/\*]|[)}\]])/, false) ? null : stream.column() + 1
  state.context = new Context(state.context, align, state.indented)
```
