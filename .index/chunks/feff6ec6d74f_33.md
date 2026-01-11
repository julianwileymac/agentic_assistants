# Chunk: feff6ec6d74f_33

- source: `.venv-lab/Lib/site-packages/notebook/static/1871.c375ee093b7e51966390.js`
- lines: 1376-1409
- chunk: 34/78

```
ld = registry.fields.AnyOfField;
    const _OneOfField = registry.fields.OneOfField;
    const isReplacingAnyOrOneOf = (uiSchema === null || uiSchema === void 0 ? void 0 : uiSchema['ui:field']) && (uiSchema === null || uiSchema === void 0 ? void 0 : uiSchema['ui:fieldReplacesAnyOrOneOf']) === true;
    return ((0,jsx_runtime.jsx)(FieldTemplate, { ...fieldProps, children: (0,jsx_runtime.jsxs)(jsx_runtime.Fragment, { children: [field, schema.anyOf && !isReplacingAnyOrOneOf && !schemaUtils.isSelect(schema) && ((0,jsx_runtime.jsx)(_AnyOfField, { name: name, disabled: disabled, readonly: readonly, hideError: hideError, errorSchema: errorSchema, formData: formData, formContext: formContext, idPrefix: idPrefix, idSchema: idSchema, idSeparator: idSeparator, onBlur: props.onBlur, onChange: props.onChange, onFocus: props.onFocus, options: schema.anyOf.map((_schema) => schemaUtils.retrieveSchema(isObject_default()(_schema) ? _schema : {}, formData)), registry: registry, schema: schema, uiSchema: uiSchema })), schema.oneOf && !isReplacingAnyOrOneOf && !schemaUtils.isSelect(schema) && ((0,jsx_runtime.jsx)(_OneOfField, { name: name, disabled: disabled, readonly: readonly, hideError: hideError, errorSchema: errorSchema, formData: formData, formContext: formContext, idPrefix: idPrefix, idSchema: idSchema, idSeparator: idSeparator, onBlur: props.onBlur, onChange: props.onChange, onFocus: props.onFocus, options: schema.oneOf.map((_schema) => schemaUtils.retrieveSchema(isObject_default()(_schema) ? _schema : {}, formData)), registry: registry, schema: schema, uiSchema: uiSchema }))] }) }));
}
/** The `SchemaField` component determines whether it is necessary to rerender the component based on any props changes
 * and if so, calls the `SchemaFieldRender` component with the props.
 */
class SchemaField extends index_js_.Component {
    shouldComponentUpdate(nextProps) {
        return !(0,lib_index_js_.deepEquals)(this.props, nextProps);
    }
    render() {
        return (0,jsx_runtime.jsx)(SchemaFieldRender, { ...this.props });
    }
}
/* harmony default export */ const fields_SchemaField = (SchemaField);
//# sourceMappingURL=SchemaField.js.map
;// CONCATENATED MODULE: ../node_modules/@rjsf/core/lib/components/fields/StringField.js


/** The `StringField` component is used to render a schema field that represents a string type
 *
 * @param props - The `FieldProps` for this template
 */
function StringField(props) {
    var _a;
    const { schema, name, uiSchema, idSchema, formData, required, disabled = false, readonly = false, autofocus = false, onChange, onBlur, onFocus, registry, rawErrors, hideError, } = props;
    const { title, format } = schema;
    const { widgets, formContext, schemaUtils, globalUiOptions } = registry;
    const enumOptions = schemaUtils.isSelect(schema) ? (0,lib_index_js_.optionsList)(schema) : undefined;
    let defaultWidget = enumOptions ? 'select' : 'text';
    if (format && (0,lib_index_js_.hasWidget)(schema, format, widgets)) {
```
