# Chunk: ec19b1bd5c6e_0

- source: `.venv-lab/Lib/site-packages/notebook/static/2913.274b19d8f201991f4a69.js`
- lines: 1-81
- chunk: 1/104

```
"use strict";
(self["webpackChunk_JUPYTERLAB_CORE_OUTPUT"] = self["webpackChunk_JUPYTERLAB_CORE_OUTPUT"] || []).push([[2913],{

/***/ 93036:
/***/ ((module) => {


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
const config = {
    mode: "lazy"
};
module.exports = config;
//# sourceMappingURL=config.js.map

/***/ }),

/***/ 90425:
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
 require('foo').implementation or require('foo/implementation') is a spec-compliant JS function,
 that will depend on a receiver (a “this” value) as the spec requires.
 */
const config = __webpack_require__(93036);
const nativeExec = __webpack_require__(55460);
const regexp_tree_1 = __webpack_require__(3661);
const weakMeasurementRegExp = new WeakMap();
function exec(string) {
    return config.mode === "spec-compliant"
        ? execSpecCompliant(this, string)
        : execLazy(this, string);
}
function execLazy(regexp, string) {
    const index = regexp.lastIndex;
    const result = nativeExec.call(regexp, string);
    if (result === null)
        return null;
    // For performance reasons, we defer computing the indices until later. This isn't spec compliant,
    // but once we compute the indices we convert the result to a data-property.
    let indicesArray;
    Object.defineProperty(result, "indices", {
        enumerable: true,
        configurable: true,
        get() {
            if (indicesArray === undefined) {
                const { measurementRegExp, groupInfos } = getMeasurementRegExp(regexp);
                measurementRegExp.lastIndex = index;
                const measuredResult = nativeExec.call(measurementRegExp, string);
                if (measuredResult === null)
                    throw new TypeError();
```
