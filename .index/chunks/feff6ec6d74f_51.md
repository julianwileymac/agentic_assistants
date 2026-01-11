# Chunk: feff6ec6d74f_51

- source: `.venv-lab/Lib/site-packages/notebook/static/1871.c375ee093b7e51966390.js`
- lines: 2202-2243
- chunk: 52/78

```
he `WidgetProps` for this component
 */
function PasswordWidget(props) {
    const { options, registry } = props;
    const BaseInputTemplate = (0,lib_index_js_.getTemplate)('BaseInputTemplate', registry, options);
    return (0,jsx_runtime.jsx)(BaseInputTemplate, { type: 'password', ...props });
}
//# sourceMappingURL=PasswordWidget.js.map
;// CONCATENATED MODULE: ../node_modules/@rjsf/core/lib/components/widgets/RadioWidget.js



/** The `RadioWidget` is a widget for rendering a radio group.
 *  It is typically used with a string property constrained with enum options.
 *
 * @param props - The `WidgetProps` for this component
 */
function RadioWidget({ options, value, required, disabled, readonly, autofocus = false, onBlur, onFocus, onChange, id, }) {
    const { enumOptions, enumDisabled, inline, emptyValue } = options;
    const handleBlur = (0,index_js_.useCallback)(({ target: { value } }) => onBlur(id, (0,lib_index_js_.enumOptionsValueForIndex)(value, enumOptions, emptyValue)), [onBlur, id]);
    const handleFocus = (0,index_js_.useCallback)(({ target: { value } }) => onFocus(id, (0,lib_index_js_.enumOptionsValueForIndex)(value, enumOptions, emptyValue)), [onFocus, id]);
    return ((0,jsx_runtime.jsx)("div", { className: 'field-radio-group', id: id, children: Array.isArray(enumOptions) &&
            enumOptions.map((option, i) => {
                const checked = (0,lib_index_js_.enumOptionsIsSelected)(option.value, value);
                const itemDisabled = Array.isArray(enumDisabled) && enumDisabled.indexOf(option.value) !== -1;
                const disabledCls = disabled || itemDisabled || readonly ? 'disabled' : '';
                const handleChange = () => onChange(option.value);
                const radio = ((0,jsx_runtime.jsxs)("span", { children: [(0,jsx_runtime.jsx)("input", { type: 'radio', id: (0,lib_index_js_.optionId)(id, i), checked: checked, name: id, required: required, value: String(i), disabled: disabled || itemDisabled || readonly, autoFocus: autofocus && i === 0, onChange: handleChange, onBlur: handleBlur, onFocus: handleFocus, "aria-describedby": (0,lib_index_js_.ariaDescribedByIds)(id) }), (0,jsx_runtime.jsx)("span", { children: option.label })] }));
                return inline ? ((0,jsx_runtime.jsx)("label", { className: `radio-inline ${disabledCls}`, children: radio }, i)) : ((0,jsx_runtime.jsx)("div", { className: `radio ${disabledCls}`, children: (0,jsx_runtime.jsx)("label", { children: radio }) }, i));
            }) }));
}
/* harmony default export */ const widgets_RadioWidget = (RadioWidget);
//# sourceMappingURL=RadioWidget.js.map
;// CONCATENATED MODULE: ../node_modules/@rjsf/core/lib/components/widgets/RangeWidget.js

/** The `RangeWidget` component uses the `BaseInputTemplate` changing the type to `range` and wrapping the result
 * in a div, with the value along side it.
 *
 * @param props - The `WidgetProps` for this component
 */
function RangeWidget(props) {
```
