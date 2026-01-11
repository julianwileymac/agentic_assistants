# Chunk: feff6ec6d74f_34

- source: `.venv-lab/Lib/site-packages/notebook/static/1871.c375ee093b7e51966390.js`
- lines: 1405-1470
- chunk: 35/78

```
dgets, formContext, schemaUtils, globalUiOptions } = registry;
    const enumOptions = schemaUtils.isSelect(schema) ? (0,lib_index_js_.optionsList)(schema) : undefined;
    let defaultWidget = enumOptions ? 'select' : 'text';
    if (format && (0,lib_index_js_.hasWidget)(schema, format, widgets)) {
        defaultWidget = format;
    }
    const { widget = defaultWidget, placeholder = '', title: uiTitle, ...options } = (0,lib_index_js_.getUiOptions)(uiSchema);
    const displayLabel = schemaUtils.getDisplayLabel(schema, uiSchema, globalUiOptions);
    const label = (_a = uiTitle !== null && uiTitle !== void 0 ? uiTitle : title) !== null && _a !== void 0 ? _a : name;
    const Widget = (0,lib_index_js_.getWidget)(schema, widget, widgets);
    return ((0,jsx_runtime.jsx)(Widget, { options: { ...options, enumOptions }, schema: schema, uiSchema: uiSchema, id: idSchema.$id, name: name, label: label, hideLabel: !displayLabel, hideError: hideError, value: formData, onChange: onChange, onBlur: onBlur, onFocus: onFocus, required: required, disabled: disabled, readonly: readonly, formContext: formContext, autofocus: autofocus, registry: registry, placeholder: placeholder, rawErrors: rawErrors }));
}
/* harmony default export */ const fields_StringField = (StringField);
//# sourceMappingURL=StringField.js.map
;// CONCATENATED MODULE: ../node_modules/@rjsf/core/lib/components/fields/NullField.js

/** The `NullField` component is used to render a field in the schema is null. It also ensures that the `formData` is
 * also set to null if it has no value.
 *
 * @param props - The `FieldProps` for this template
 */
function NullField(props) {
    const { formData, onChange } = props;
    (0,index_js_.useEffect)(() => {
        if (formData === undefined) {
            onChange(null);
        }
    }, [formData, onChange]);
    return null;
}
/* harmony default export */ const fields_NullField = (NullField);
//# sourceMappingURL=NullField.js.map
;// CONCATENATED MODULE: ../node_modules/@rjsf/core/lib/components/fields/index.js








function fields() {
    return {
        AnyOfField: MultiSchemaField,
        ArrayField: fields_ArrayField,
        // ArrayField falls back to SchemaField if ArraySchemaField is not defined, which it isn't by default
        BooleanField: fields_BooleanField,
        NumberField: fields_NumberField,
        ObjectField: fields_ObjectField,
        OneOfField: MultiSchemaField,
        SchemaField: fields_SchemaField,
        StringField: fields_StringField,
        NullField: fields_NullField,
    };
}
/* harmony default export */ const components_fields = (fields);
//# sourceMappingURL=index.js.map
;// CONCATENATED MODULE: ../node_modules/@rjsf/core/lib/components/templates/ArrayFieldDescriptionTemplate.js


/** The `ArrayFieldDescriptionTemplate` component renders a `DescriptionFieldTemplate` with an `id` derived from
 * the `idSchema`.
 *
 * @param props - The `ArrayFieldDescriptionProps` for the component
 */
```
