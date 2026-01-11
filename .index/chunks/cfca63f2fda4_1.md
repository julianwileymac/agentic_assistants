# Chunk: cfca63f2fda4_1

- source: `.venv-lab/Lib/site-packages/notebook/static/9676.0476942dc748eb1854c5.js`
- lines: 58-155
- chunk: 2/2

```
== Location.POST_OBJ
           )
         ) ret = currLocation;

  // Reset.
  else if(currLocation == Location.POST_OBJ && c == '.') ret = Location.PRE_SUBJECT;

  // Error
  else ret = Location.ERROR;

  currState.location=ret;
}

const ntriples = {
  name: "ntriples",
  startState: function() {
    return {
      location : Location.PRE_SUBJECT,
      uris     : [],
      anchors  : [],
      bnodes   : [],
      langs    : [],
      types    : []
    };
  },
  token: function(stream, state) {
    var ch = stream.next();
    if(ch == '<') {
      transitState(state, ch);
      var parsedURI = '';
      stream.eatWhile( function(c) { if( c != '#' && c != '>' ) { parsedURI += c; return true; } return false;} );
      state.uris.push(parsedURI);
      if( stream.match('#', false) ) return 'variable';
      stream.next();
      transitState(state, '>');
      return 'variable';
    }
    if(ch == '#') {
      var parsedAnchor = '';
      stream.eatWhile(function(c) { if(c != '>' && c != ' ') { parsedAnchor+= c; return true; } return false;});
      state.anchors.push(parsedAnchor);
      return 'url';
    }
    if(ch == '>') {
      transitState(state, '>');
      return 'variable';
    }
    if(ch == '_') {
      transitState(state, ch);
      var parsedBNode = '';
      stream.eatWhile(function(c) { if( c != ' ' ) { parsedBNode += c; return true; } return false;});
      state.bnodes.push(parsedBNode);
      stream.next();
      transitState(state, ' ');
      return 'builtin';
    }
    if(ch == '"') {
      transitState(state, ch);
      stream.eatWhile( function(c) { return c != '"'; } );
      stream.next();
      if( stream.peek() != '@' && stream.peek() != '^' ) {
        transitState(state, '"');
      }
      return 'string';
    }
    if( ch == '@' ) {
      transitState(state, '@');
      var parsedLang = '';
      stream.eatWhile(function(c) { if( c != ' ' ) { parsedLang += c; return true; } return false;});
      state.langs.push(parsedLang);
      stream.next();
      transitState(state, ' ');
      return 'string.special';
    }
    if( ch == '^' ) {
      stream.next();
      transitState(state, '^');
      var parsedType = '';
      stream.eatWhile(function(c) { if( c != '>' ) { parsedType += c; return true; } return false;} );
      state.types.push(parsedType);
      stream.next();
      transitState(state, '>');
      return 'variable';
    }
    if( ch == ' ' ) {
      transitState(state, ch);
    }
    if( ch == '.' ) {
      transitState(state, ch);
    }
  }
};


/***/ })

}]);
//# sourceMappingURL=9676.0476942dc748eb1854c5.js.map?v=0476942dc748eb1854c5
```
