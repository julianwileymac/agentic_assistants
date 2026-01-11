# Chunk: 65ddeb89aef7_1

- source: `webui/.next/build/chunks/[root-of-the-server]__1359ec9e._.js`
- lines: 85-180
- chunk: 2/7

```
r[3]);
    if (a && l != null) {
        r[3] = l[1];
        r[4] = l[2];
        r[5] = null;
    }
    return {
        file: r[3],
        methodName: r[1] || n,
        arguments: r[2] ? r[2].split(",") : [],
        lineNumber: r[4] ? +r[4] : null,
        column: r[5] ? +r[5] : null
    };
}
var s = /^\s*(?:([^@]*)(?:\((.*?)\))?@)?(\S.*?):(\d+)(?::(\d+))?\s*$/i;
function parseJSC(e) {
    var r = s.exec(e);
    if (!r) {
        return null;
    }
    return {
        file: r[3],
        methodName: r[1] || n,
        arguments: [],
        lineNumber: +r[4],
        column: r[5] ? +r[5] : null
    };
}
var o = /^\s*at (?:((?:\[object object\])?[^\\/]+(?: \[as \S+\])?) )?\(?(.*?):(\d+)(?::(\d+))?\)?\s*$/i;
function parseNode(e) {
    var r = o.exec(e);
    if (!r) {
        return null;
    }
    return {
        file: r[2],
        methodName: r[1] || n,
        arguments: [],
        lineNumber: +r[3],
        column: r[4] ? +r[4] : null
    };
}
}),
"[turbopack-node]/ipc/error.ts [postcss] (ecmascript)", ((__turbopack_context__) => {
"use strict";

// merged from next.js
// https://github.com/vercel/next.js/blob/e657741b9908cf0044aaef959c0c4defb19ed6d8/packages/next/src/lib/is-error.ts
// https://github.com/vercel/next.js/blob/e657741b9908cf0044aaef959c0c4defb19ed6d8/packages/next/src/shared/lib/is-plain-object.ts
__turbopack_context__.s([
    "default",
    ()=>isError,
    "getProperError",
    ()=>getProperError
]);
function isError(err) {
    return typeof err === 'object' && err !== null && 'name' in err && 'message' in err;
}
function getProperError(err) {
    if (isError(err)) {
        return err;
    }
    if ("TURBOPACK compile-time falsy", 0) //TURBOPACK unreachable
    ;
    return new Error(isPlainObject(err) ? JSON.stringify(err) : err + '');
}
function getObjectClassLabel(value) {
    return Object.prototype.toString.call(value);
}
function isPlainObject(value) {
    if (getObjectClassLabel(value) !== '[object Object]') {
        return false;
    }
    const prototype = Object.getPrototypeOf(value);
    /**
   * this used to be previously:
   *
   * `return prototype === null || prototype === Object.prototype`
   *
   * but Edge Runtime expose Object from vm, being that kind of type-checking wrongly fail.
   *
   * It was changed to the current implementation since it's resilient to serialization.
   */ return prototype === null || prototype.hasOwnProperty('isPrototypeOf');
}
}),
"[turbopack-node]/ipc/index.ts [postcss] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "IPC",
    ()=>IPC,
    "structuredError",
    ()=>structuredError
]);
var __TURBOPACK__imported__module__$5b$externals$5d2f$node$3a$net__$5b$external$5d$__$28$node$3a$net$2c$__cjs$29$__ = __turbopack_context__.i("[externals]/node:net [external] (node:net, cjs)");
```
