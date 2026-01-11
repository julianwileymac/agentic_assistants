# Chunk: feff6ec6d74f_53

- source: `.venv-lab/Lib/site-packages/notebook/static/1871.c375ee093b7e51966390.js`
- lines: 2281-2334
- chunk: 54/78

```
onChange: handleChange, "aria-describedby": (0,lib_index_js_.ariaDescribedByIds)(id), children: [!multiple && schema.default === undefined && (0,jsx_runtime.jsx)("option", { value: '', children: placeholder }), Array.isArray(enumOptions) &&
                enumOptions.map(({ value, label }, i) => {
                    const disabled = enumDisabled && enumDisabled.indexOf(value) !== -1;
                    return ((0,jsx_runtime.jsx)("option", { value: String(i), disabled: disabled, children: label }, i));
                })] }));
}
/* harmony default export */ const widgets_SelectWidget = (SelectWidget);
//# sourceMappingURL=SelectWidget.js.map
;// CONCATENATED MODULE: ../node_modules/@rjsf/core/lib/components/widgets/TextareaWidget.js



/** The `TextareaWidget` is a widget for rendering input fields as textarea.
 *
 * @param props - The `WidgetProps` for this component
 */
function TextareaWidget({ id, options = {}, placeholder, value, required, disabled, readonly, autofocus = false, onChange, onBlur, onFocus, }) {
    const handleChange = (0,index_js_.useCallback)(({ target: { value } }) => onChange(value === '' ? options.emptyValue : value), [onChange, options.emptyValue]);
    const handleBlur = (0,index_js_.useCallback)(({ target: { value } }) => onBlur(id, value), [onBlur, id]);
    const handleFocus = (0,index_js_.useCallback)(({ target: { value } }) => onFocus(id, value), [id, onFocus]);
    return ((0,jsx_runtime.jsx)("textarea", { id: id, name: id, className: 'form-control', value: value ? value : '', placeholder: placeholder, required: required, disabled: disabled, readOnly: readonly, autoFocus: autofocus, rows: options.rows, onBlur: handleBlur, onFocus: handleFocus, onChange: handleChange, "aria-describedby": (0,lib_index_js_.ariaDescribedByIds)(id) }));
}
TextareaWidget.defaultProps = {
    autofocus: false,
    options: {},
};
/* harmony default export */ const widgets_TextareaWidget = (TextareaWidget);
//# sourceMappingURL=TextareaWidget.js.map
;// CONCATENATED MODULE: ../node_modules/@rjsf/core/lib/components/widgets/TextWidget.js


/** The `TextWidget` component uses the `BaseInputTemplate`.
 *
 * @param props - The `WidgetProps` for this component
 */
function TextWidget(props) {
    const { options, registry } = props;
    const BaseInputTemplate = (0,lib_index_js_.getTemplate)('BaseInputTemplate', registry, options);
    return (0,jsx_runtime.jsx)(BaseInputTemplate, { ...props });
}
//# sourceMappingURL=TextWidget.js.map
;// CONCATENATED MODULE: ../node_modules/@rjsf/core/lib/components/widgets/TimeWidget.js



/** The `TimeWidget` component uses the `BaseInputTemplate` changing the type to `time` and transforms
 * the value to undefined when it is falsy during the `onChange` handling.
 *
 * @param props - The `WidgetProps` for this component
 */
function TimeWidget(props) {
    const { onChange, options, registry } = props;
    const BaseInputTemplate = (0,lib_index_js_.getTemplate)('BaseInputTemplate', registry, options);
```
