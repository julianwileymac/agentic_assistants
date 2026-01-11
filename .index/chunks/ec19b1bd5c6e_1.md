# Chunk: ec19b1bd5c6e_1

- source: `.venv-lab/Lib/site-packages/notebook/static/2913.274b19d8f201991f4a69.js`
- lines: 76-139
- chunk: 2/104

```
onst { measurementRegExp, groupInfos } = getMeasurementRegExp(regexp);
                measurementRegExp.lastIndex = index;
                const measuredResult = nativeExec.call(measurementRegExp, string);
                if (measuredResult === null)
                    throw new TypeError();
                makeDataProperty(result, "indices", indicesArray = makeIndicesArray(measuredResult, groupInfos));
            }
            return indicesArray;
        },
        set(value) {
            makeDataProperty(result, "indices", value);
        }
    });
    return result;
}
function execSpecCompliant(regexp, string) {
    const { measurementRegExp, groupInfos } = getMeasurementRegExp(regexp);
    measurementRegExp.lastIndex = regexp.lastIndex;
    const measuredResult = nativeExec.call(measurementRegExp, string);
    if (measuredResult === null)
        return null;
    regexp.lastIndex = measurementRegExp.lastIndex;
    const result = [];
    makeDataProperty(result, 0, measuredResult[0]);
    for (const groupInfo of groupInfos) {
        makeDataProperty(result, groupInfo.oldGroupNumber, measuredResult[groupInfo.newGroupNumber]);
    }
    makeDataProperty(result, "index", measuredResult.index);
    makeDataProperty(result, "input", measuredResult.input);
    makeDataProperty(result, "groups", measuredResult.groups);
    makeDataProperty(result, "indices", makeIndicesArray(measuredResult, groupInfos));
    return result;
}
function getMeasurementRegExp(regexp) {
    let transformed = weakMeasurementRegExp.get(regexp);
    if (!transformed) {
        transformed = transformMeasurementGroups(regexp_tree_1.parse(`/${regexp.source}/${regexp.flags}`));
        weakMeasurementRegExp.set(regexp, transformed);
    }
    const groupInfos = transformed.getExtra();
    const measurementRegExp = transformed.toRegExp();
    return { measurementRegExp, groupInfos };
}
function makeIndicesArray(measuredResult, groupInfos) {
    const matchStart = measuredResult.index;
    const matchEnd = matchStart + measuredResult[0].length;
    const hasGroups = !!measuredResult.groups;
    const indicesArray = [];
    const groups = hasGroups ? Object.create(null) : undefined;
    makeDataProperty(indicesArray, 0, [matchStart, matchEnd]);
    for (const groupInfo of groupInfos) {
        let indices;
        if (measuredResult[groupInfo.newGroupNumber] !== undefined) {
            let startIndex = matchStart;
            if (groupInfo.measurementGroups) {
                for (const measurementGroup of groupInfo.measurementGroups) {
                    startIndex += measuredResult[measurementGroup].length;
                }
            }
            const endIndex = startIndex + measuredResult[groupInfo.newGroupNumber].length;
            indices = [startIndex, endIndex];
        }
        makeDataProperty(indicesArray, groupInfo.oldGroupNumber, indices);
```
