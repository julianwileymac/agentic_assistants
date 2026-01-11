# Chunk: 65ddeb89aef7_5

- source: `webui/.next/build/chunks/[root-of-the-server]__1359ec9e._.js`
- lines: 372-465
- chunk: 6/7

```
ut', true);
improveConsole('dirxml', 'stdout', true);
improveConsole('timeEnd', 'stdout', true);
improveConsole('timeLog', 'stdout', true);
improveConsole('timeStamp', 'stdout', true);
improveConsole('assert', 'stderr', true);
/**
 * Utility function to ensure all variants of an enum are handled.
 */ function invariant(never, computeMessage) {
    throw new Error(`Invariant: ${computeMessage(never)}`);
}
}),
"[turbopack-node]/ipc/evaluate.ts [postcss] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "run",
    ()=>run
]);
var __TURBOPACK__imported__module__$5b$turbopack$2d$node$5d2f$ipc$2f$index$2e$ts__$5b$postcss$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[turbopack-node]/ipc/index.ts [postcss] (ecmascript)");
;
const ipc = __TURBOPACK__imported__module__$5b$turbopack$2d$node$5d2f$ipc$2f$index$2e$ts__$5b$postcss$5d$__$28$ecmascript$29$__["IPC"];
const queue = [];
const run = async (moduleFactory)=>{
    let nextId = 1;
    const requests = new Map();
    const internalIpc = {
        sendInfo: (message)=>ipc.send({
                type: 'info',
                data: message
            }),
        sendRequest: (message)=>{
            const id = nextId++;
            let resolve, reject;
            const promise = new Promise((res, rej)=>{
                resolve = res;
                reject = rej;
            });
            requests.set(id, {
                resolve,
                reject
            });
            return ipc.send({
                type: 'request',
                id,
                data: message
            }).then(()=>promise);
        },
        sendError: (error)=>{
            return ipc.sendError(error);
        }
    };
    // Initialize module and send ready message
    let getValue;
    try {
        const module = await moduleFactory();
        if (typeof module.init === 'function') {
            await module.init();
        }
        getValue = module.default;
        await ipc.sendReady();
    } catch (err) {
        await ipc.sendReady();
        await ipc.sendError(err);
    }
    // Queue handling
    let isRunning = false;
    const run = async ()=>{
        while(queue.length > 0){
            const args = queue.shift();
            try {
                const value = await getValue(internalIpc, ...args);
                await ipc.send({
                    type: 'end',
                    data: value === undefined ? undefined : JSON.stringify(value, null, 2),
                    duration: 0
                });
            } catch (e) {
                await ipc.sendError(e);
            }
        }
        isRunning = false;
    };
    // Communication handling
    while(true){
        const msg = await ipc.recv();
        switch(msg.type){
            case 'evaluate':
                {
                    queue.push(msg.args);
                    if (!isRunning) {
                        isRunning = true;
                        run();
```
