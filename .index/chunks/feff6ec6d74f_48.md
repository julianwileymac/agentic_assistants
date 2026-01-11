# Chunk: feff6ec6d74f_48

- source: `.venv-lab/Lib/site-packages/notebook/static/1871.c375ee093b7e51966390.js`
- lines: 2031-2097
- chunk: 49/78

```
bled, readonly, options, registry } = props;
    const BaseInputTemplate = (0,lib_index_js_.getTemplate)('BaseInputTemplate', registry, options);
    return (0,jsx_runtime.jsx)(BaseInputTemplate, { type: 'color', ...props, disabled: disabled || readonly });
}
//# sourceMappingURL=ColorWidget.js.map
;// CONCATENATED MODULE: ../node_modules/@rjsf/core/lib/components/widgets/DateWidget.js



/** The `DateWidget` component uses the `BaseInputTemplate` changing the type to `date` and transforms
 * the value to undefined when it is falsy during the `onChange` handling.
 *
 * @param props - The `WidgetProps` for this component
 */
function DateWidget(props) {
    const { onChange, options, registry } = props;
    const BaseInputTemplate = (0,lib_index_js_.getTemplate)('BaseInputTemplate', registry, options);
    const handleChange = (0,index_js_.useCallback)((value) => onChange(value || undefined), [onChange]);
    return (0,jsx_runtime.jsx)(BaseInputTemplate, { type: 'date', ...props, onChange: handleChange });
}
//# sourceMappingURL=DateWidget.js.map
;// CONCATENATED MODULE: ../node_modules/@rjsf/core/lib/components/widgets/DateTimeWidget.js


/** The `DateTimeWidget` component uses the `BaseInputTemplate` changing the type to `datetime-local` and transforms
 * the value to/from utc using the appropriate utility functions.
 *
 * @param props - The `WidgetProps` for this component
 */
function DateTimeWidget(props) {
    const { onChange, value, options, registry } = props;
    const BaseInputTemplate = (0,lib_index_js_.getTemplate)('BaseInputTemplate', registry, options);
    return ((0,jsx_runtime.jsx)(BaseInputTemplate, { type: 'datetime-local', ...props, value: (0,lib_index_js_.utcToLocal)(value), onChange: (value) => onChange((0,lib_index_js_.localToUTC)(value)) }));
}
//# sourceMappingURL=DateTimeWidget.js.map
;// CONCATENATED MODULE: ../node_modules/@rjsf/core/lib/components/widgets/EmailWidget.js


/** The `EmailWidget` component uses the `BaseInputTemplate` changing the type to `email`.
 *
 * @param props - The `WidgetProps` for this component
 */
function EmailWidget(props) {
    const { options, registry } = props;
    const BaseInputTemplate = (0,lib_index_js_.getTemplate)('BaseInputTemplate', registry, options);
    return (0,jsx_runtime.jsx)(BaseInputTemplate, { type: 'email', ...props });
}
//# sourceMappingURL=EmailWidget.js.map
;// CONCATENATED MODULE: ../node_modules/@rjsf/core/lib/components/widgets/FileWidget.js




function addNameToDataURL(dataURL, name) {
    if (dataURL === null) {
        return null;
    }
    return dataURL.replace(';base64', `;name=${encodeURIComponent(name)};base64`);
}
function processFile(file) {
    const { name, size, type } = file;
    return new Promise((resolve, reject) => {
        const reader = new window.FileReader();
        reader.onerror = reject;
        reader.onload = (event) => {
            var _a;
```
