# Chunk: feff6ec6d74f_29

- source: `.venv-lab/Lib/site-packages/notebook/static/1871.c375ee093b7e51966390.js`
- lines: 1195-1256
- chunk: 30/78

```
  const fieldUiSchema = addedByAdditionalProperties ? uiSchema.additionalProperties : uiSchema[name];
                const hidden = (0,lib_index_js_.getUiOptions)(fieldUiSchema).widget === 'hidden';
                const fieldIdSchema = get_default()(idSchema, [name], {});
                return {
                    content: ((0,jsx_runtime.jsx)(SchemaField, { name: name, required: this.isRequired(name), schema: get_default()(schema, [lib_index_js_.PROPERTIES_KEY, name], {}), uiSchema: fieldUiSchema, errorSchema: get_default()(errorSchema, name), idSchema: fieldIdSchema, idPrefix: idPrefix, idSeparator: idSeparator, formData: get_default()(formData, name), formContext: formContext, wasPropertyKeyModified: this.state.wasPropertyKeyModified, onKeyChange: this.onKeyChange(name), onChange: this.onPropertyChange(name, addedByAdditionalProperties), onBlur: onBlur, onFocus: onFocus, registry: registry, disabled: disabled, readonly: readonly, hideError: hideError, onDropPropertyClick: this.onDropPropertyClick }, name)),
                    name,
                    readonly,
                    disabled,
                    required,
                    hidden,
                };
            }),
            readonly,
            disabled,
            required,
            idSchema,
            uiSchema,
            errorSchema,
            schema,
            formData,
            formContext,
            registry,
        };
        return (0,jsx_runtime.jsx)(Template, { ...templateProps, onAddClick: this.handleAddClick });
    }
}
/* harmony default export */ const fields_ObjectField = (ObjectField);
//# sourceMappingURL=ObjectField.js.map
;// CONCATENATED MODULE: ../node_modules/@rjsf/core/lib/components/fields/SchemaField.js






/** The map of component type to FieldName */
const COMPONENT_TYPES = {
    array: 'ArrayField',
    boolean: 'BooleanField',
    integer: 'NumberField',
    number: 'NumberField',
    object: 'ObjectField',
    string: 'StringField',
    null: 'NullField',
};
/** Computes and returns which `Field` implementation to return in order to render the field represented by the
 * `schema`. The `uiOptions` are used to alter what potential `Field` implementation is actually returned. If no
 * appropriate `Field` implementation can be found then a wrapper around `UnsupportedFieldTemplate` is used.
 *
 * @param schema - The schema from which to obtain the type
 * @param uiOptions - The UI Options that may affect the component decision
 * @param idSchema - The id that is passed to the `UnsupportedFieldTemplate`
 * @param registry - The registry from which fields and templates are obtained
 * @returns - The `Field` component that is used to render the actual field data
 */
function getFieldComponent(schema, uiOptions, idSchema, registry) {
    const field = uiOptions.field;
    const { fields, translateString } = registry;
    if (typeof field === 'function') {
        return field;
    }
```
