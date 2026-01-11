# Chunk: feff6ec6d74f_47

- source: `.venv-lab/Lib/site-packages/notebook/static/1871.c375ee093b7e51966390.js`
- lines: 1999-2036
- chunk: 48/78

```
 = false, readonly, onChange, onBlur, onFocus, }) {
    const checkboxesValues = Array.isArray(value) ? value : [value];
    const handleBlur = (0,index_js_.useCallback)(({ target: { value } }) => onBlur(id, (0,lib_index_js_.enumOptionsValueForIndex)(value, enumOptions, emptyValue)), [onBlur, id]);
    const handleFocus = (0,index_js_.useCallback)(({ target: { value } }) => onFocus(id, (0,lib_index_js_.enumOptionsValueForIndex)(value, enumOptions, emptyValue)), [onFocus, id]);
    return ((0,jsx_runtime.jsx)("div", { className: 'checkboxes', id: id, children: Array.isArray(enumOptions) &&
            enumOptions.map((option, index) => {
                const checked = (0,lib_index_js_.enumOptionsIsSelected)(option.value, checkboxesValues);
                const itemDisabled = Array.isArray(enumDisabled) && enumDisabled.indexOf(option.value) !== -1;
                const disabledCls = disabled || itemDisabled || readonly ? 'disabled' : '';
                const handleChange = (event) => {
                    if (event.target.checked) {
                        onChange((0,lib_index_js_.enumOptionsSelectValue)(index, checkboxesValues, enumOptions));
                    }
                    else {
                        onChange((0,lib_index_js_.enumOptionsDeselectValue)(index, checkboxesValues, enumOptions));
                    }
                };
                const checkbox = ((0,jsx_runtime.jsxs)("span", { children: [(0,jsx_runtime.jsx)("input", { type: 'checkbox', id: (0,lib_index_js_.optionId)(id, index), name: id, checked: checked, value: String(index), disabled: disabled || itemDisabled || readonly, autoFocus: autofocus && index === 0, onChange: handleChange, onBlur: handleBlur, onFocus: handleFocus, "aria-describedby": (0,lib_index_js_.ariaDescribedByIds)(id) }), (0,jsx_runtime.jsx)("span", { children: option.label })] }));
                return inline ? ((0,jsx_runtime.jsx)("label", { className: `checkbox-inline ${disabledCls}`, children: checkbox }, index)) : ((0,jsx_runtime.jsx)("div", { className: `checkbox ${disabledCls}`, children: (0,jsx_runtime.jsx)("label", { children: checkbox }) }, index));
            }) }));
}
/* harmony default export */ const widgets_CheckboxesWidget = (CheckboxesWidget);
//# sourceMappingURL=CheckboxesWidget.js.map
;// CONCATENATED MODULE: ../node_modules/@rjsf/core/lib/components/widgets/ColorWidget.js


/** The `ColorWidget` component uses the `BaseInputTemplate` changing the type to `color` and disables it when it is
 * either disabled or readonly.
 *
 * @param props - The `WidgetProps` for this component
 */
function ColorWidget(props) {
    const { disabled, readonly, options, registry } = props;
    const BaseInputTemplate = (0,lib_index_js_.getTemplate)('BaseInputTemplate', registry, options);
    return (0,jsx_runtime.jsx)(BaseInputTemplate, { type: 'color', ...props, disabled: disabled || readonly });
}
//# sourceMappingURL=ColorWidget.js.map
```
