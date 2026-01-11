# Chunk: feff6ec6d74f_18

- source: `.venv-lab/Lib/site-packages/notebook/static/1871.c375ee093b7e51966390.js`
- lines: 939-983
- chunk: 19/78

```
e state. If it matches the cached value, the cached
 *    value is passed to the input instead of the formData value
 */
function NumberField(props) {
    const { registry, onChange, formData, value: initialValue } = props;
    const [lastValue, setLastValue] = (0,index_js_.useState)(initialValue);
    const { StringField } = registry.fields;
    let value = formData;
    /** Handle the change from the `StringField` to properly convert to a number
     *
     * @param value - The current value for the change occurring
     */
    const handleChange = (0,index_js_.useCallback)((value) => {
        // Cache the original value in component state
        setLastValue(value);
        // Normalize decimals that don't start with a zero character in advance so
        // that the rest of the normalization logic is simpler
        if (`${value}`.charAt(0) === '.') {
            value = `0${value}`;
        }
        // Check that the value is a string (this can happen if the widget used is a
        // <select>, due to an enum declaration etc) then, if the value ends in a
        // trailing decimal point or multiple zeroes, strip the trailing values
        const processed = typeof value === 'string' && value.match(trailingCharMatcherWithPrefix)
            ? (0,lib_index_js_.asNumber)(value.replace(trailingCharMatcher, ''))
            : (0,lib_index_js_.asNumber)(value);
        onChange(processed);
    }, [onChange]);
    if (typeof lastValue === 'string' && typeof value === 'number') {
        // Construct a regular expression that checks for a string that consists
        // of the formData value suffixed with zero or one '.' characters and zero
        // or more '0' characters
        const re = new RegExp(`${value}`.replace('.', '\\.') + '\\.?0*$');
        // If the cached "lastValue" is a match, use that instead of the formData
        // value to prevent the input value from changing in the UI
        if (lastValue.match(re)) {
            value = lastValue;
        }
    }
    return (0,jsx_runtime.jsx)(StringField, { ...props, formData: value, onChange: handleChange });
}
/* harmony default export */ const fields_NumberField = (NumberField);
//# sourceMappingURL=NumberField.js.map
;// CONCATENATED MODULE: ../node_modules/markdown-to-jsx/dist/index.modern.js
```
