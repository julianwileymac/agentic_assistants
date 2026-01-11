# Chunk: dabcc3c9658b_1

- source: `.venv-lab/share/jupyter/lab/static/6843.dabcc3c9658bc6ded6d1.js`
- lines: 1-1
- chunk: 2/2

```
|l.context.name!="!cdata")h("!cdata");if(l.tokenize==u)g();return d()}else return d()}function m(e){return function(t){if(t=="selfclosePlugin"||t=="endPlugin")return d();if(t=="endPlugin"){h(l.pluginName,e);return d()}return d()}}function x(e){return function(t){if(e)k="error";if(t=="endPlugin")return d();return p()}}function v(e){if(e=="keyword"){k="attribute";return d(v)}if(e=="equals")return d(w,v);return p()}function w(e){if(e=="keyword"){k="string";return d()}if(e=="string")return d(z);return p()}function z(e){if(e=="string")return d(z);else return p()}const _={name:"tiki",startState:function(){return{tokenize:u,cc:[],indented:0,startOfLine:true,pluginName:null,context:null}},token:function(e,t){if(e.sol()){t.startOfLine=true;t.indented=e.indentation()}if(e.eatSpace())return null;k=o=a=null;var n=t.tokenize(e,t);if((n||o)&&n!="comment"){l=t;while(true){var r=t.cc.pop()||b;if(r(o||n))break}}t.startOfLine=false;return k||n},indent:function(e,t,n){var r=e.context;if(r&&r.noIndent)return 0;if(r&&/^{\//.test(t))r=r.prev;while(r&&!r.startOfLine)r=r.prev;if(r)return r.indent+n.unit;else return 0}}}}]);
```
