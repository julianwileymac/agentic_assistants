# Chunk: 83e78dadcef8_1

- source: `.venv-lab/share/jupyter/lab/static/5211.83e78dadcef89cae04bf.js`
- lines: 1-1
- chunk: 2/2

```
rn e.replace(/\./g," ");var t=[];for(var n=0;n<e.length;n++)t.push(e[n]&&e[n].replace(/\./g," "));return t}function o(e,t){if(e.next||e.push)a(t,e.next||e.push);this.regex=i(e.regex);this.token=s(e.token);this.data=e}function g(e){return function(t,n){if(n.pending){var r=n.pending.shift();if(n.pending.length==0)n.pending=null;t.pos+=r.text.length;return r.token}var a=e[n.state];for(var i=0;i<a.length;i++){var s=a[i];var o=(!s.data.sol||t.sol())&&t.match(s.regex);if(o){if(s.data.next){n.state=s.data.next}else if(s.data.push){(n.stack||(n.stack=[])).push(n.state);n.state=s.data.push}else if(s.data.pop&&n.stack&&n.stack.length){n.state=n.stack.pop()}if(s.data.indent)n.indent.push(t.indentation()+t.indentUnit);if(s.data.dedent)n.indent.pop();var g=s.token;if(g&&g.apply)g=g(o);if(o.length>2&&s.token&&typeof s.token!="string"){n.pending=[];for(var l=2;l<o.length;l++)if(o[l])n.pending.push({text:o[l],token:s.token[l-1]});t.backUp(o[0].length-(o[1]?o[1].length:0));return g[0]}else if(g&&g.join){return g[0]}else{return g}}}t.next();return null}}function l(e,t){return function(n,r){if(n.indent==null||t.dontIndentStates&&t.dontIndentStates.indexOf(n.state)>-1)return null;var a=n.indent.length-1,i=e[n.state];e:for(;;){for(var s=0;s<i.length;s++){var o=i[s];if(o.data.dedent&&o.data.dedentIfLineStart!==false){var g=o.regex.exec(r);if(g&&g[0]){a--;if(o.next||o.push)i=e[o.next||o.push];r=r.slice(g[0].length);continue e}}}break}return a<0?0:n.indent[a]}}}}]);
```
