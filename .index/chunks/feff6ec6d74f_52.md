# Chunk: feff6ec6d74f_52

- source: `.venv-lab/Lib/site-packages/notebook/static/1871.c375ee093b7e51966390.js`
- lines: 2235-2283
- chunk: 53/78

```
/@rjsf/core/lib/components/widgets/RangeWidget.js

/** The `RangeWidget` component uses the `BaseInputTemplate` changing the type to `range` and wrapping the result
 * in a div, with the value along side it.
 *
 * @param props - The `WidgetProps` for this component
 */
function RangeWidget(props) {
    const { value, registry: { templates: { BaseInputTemplate }, }, } = props;
    return ((0,jsx_runtime.jsxs)("div", { className: 'field-range-wrapper', children: [(0,jsx_runtime.jsx)(BaseInputTemplate, { type: 'range', ...props }), (0,jsx_runtime.jsx)("span", { className: 'range-view', children: value })] }));
}
//# sourceMappingURL=RangeWidget.js.map
;// CONCATENATED MODULE: ../node_modules/@rjsf/core/lib/components/widgets/SelectWidget.js



function getValue(event, multiple) {
    if (multiple) {
        return Array.from(event.target.options)
            .slice()
            .filter((o) => o.selected)
            .map((o) => o.value);
    }
    return event.target.value;
}
/** The `SelectWidget` is a widget for rendering dropdowns.
 *  It is typically used with string properties constrained with enum options.
 *
 * @param props - The `WidgetProps` for this component
 */
function SelectWidget({ schema, id, options, value, required, disabled, readonly, multiple = false, autofocus = false, onChange, onBlur, onFocus, placeholder, }) {
    const { enumOptions, enumDisabled, emptyValue: optEmptyVal } = options;
    const emptyValue = multiple ? [] : '';
    const handleFocus = (0,index_js_.useCallback)((event) => {
        const newValue = getValue(event, multiple);
        return onFocus(id, (0,lib_index_js_.enumOptionsValueForIndex)(newValue, enumOptions, optEmptyVal));
    }, [onFocus, id, schema, multiple, options]);
    const handleBlur = (0,index_js_.useCallback)((event) => {
        const newValue = getValue(event, multiple);
        return onBlur(id, (0,lib_index_js_.enumOptionsValueForIndex)(newValue, enumOptions, optEmptyVal));
    }, [onBlur, id, schema, multiple, options]);
    const handleChange = (0,index_js_.useCallback)((event) => {
        const newValue = getValue(event, multiple);
        return onChange((0,lib_index_js_.enumOptionsValueForIndex)(newValue, enumOptions, optEmptyVal));
    }, [onChange, schema, multiple, options]);
    const selectedIndexes = (0,lib_index_js_.enumOptionsIndexForValue)(value, enumOptions, multiple);
    return ((0,jsx_runtime.jsxs)("select", { id: id, name: id, multiple: multiple, className: 'form-control', value: typeof selectedIndexes === 'undefined' ? emptyValue : selectedIndexes, required: required, disabled: disabled || readonly, autoFocus: autofocus, onBlur: handleBlur, onFocus: handleFocus, onChange: handleChange, "aria-describedby": (0,lib_index_js_.ariaDescribedByIds)(id), children: [!multiple && schema.default === undefined && (0,jsx_runtime.jsx)("option", { value: '', children: placeholder }), Array.isArray(enumOptions) &&
                enumOptions.map(({ value, label }, i) => {
```
