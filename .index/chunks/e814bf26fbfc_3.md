# Chunk: e814bf26fbfc_3

- source: `.venv-lab/share/jupyter/lab/static/867.e814bf26fbfc77fc4f16.js`
- lines: 1-1
- chunk: 4/4

```
olumn+r.unit}}else if(z(a.token,f)){return a.column+a.token.length}else{n=$(e);return G(n)?n.column+r.unit:0}}function N(e){var t=e.match(/,|[a-z]+|\}|\]|\)|>>|\|+|\(/);return G(t)&&t.index===0?t[0]:""}function O(e){var t=e.tokenStack.slice(0,-1);var r=F(t,"type",["open_paren"]);return G(t[r])?t[r]:false}function $(e){var t=e.tokenStack;var r=F(t,"type",["open_paren","separator","keyword"]);var n=F(t,"type",["operator"]);if(G(r)&&G(n)&&r<n){return t[r+1]}else if(G(r)){return t[r]}else{return false}}function B(e,t){var r=e.tokenStack;var n=F(r,"token",t);return G(r[n])?r[n]:false}function F(e,t,r){for(var n=e.length-1;-1<n;n--){if(z(e[n][t],r)){return n}}return false}function G(e){return e!==false&&e!=null}const H={name:"erlang",startState(){return{tokenStack:[],in_string:false,in_atom:false}},token:g,indent:D,languageData:{commentTokens:{line:"%"}}}}}]);
```
