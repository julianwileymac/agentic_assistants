# Chunk: feff6ec6d74f_62

- source: `.venv-lab/Lib/site-packages/notebook/static/1871.c375ee093b7e51966390.js`
- lines: 2775-2836
- chunk: 63/78

```
ma,
            uiSchema,
            idSchema,
            formData,
            edit,
            errors,
            errorSchema,
            schemaValidationErrors,
            schemaValidationErrorSchema,
            retrievedSchema: _retrievedSchema,
        };
        return nextState;
    }
    /** React lifecycle method that is used to determine whether component should be updated.
     *
     * @param nextProps - The next version of the props
     * @param nextState - The next version of the state
     * @returns - True if the component should be updated, false otherwise
     */
    shouldComponentUpdate(nextProps, nextState) {
        return (0,lib_index_js_.shouldRender)(this, nextProps, nextState);
    }
    /** Validates the `formData` against the `schema` using the `altSchemaUtils` (if provided otherwise it uses the
     * `schemaUtils` in the state), returning the results.
     *
     * @param formData - The new form data to validate
     * @param schema - The schema used to validate against
     * @param altSchemaUtils - The alternate schemaUtils to use for validation
     */
    validate(formData, schema = this.props.schema, altSchemaUtils, retrievedSchema) {
        const schemaUtils = altSchemaUtils ? altSchemaUtils : this.state.schemaUtils;
        const { customValidate, transformErrors, uiSchema } = this.props;
        const resolvedSchema = retrievedSchema !== null && retrievedSchema !== void 0 ? retrievedSchema : schemaUtils.retrieveSchema(schema, formData);
        return schemaUtils
            .getValidator()
            .validateFormData(formData, resolvedSchema, customValidate, transformErrors, uiSchema);
    }
    /** Renders any errors contained in the `state` in using the `ErrorList`, if not disabled by `showErrorList`. */
    renderErrors(registry) {
        const { errors, errorSchema, schema, uiSchema } = this.state;
        const { formContext } = this.props;
        const options = (0,lib_index_js_.getUiOptions)(uiSchema);
        const ErrorListTemplate = (0,lib_index_js_.getTemplate)('ErrorListTemplate', registry, options);
        if (errors && errors.length) {
            return ((0,jsx_runtime.jsx)(ErrorListTemplate, { errors: errors, errorSchema: errorSchema || {}, schema: schema, uiSchema: uiSchema, formContext: formContext, registry: registry }));
        }
        return null;
    }
    /** Returns the registry for the form */
    getRegistry() {
        var _a;
        const { translateString: customTranslateString, uiSchema = {} } = this.props;
        const { schemaUtils } = this.state;
        const { fields, templates, widgets, formContext, translateString } = getDefaultRegistry();
        return {
            fields: { ...fields, ...this.props.fields },
            templates: {
                ...templates,
                ...this.props.templates,
                ButtonTemplates: {
                    ...templates.ButtonTemplates,
```
