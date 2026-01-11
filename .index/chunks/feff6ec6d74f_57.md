# Chunk: feff6ec6d74f_57

- source: `.venv-lab/Lib/site-packages/notebook/static/1871.c375ee093b7e51966390.js`
- lines: 2515-2582
- chunk: 58/78

```
getStateFromProps(this.props, formData, retrievedSchema);
                formData = newState.formData;
            }
            const mustValidate = !noValidate && liveValidate;
            let state = { formData, schema };
            let newFormData = formData;
            let _retrievedSchema;
            if (omitExtraData === true && liveOmit === true) {
                _retrievedSchema = schemaUtils.retrieveSchema(schema, formData);
                const pathSchema = schemaUtils.toPathSchema(_retrievedSchema, '', formData);
                const fieldNames = this.getFieldNames(pathSchema, formData);
                newFormData = this.getUsedFormData(formData, fieldNames);
                state = {
                    formData: newFormData,
                };
            }
            if (mustValidate) {
                const schemaValidation = this.validate(newFormData, schema, schemaUtils, retrievedSchema);
                let errors = schemaValidation.errors;
                let errorSchema = schemaValidation.errorSchema;
                const schemaValidationErrors = errors;
                const schemaValidationErrorSchema = errorSchema;
                if (extraErrors) {
                    const merged = (0,lib_index_js_.validationDataMerge)(schemaValidation, extraErrors);
                    errorSchema = merged.errorSchema;
                    errors = merged.errors;
                }
                state = {
                    formData: newFormData,
                    errors,
                    errorSchema,
                    schemaValidationErrors,
                    schemaValidationErrorSchema,
                };
            }
            else if (!noValidate && newErrorSchema) {
                const errorSchema = extraErrors
                    ? (0,lib_index_js_.mergeObjects)(newErrorSchema, extraErrors, 'preventDuplicates')
                    : newErrorSchema;
                state = {
                    formData: newFormData,
                    errorSchema: errorSchema,
                    errors: (0,lib_index_js_.toErrorList)(errorSchema),
                };
            }
            if (_retrievedSchema) {
                state.retrievedSchema = _retrievedSchema;
            }
            this.setState(state, () => onChange && onChange({ ...this.state, ...state }, id));
        };
        /**
         * Callback function to handle reset form data.
         * - Reset all fields with default values.
         * - Reset validations and errors
         *
         */
        this.reset = () => {
            const { onChange } = this.props;
            const newState = this.getStateFromProps(this.props, undefined);
            const newFormData = newState.formData;
            const state = {
                formData: newFormData,
                errorSchema: {},
                errors: [],
                schemaValidationErrors: [],
                schemaValidationErrorSchema: {},
            };
```
