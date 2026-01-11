# Chunk: ec19b1bd5c6e_2

- source: `.venv-lab/Lib/site-packages/notebook/static/2913.274b19d8f201991f4a69.js`
- lines: 132-214
- chunk: 3/104

```
asuredResult[measurementGroup].length;
                }
            }
            const endIndex = startIndex + measuredResult[groupInfo.newGroupNumber].length;
            indices = [startIndex, endIndex];
        }
        makeDataProperty(indicesArray, groupInfo.oldGroupNumber, indices);
        if (groups && groupInfo.groupName !== undefined) {
            makeDataProperty(groups, groupInfo.groupName, indices);
        }
    }
    makeDataProperty(indicesArray, "groups", groups);
    return indicesArray;
}
function makeDataProperty(result, key, value) {
    const existingDesc = Object.getOwnPropertyDescriptor(result, key);
    if (existingDesc ? existingDesc.configurable : Object.isExtensible(result)) {
        const newDesc = {
            enumerable: existingDesc ? existingDesc.enumerable : true,
            configurable: existingDesc ? existingDesc.configurable : true,
            writable: true,
            value
        };
        Object.defineProperty(result, key, newDesc);
    }
}
let groupRenumbers;
let hasBackreferences = false;
let nodesContainingCapturingGroup = new Set();
let containsCapturingGroupStack = [];
let containsCapturingGroup = false;
let nextNewGroupNumber = 1;
let measurementGroupStack = [];
let measurementGroupsForGroup = new Map();
let newGroupNumberForGroup = new Map();
const handlers = {
    init() {
        hasBackreferences = false;
        nodesContainingCapturingGroup.clear();
        containsCapturingGroupStack.length = 0;
        containsCapturingGroup = false;
        nextNewGroupNumber = 1;
        measurementGroupStack.length = 0;
        measurementGroupsForGroup.clear();
        newGroupNumberForGroup.clear();
        groupRenumbers = [];
    },
    RegExp(path) {
        regexp_tree_1.traverse(path.node, visitor);
        if (nodesContainingCapturingGroup.size > 0) {
            regexp_tree_1.transform(path.node, builder);
            regexp_tree_1.transform(path.node, groupRenumberer);
            if (hasBackreferences) {
                regexp_tree_1.transform(path.node, backreferenceRenumberer);
            }
        }
        return false;
    }
};
const nodeCallbacks = {
    pre(path) {
        containsCapturingGroupStack.push(containsCapturingGroup);
        containsCapturingGroup = path.node.type === "Group" && path.node.capturing;
    },
    post(path) {
        if (containsCapturingGroup) {
            nodesContainingCapturingGroup.add(path.node);
        }
        containsCapturingGroup = containsCapturingGroupStack.pop() || containsCapturingGroup;
    }
};
const visitor = {
    Alternative: nodeCallbacks,
    Disjunction: nodeCallbacks,
    Assertion: nodeCallbacks,
    Group: nodeCallbacks,
    Repetition: nodeCallbacks,
    Backreference(path) { hasBackreferences = true; }
};
const builder = {
    Alternative(path) {
        if (nodesContainingCapturingGroup.has(path.node)) {
```
