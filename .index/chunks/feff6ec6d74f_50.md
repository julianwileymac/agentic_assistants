# Chunk: feff6ec6d74f_50

- source: `.venv-lab/Lib/site-packages/notebook/static/1871.c375ee093b7e51966390.js`
- lines: 2156-2209
- chunk: 51/78

```
  It is typically used with a string property with data-url format.
 */
function FileWidget(props) {
    const { disabled, readonly, required, multiple, onChange, value, options, registry } = props;
    const BaseInputTemplate = (0,lib_index_js_.getTemplate)('BaseInputTemplate', registry, options);
    const [filesInfo, setFilesInfo] = (0,index_js_.useState)(Array.isArray(value) ? extractFileInfo(value) : extractFileInfo([value]));
    const handleChange = (0,index_js_.useCallback)((event) => {
        if (!event.target.files) {
            return;
        }
        // Due to variances in themes, dealing with multiple files for the array case now happens one file at a time.
        // This is because we don't pass `multiple` into the `BaseInputTemplate` anymore. Instead, we deal with the single
        // file in each event and concatenate them together ourselves
        processFiles(event.target.files).then((filesInfoEvent) => {
            const newValue = filesInfoEvent.map((fileInfo) => fileInfo.dataURL);
            if (multiple) {
                setFilesInfo(filesInfo.concat(filesInfoEvent[0]));
                onChange(value.concat(newValue[0]));
            }
            else {
                setFilesInfo(filesInfoEvent);
                onChange(newValue[0]);
            }
        });
    }, [multiple, value, filesInfo, onChange]);
    return ((0,jsx_runtime.jsxs)("div", { children: [(0,jsx_runtime.jsx)(BaseInputTemplate, { ...props, disabled: disabled || readonly, type: 'file', required: value ? false : required, onChangeOverride: handleChange, value: '', accept: options.accept ? String(options.accept) : undefined }), (0,jsx_runtime.jsx)(FilesInfo, { filesInfo: filesInfo, registry: registry, preview: options.filePreview })] }));
}
/* harmony default export */ const widgets_FileWidget = (FileWidget);
//# sourceMappingURL=FileWidget.js.map
;// CONCATENATED MODULE: ../node_modules/@rjsf/core/lib/components/widgets/HiddenWidget.js

/** The `HiddenWidget` is a widget for rendering a hidden input field.
 *  It is typically used by setting type to "hidden".
 *
 * @param props - The `WidgetProps` for this component
 */
function HiddenWidget({ id, value, }) {
    return (0,jsx_runtime.jsx)("input", { type: 'hidden', id: id, name: id, value: typeof value === 'undefined' ? '' : value });
}
/* harmony default export */ const widgets_HiddenWidget = (HiddenWidget);
//# sourceMappingURL=HiddenWidget.js.map
;// CONCATENATED MODULE: ../node_modules/@rjsf/core/lib/components/widgets/PasswordWidget.js


/** The `PasswordWidget` component uses the `BaseInputTemplate` changing the type to `password`.
 *
 * @param props - The `WidgetProps` for this component
 */
function PasswordWidget(props) {
    const { options, registry } = props;
    const BaseInputTemplate = (0,lib_index_js_.getTemplate)('BaseInputTemplate', registry, options);
    return (0,jsx_runtime.jsx)(BaseInputTemplate, { type: 'password', ...props });
}
```
