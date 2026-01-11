# Chunk: ec19b1bd5c6e_4

- source: `.venv-lab/Lib/site-packages/notebook/static/2913.274b19d8f201991f4a69.js`
- lines: 269-368
- chunk: 5/104

```
entGroups && measurementGroups.map(group => group.number),
                groupName: path.node.name
            });
            newGroupNumberForGroup.set(oldGroupNumber, newGroupNumber);
        }
        path.update({ number: newGroupNumber });
    }
};
const backreferenceRenumberer = {
    Backreference(path) {
        const newGroupNumber = newGroupNumberForGroup.get(path.node.number);
        if (newGroupNumber) {
            if (path.node.kind === "number") {
                path.update({
                    number: newGroupNumber,
                    reference: newGroupNumber
                });
            }
            else {
                path.update({
                    number: newGroupNumber
                });
            }
        }
    }
};
function getMeasurementGroups() {
    const measurementGroups = [];
    for (const array of measurementGroupStack) {
        for (const item of array) {
            measurementGroups.push(item);
        }
    }
    return measurementGroups;
}
function transformMeasurementGroups(ast) {
    const result = regexp_tree_1.transform(ast, handlers);
    return new regexp_tree_1.TransformResult(result.getAST(), groupRenumbers);
}
module.exports = exec;
//# sourceMappingURL=implementation.js.map

/***/ }),

/***/ 32913:
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
const implementation = __webpack_require__(90425);
const native = __webpack_require__(55460);
const getPolyfill = __webpack_require__(5565);
const shim = __webpack_require__(37637);
const config = __webpack_require__(93036);
const polyfill = getPolyfill();
function exec(regexp, string) {
    return polyfill.call(regexp, string);
}
exec.implementation = implementation;
exec.native = native;
exec.getPolyfill = getPolyfill;
exec.shim = shim;
exec.config = config;
(function (exec) {
})(exec || (exec = {}));
module.exports = exec;
//# sourceMappingURL=index.js.map

/***/ }),

/***/ 55460:
/***/ ((module) => {


/*!
Copyright 2019 Ron Buckton

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
```
