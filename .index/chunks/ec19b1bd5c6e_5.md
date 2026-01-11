# Chunk: ec19b1bd5c6e_5

- source: `.venv-lab/Lib/site-packages/notebook/static/2913.274b19d8f201991f4a69.js`
- lines: 360-442
- chunk: 6/104

```
");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/
const nativeExec = RegExp.prototype.exec;
module.exports = nativeExec;
//# sourceMappingURL=native.js.map

/***/ }),

/***/ 5565:
/***/ ((module, __unused_webpack_exports, __webpack_require__) => {


/*!
Copyright 2019 Ron Buckton

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/
/*
 require('foo').getPolyfill or require('foo/polyfill') is a function that when invoked, will return
 the most compliant and performant function that it can - if a native version is available, and does
 not violate the spec, then the native function will be returned - otherwise, either the implementation,
 or a custom, wrapped version of the native function, will be returned. This is also the result that
 will be used as the default export.
 */
const nativeExec = __webpack_require__(55460);
const implementation = __webpack_require__(90425);
function getPolyfill() {
    const re = new RegExp("a");
    const match = nativeExec.call(re, "a");
    if (match.indices) {
        return nativeExec;
    }
    return implementation;
}
module.exports = getPolyfill;
//# sourceMappingURL=polyfill.js.map

/***/ }),

/***/ 37637:
/***/ ((module, __unused_webpack_exports, __webpack_require__) => {


/*!
Copyright 2019 Ron Buckton

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/
/*
 require('foo').shim or require('foo/shim') is a function that when invoked, will call getPolyfill,
 and if the polyfill doesn’t match the built-in value, will install it into the global environment.
 */
```
