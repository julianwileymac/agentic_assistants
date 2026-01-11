# Chunk: feff6ec6d74f_42

- source: `.venv-lab/Lib/site-packages/notebook/static/1871.c375ee093b7e51966390.js`
- lines: 1772-1828
- chunk: 43/78

```
ry: registry })), properties.map((prop) => prop.content), (0,lib_index_js_.canExpand)(schema, uiSchema, formData) && ((0,jsx_runtime.jsx)(AddButton, { className: 'object-property-expand', onClick: onAddClick(schema), disabled: disabled || readonly, uiSchema: uiSchema, registry: registry }))] }));
}
//# sourceMappingURL=ObjectFieldTemplate.js.map
;// CONCATENATED MODULE: ../node_modules/@rjsf/core/lib/components/templates/TitleField.js

const TitleField_REQUIRED_FIELD_SYMBOL = '*';
/** The `TitleField` is the template to use to render the title of a field
 *
 * @param props - The `TitleFieldProps` for this component
 */
function TitleField(props) {
    const { id, title, required } = props;
    return ((0,jsx_runtime.jsxs)("legend", { id: id, children: [title, required && (0,jsx_runtime.jsx)("span", { className: 'required', children: TitleField_REQUIRED_FIELD_SYMBOL })] }));
}
//# sourceMappingURL=TitleField.js.map
;// CONCATENATED MODULE: ../node_modules/@rjsf/core/lib/components/templates/UnsupportedField.js



/** The `UnsupportedField` component is used to render a field in the schema is one that is not supported by
 * react-jsonschema-form.
 *
 * @param props - The `FieldProps` for this template
 */
function UnsupportedField(props) {
    const { schema, idSchema, reason, registry } = props;
    const { translateString } = registry;
    let translateEnum = lib_index_js_.TranslatableString.UnsupportedField;
    const translateParams = [];
    if (idSchema && idSchema.$id) {
        translateEnum = lib_index_js_.TranslatableString.UnsupportedFieldWithId;
        translateParams.push(idSchema.$id);
    }
    if (reason) {
        translateEnum =
            translateEnum === lib_index_js_.TranslatableString.UnsupportedField
                ? lib_index_js_.TranslatableString.UnsupportedFieldWithReason
                : lib_index_js_.TranslatableString.UnsupportedFieldWithIdAndReason;
        translateParams.push(reason);
    }
    return ((0,jsx_runtime.jsxs)("div", { className: 'unsupported-field', children: [(0,jsx_runtime.jsx)("p", { children: (0,jsx_runtime.jsx)(index_modern, { children: translateString(translateEnum, translateParams) }) }), schema && (0,jsx_runtime.jsx)("pre", { children: JSON.stringify(schema, null, 2) })] }));
}
/* harmony default export */ const templates_UnsupportedField = (UnsupportedField);
//# sourceMappingURL=UnsupportedField.js.map
;// CONCATENATED MODULE: ../node_modules/@rjsf/core/lib/components/templates/WrapIfAdditionalTemplate.js



/** The `WrapIfAdditional` component is used by the `FieldTemplate` to rename, or remove properties that are
 * part of an `additionalProperties` part of a schema.
 *
 * @param props - The `WrapIfAdditionalProps` for this component
 */
function WrapIfAdditionalTemplate(props) {
    const { id, classNames, style, disabled, label, onKeyChange, onDropPropertyClick, readonly, required, schema, children, uiSchema, registry, } = props;
    const { templates, translateString } = registry;
```
