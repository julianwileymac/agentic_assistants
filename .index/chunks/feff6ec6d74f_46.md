# Chunk: feff6ec6d74f_46

- source: `.venv-lab/Lib/site-packages/notebook/static/1871.c375ee093b7e51966390.js`
- lines: 1964-2002
- chunk: 47/78

```
eTimeWidget = (AltDateTimeWidget);
//# sourceMappingURL=AltDateTimeWidget.js.map
;// CONCATENATED MODULE: ../node_modules/@rjsf/core/lib/components/widgets/CheckboxWidget.js



/** The `CheckBoxWidget` is a widget for rendering boolean properties.
 *  It is typically used to represent a boolean.
 *
 * @param props - The `WidgetProps` for this component
 */
function CheckboxWidget({ schema, uiSchema, options, id, value, disabled, readonly, label, hideLabel, autofocus = false, onBlur, onFocus, onChange, registry, }) {
    var _a;
    const DescriptionFieldTemplate = (0,lib_index_js_.getTemplate)('DescriptionFieldTemplate', registry, options);
    // Because an unchecked checkbox will cause html5 validation to fail, only add
    // the "required" attribute if the field value must be "true", due to the
    // "const" or "enum" keywords
    const required = (0,lib_index_js_.schemaRequiresTrueValue)(schema);
    const handleChange = (0,index_js_.useCallback)((event) => onChange(event.target.checked), [onChange]);
    const handleBlur = (0,index_js_.useCallback)((event) => onBlur(id, event.target.checked), [onBlur, id]);
    const handleFocus = (0,index_js_.useCallback)((event) => onFocus(id, event.target.checked), [onFocus, id]);
    const description = (_a = options.description) !== null && _a !== void 0 ? _a : schema.description;
    return ((0,jsx_runtime.jsxs)("div", { className: `checkbox ${disabled || readonly ? 'disabled' : ''}`, children: [!hideLabel && !!description && ((0,jsx_runtime.jsx)(DescriptionFieldTemplate, { id: (0,lib_index_js_.descriptionId)(id), description: description, schema: schema, uiSchema: uiSchema, registry: registry })), (0,jsx_runtime.jsxs)("label", { children: [(0,jsx_runtime.jsx)("input", { type: 'checkbox', id: id, name: id, checked: typeof value === 'undefined' ? false : value, required: required, disabled: disabled || readonly, autoFocus: autofocus, onChange: handleChange, onBlur: handleBlur, onFocus: handleFocus, "aria-describedby": (0,lib_index_js_.ariaDescribedByIds)(id) }), (0,lib_index_js_.labelValue)((0,jsx_runtime.jsx)("span", { children: label }), hideLabel)] })] }));
}
/* harmony default export */ const widgets_CheckboxWidget = (CheckboxWidget);
//# sourceMappingURL=CheckboxWidget.js.map
;// CONCATENATED MODULE: ../node_modules/@rjsf/core/lib/components/widgets/CheckboxesWidget.js



/** The `CheckboxesWidget` is a widget for rendering checkbox groups.
 *  It is typically used to represent an array of enums.
 *
 * @param props - The `WidgetProps` for this component
 */
function CheckboxesWidget({ id, disabled, options: { inline = false, enumOptions, enumDisabled, emptyValue }, value, autofocus = false, readonly, onChange, onBlur, onFocus, }) {
    const checkboxesValues = Array.isArray(value) ? value : [value];
    const handleBlur = (0,index_js_.useCallback)(({ target: { value } }) => onBlur(id, (0,lib_index_js_.enumOptionsValueForIndex)(value, enumOptions, emptyValue)), [onBlur, id]);
```
