# Chunk: ebdf8da40f1b_3

- source: `.venv-lab/share/jupyter/lab/static/6412.ebdf8da40f1ba8272df9.js`
- lines: 1-1
- chunk: 4/4

```
 i.indented+(u?0:r.unit)},languageData:{indentOnInput:/^\s*[{}]$/,commentTokens:{line:"//",block:{open:"/*",close:"*/"}}}};const le={name:"hxml",startState:function(){return{define:false,inString:false}},token:function(e,t){var r=e.peek();var n=e.sol();if(r=="#"){e.skipToEnd();return"comment"}if(n&&r=="-"){var i="variable-2";e.eat(/-/);if(e.peek()=="-"){e.eat(/-/);i="keyword a"}if(e.peek()=="D"){e.eat(/[D]/);i="keyword c";t.define=true}e.eatWhile(/[A-Z]/i);return i}var r=e.peek();if(t.inString==false&&r=="'"){t.inString=true;e.next()}if(t.inString==true){if(e.skipTo("'")){}else{e.skipToEnd()}if(e.peek()=="'"){e.next();t.inString=false}return"string"}e.next();return null},languageData:{commentTokens:{line:"#"}}}}}]);
```
