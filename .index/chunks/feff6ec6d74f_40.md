# Chunk: feff6ec6d74f_40

- source: `.venv-lab/Lib/site-packages/notebook/static/1871.c375ee093b7e51966390.js`
- lines: 1674-1732
- chunk: 41/78

```
', children: translateString(lib_index_js_.TranslatableString.ErrorsLabel) }) }), (0,jsx_runtime.jsx)("ul", { className: 'list-group', children: errors.map((error, i) => {
                    return ((0,jsx_runtime.jsx)("li", { className: 'list-group-item text-danger', children: error.stack }, i));
                }) })] }));
}
//# sourceMappingURL=ErrorList.js.map
;// CONCATENATED MODULE: ../node_modules/@rjsf/core/lib/components/templates/FieldTemplate/Label.js

const REQUIRED_FIELD_SYMBOL = '*';
/** Renders a label for a field
 *
 * @param props - The `LabelProps` for this component
 */
function Label(props) {
    const { label, required, id } = props;
    if (!label) {
        return null;
    }
    return ((0,jsx_runtime.jsxs)("label", { className: 'control-label', htmlFor: id, children: [label, required && (0,jsx_runtime.jsx)("span", { className: 'required', children: REQUIRED_FIELD_SYMBOL })] }));
}
//# sourceMappingURL=Label.js.map
;// CONCATENATED MODULE: ../node_modules/@rjsf/core/lib/components/templates/FieldTemplate/FieldTemplate.js



/** The `FieldTemplate` component is the template used by `SchemaField` to render any field. It renders the field
 * content, (label, description, children, errors and help) inside of a `WrapIfAdditional` component.
 *
 * @param props - The `FieldTemplateProps` for this component
 */
function FieldTemplate(props) {
    const { id, label, children, errors, help, description, hidden, required, displayLabel, registry, uiSchema } = props;
    const uiOptions = (0,lib_index_js_.getUiOptions)(uiSchema);
    const WrapIfAdditionalTemplate = (0,lib_index_js_.getTemplate)('WrapIfAdditionalTemplate', registry, uiOptions);
    if (hidden) {
        return (0,jsx_runtime.jsx)("div", { className: 'hidden', children: children });
    }
    return ((0,jsx_runtime.jsxs)(WrapIfAdditionalTemplate, { ...props, children: [displayLabel && (0,jsx_runtime.jsx)(Label, { label: label, required: required, id: id }), displayLabel && description ? description : null, children, errors, help] }));
}
//# sourceMappingURL=FieldTemplate.js.map
;// CONCATENATED MODULE: ../node_modules/@rjsf/core/lib/components/templates/FieldTemplate/index.js

/* harmony default export */ const templates_FieldTemplate = (FieldTemplate);
//# sourceMappingURL=index.js.map
;// CONCATENATED MODULE: ../node_modules/@rjsf/core/lib/components/templates/FieldErrorTemplate.js


/** The `FieldErrorTemplate` component renders the errors local to the particular field
 *
 * @param props - The `FieldErrorProps` for the errors being rendered
 */
function FieldErrorTemplate(props) {
    const { errors = [], idSchema } = props;
    if (errors.length === 0) {
        return null;
    }
    const id = (0,lib_index_js_.errorId)(idSchema);
    return ((0,jsx_runtime.jsx)("div", { children: (0,jsx_runtime.jsx)("ul", { id: id, className: 'error-detail bs-callout bs-callout-info', children: errors
                .filter((elem) => !!elem)
```
