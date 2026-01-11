# Chunk: feff6ec6d74f_30

- source: `.venv-lab/Lib/site-packages/notebook/static/1871.c375ee093b7e51966390.js`
- lines: 1248-1296
- chunk: 31/78

```
eturns - The `Field` component that is used to render the actual field data
 */
function getFieldComponent(schema, uiOptions, idSchema, registry) {
    const field = uiOptions.field;
    const { fields, translateString } = registry;
    if (typeof field === 'function') {
        return field;
    }
    if (typeof field === 'string' && field in fields) {
        return fields[field];
    }
    const schemaType = (0,lib_index_js_.getSchemaType)(schema);
    const type = Array.isArray(schemaType) ? schemaType[0] : schemaType || '';
    const schemaId = schema.$id;
    let componentName = COMPONENT_TYPES[type];
    if (schemaId && schemaId in fields) {
        componentName = schemaId;
    }
    // If the type is not defined and the schema uses 'anyOf' or 'oneOf', don't
    // render a field and let the MultiSchemaField component handle the form display
    if (!componentName && (schema.anyOf || schema.oneOf)) {
        return () => null;
    }
    return componentName in fields
        ? fields[componentName]
        : () => {
            const UnsupportedFieldTemplate = (0,lib_index_js_.getTemplate)('UnsupportedFieldTemplate', registry, uiOptions);
            return ((0,jsx_runtime.jsx)(UnsupportedFieldTemplate, { schema: schema, idSchema: idSchema, reason: translateString(lib_index_js_.TranslatableString.UnknownFieldType, [String(schema.type)]), registry: registry }));
        };
}
/** The `SchemaFieldRender` component is the work-horse of react-jsonschema-form, determining what kind of real field to
 * render based on the `schema`, `uiSchema` and all the other props. It also deals with rendering the `anyOf` and
 * `oneOf` fields.
 *
 * @param props - The `FieldProps` for this component
 */
function SchemaFieldRender(props) {
    const { schema: _schema, idSchema: _idSchema, uiSchema, formData, errorSchema, idPrefix, idSeparator, name, onChange, onKeyChange, onDropPropertyClick, required, registry, wasPropertyKeyModified = false, } = props;
    const { formContext, schemaUtils, globalUiOptions } = registry;
    const uiOptions = (0,lib_index_js_.getUiOptions)(uiSchema, globalUiOptions);
    const FieldTemplate = (0,lib_index_js_.getTemplate)('FieldTemplate', registry, uiOptions);
    const DescriptionFieldTemplate = (0,lib_index_js_.getTemplate)('DescriptionFieldTemplate', registry, uiOptions);
    const FieldHelpTemplate = (0,lib_index_js_.getTemplate)('FieldHelpTemplate', registry, uiOptions);
    const FieldErrorTemplate = (0,lib_index_js_.getTemplate)('FieldErrorTemplate', registry, uiOptions);
    const schema = schemaUtils.retrieveSchema(_schema, formData);
    const fieldId = _idSchema[lib_index_js_.ID_KEY];
    const idSchema = (0,lib_index_js_.mergeObjects)(schemaUtils.toIdSchema(schema, fieldId, formData, idPrefix, idSeparator), _idSchema);
    /** Intermediary `onChange` handler for field components that will inject the `id` of the current field into the
```
