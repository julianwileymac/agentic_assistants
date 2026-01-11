# Chunk: feff6ec6d74f_38

- source: `.venv-lab/Lib/site-packages/notebook/static/1871.c375ee093b7e51966390.js`
- lines: 1575-1623
- chunk: 39/78

```
ined, onChange: onChangeOverride || _onChange, onBlur: _onBlur, onFocus: _onFocus, "aria-describedby": (0,lib_index_js_.ariaDescribedByIds)(id, !!schema.examples) }), Array.isArray(schema.examples) && ((0,jsx_runtime.jsx)("datalist", { id: (0,lib_index_js_.examplesId)(id), children: schema.examples
                    .concat(schema.default && !schema.examples.includes(schema.default) ? [schema.default] : [])
                    .map((example) => {
                    return (0,jsx_runtime.jsx)("option", { value: example }, example);
                }) }, `datalist_${id}`))] }));
}
//# sourceMappingURL=BaseInputTemplate.js.map
;// CONCATENATED MODULE: ../node_modules/@rjsf/core/lib/components/templates/ButtonTemplates/SubmitButton.js


/** The `SubmitButton` renders a button that represent the `Submit` action on a form
 */
function SubmitButton({ uiSchema }) {
    const { submitText, norender, props: submitButtonProps = {} } = (0,lib_index_js_.getSubmitButtonOptions)(uiSchema);
    if (norender) {
        return null;
    }
    return ((0,jsx_runtime.jsx)("div", { children: (0,jsx_runtime.jsx)("button", { type: 'submit', ...submitButtonProps, className: `btn btn-info ${submitButtonProps.className || ''}`, children: submitText }) }));
}
//# sourceMappingURL=SubmitButton.js.map
;// CONCATENATED MODULE: ../node_modules/@rjsf/core/lib/components/templates/ButtonTemplates/IconButton.js


function IconButton(props) {
    const { iconType = 'default', icon, className, uiSchema, registry, ...otherProps } = props;
    return ((0,jsx_runtime.jsx)("button", { type: 'button', className: `btn btn-${iconType} ${className}`, ...otherProps, children: (0,jsx_runtime.jsx)("i", { className: `glyphicon glyphicon-${icon}` }) }));
}
function CopyButton(props) {
    const { registry: { translateString }, } = props;
    return ((0,jsx_runtime.jsx)(IconButton, { title: translateString(lib_index_js_.TranslatableString.CopyButton), className: 'array-item-copy', ...props, icon: 'copy' }));
}
function MoveDownButton(props) {
    const { registry: { translateString }, } = props;
    return ((0,jsx_runtime.jsx)(IconButton, { title: translateString(lib_index_js_.TranslatableString.MoveDownButton), className: 'array-item-move-down', ...props, icon: 'arrow-down' }));
}
function MoveUpButton(props) {
    const { registry: { translateString }, } = props;
    return ((0,jsx_runtime.jsx)(IconButton, { title: translateString(lib_index_js_.TranslatableString.MoveUpButton), className: 'array-item-move-up', ...props, icon: 'arrow-up' }));
}
function RemoveButton(props) {
    const { registry: { translateString }, } = props;
    return ((0,jsx_runtime.jsx)(IconButton, { title: translateString(lib_index_js_.TranslatableString.RemoveButton), className: 'array-item-remove', ...props, iconType: 'danger', icon: 'remove' }));
}
//# sourceMappingURL=IconButton.js.map
;// CONCATENATED MODULE: ../node_modules/@rjsf/core/lib/components/templates/ButtonTemplates/AddButton.js
```
