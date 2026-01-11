# Chunk: feff6ec6d74f_31

- source: `.venv-lab/Lib/site-packages/notebook/static/1871.c375ee093b7e51966390.js`
- lines: 1293-1334
- chunk: 32/78

```
t fieldId = _idSchema[lib_index_js_.ID_KEY];
    const idSchema = (0,lib_index_js_.mergeObjects)(schemaUtils.toIdSchema(schema, fieldId, formData, idPrefix, idSeparator), _idSchema);
    /** Intermediary `onChange` handler for field components that will inject the `id` of the current field into the
     * `onChange` chain if it is not already being provided from a deeper level in the hierarchy
     */
    const handleFieldComponentChange = (0,index_js_.useCallback)((formData, newErrorSchema, id) => {
        const theId = id || fieldId;
        return onChange(formData, newErrorSchema, theId);
    }, [fieldId, onChange]);
    const FieldComponent = getFieldComponent(schema, uiOptions, idSchema, registry);
    const disabled = Boolean(props.disabled || uiOptions.disabled);
    const readonly = Boolean(props.readonly || uiOptions.readonly || props.schema.readOnly || schema.readOnly);
    const uiSchemaHideError = uiOptions.hideError;
    // Set hideError to the value provided in the uiSchema, otherwise stick with the prop to propagate to children
    const hideError = uiSchemaHideError === undefined ? props.hideError : Boolean(uiSchemaHideError);
    const autofocus = Boolean(props.autofocus || uiOptions.autofocus);
    if (Object.keys(schema).length === 0) {
        return null;
    }
    const displayLabel = schemaUtils.getDisplayLabel(schema, uiSchema, globalUiOptions);
    const { __errors, ...fieldErrorSchema } = errorSchema || {};
    // See #439: uiSchema: Don't pass consumed class names or style to child components
    const fieldUiSchema = omit_default()(uiSchema, ['ui:classNames', 'classNames', 'ui:style']);
    if (lib_index_js_.UI_OPTIONS_KEY in fieldUiSchema) {
        fieldUiSchema[lib_index_js_.UI_OPTIONS_KEY] = omit_default()(fieldUiSchema[lib_index_js_.UI_OPTIONS_KEY], ['classNames', 'style']);
    }
    const field = ((0,jsx_runtime.jsx)(FieldComponent, { ...props, onChange: handleFieldComponentChange, idSchema: idSchema, schema: schema, uiSchema: fieldUiSchema, disabled: disabled, readonly: readonly, hideError: hideError, autofocus: autofocus, errorSchema: fieldErrorSchema, formContext: formContext, rawErrors: __errors }));
    const id = idSchema[lib_index_js_.ID_KEY];
    // If this schema has a title defined, but the user has set a new key/label, retain their input.
    let label;
    if (wasPropertyKeyModified) {
        label = name;
    }
    else {
        label = lib_index_js_.ADDITIONAL_PROPERTY_FLAG in schema ? name : uiOptions.title || props.schema.title || schema.title || name;
    }
    const description = uiOptions.description || props.schema.description || schema.description || '';
    const richDescription = uiOptions.enableMarkdownInDescription ? (0,jsx_runtime.jsx)(index_modern, { children: description }) : description;
    const help = uiOptions.help;
    const hidden = uiOptions.widget === 'hidden';
    const classNames = ['form-group', 'field', `field-${(0,lib_index_js_.getSchemaType)(schema)}`];
```
