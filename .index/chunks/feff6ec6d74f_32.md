# Chunk: feff6ec6d74f_32

- source: `.venv-lab/Lib/site-packages/notebook/static/1871.c375ee093b7e51966390.js`
- lines: 1330-1379
- chunk: 33/78

```
 uiOptions.enableMarkdownInDescription ? (0,jsx_runtime.jsx)(index_modern, { children: description }) : description;
    const help = uiOptions.help;
    const hidden = uiOptions.widget === 'hidden';
    const classNames = ['form-group', 'field', `field-${(0,lib_index_js_.getSchemaType)(schema)}`];
    if (!hideError && __errors && __errors.length > 0) {
        classNames.push('field-error has-error has-danger');
    }
    if (uiSchema === null || uiSchema === void 0 ? void 0 : uiSchema.classNames) {
        if (false) {}
        classNames.push(uiSchema.classNames);
    }
    if (uiOptions.classNames) {
        classNames.push(uiOptions.classNames);
    }
    const helpComponent = ((0,jsx_runtime.jsx)(FieldHelpTemplate, { help: help, idSchema: idSchema, schema: schema, uiSchema: uiSchema, hasErrors: !hideError && __errors && __errors.length > 0, registry: registry }));
    /*
     * AnyOf/OneOf errors handled by child schema
     * unless it can be rendered as select control
     */
    const errorsComponent = hideError || ((schema.anyOf || schema.oneOf) && !schemaUtils.isSelect(schema)) ? undefined : ((0,jsx_runtime.jsx)(FieldErrorTemplate, { errors: __errors, errorSchema: errorSchema, idSchema: idSchema, schema: schema, uiSchema: uiSchema, registry: registry }));
    const fieldProps = {
        description: ((0,jsx_runtime.jsx)(DescriptionFieldTemplate, { id: (0,lib_index_js_.descriptionId)(id), description: richDescription, schema: schema, uiSchema: uiSchema, registry: registry })),
        rawDescription: description,
        help: helpComponent,
        rawHelp: typeof help === 'string' ? help : undefined,
        errors: errorsComponent,
        rawErrors: hideError ? undefined : __errors,
        id,
        label,
        hidden,
        onChange,
        onKeyChange,
        onDropPropertyClick,
        required,
        disabled,
        readonly,
        hideError,
        displayLabel,
        classNames: classNames.join(' ').trim(),
        style: uiOptions.style,
        formContext,
        formData,
        schema,
        uiSchema,
        registry,
    };
    const _AnyOfField = registry.fields.AnyOfField;
    const _OneOfField = registry.fields.OneOfField;
    const isReplacingAnyOrOneOf = (uiSchema === null || uiSchema === void 0 ? void 0 : uiSchema['ui:field']) && (uiSchema === null || uiSchema === void 0 ? void 0 : uiSchema['ui:fieldReplacesAnyOrOneOf']) === true;
```
