# Chunk: feff6ec6d74f_61

- source: `.venv-lab/Lib/site-packages/notebook/static/1871.c375ee093b7e51966390.js`
- lines: 2723-2788
- chunk: 62/78

```
date : this.props.liveValidate;
        const mustValidate = edit && !props.noValidate && liveValidate;
        const rootSchema = schema;
        const experimental_defaultFormStateBehavior = 'experimental_defaultFormStateBehavior' in props
            ? props.experimental_defaultFormStateBehavior
            : this.props.experimental_defaultFormStateBehavior;
        let schemaUtils = state.schemaUtils;
        if (!schemaUtils ||
            schemaUtils.doesSchemaUtilsDiffer(props.validator, rootSchema, experimental_defaultFormStateBehavior)) {
            schemaUtils = (0,lib_index_js_.createSchemaUtils)(props.validator, rootSchema, experimental_defaultFormStateBehavior);
        }
        const formData = schemaUtils.getDefaultFormState(schema, inputFormData);
        const _retrievedSchema = retrievedSchema !== null && retrievedSchema !== void 0 ? retrievedSchema : schemaUtils.retrieveSchema(schema, formData);
        const getCurrentErrors = () => {
            if (props.noValidate) {
                return { errors: [], errorSchema: {} };
            }
            else if (!props.liveValidate) {
                return {
                    errors: state.schemaValidationErrors || [],
                    errorSchema: state.schemaValidationErrorSchema || {},
                };
            }
            return {
                errors: state.errors || [],
                errorSchema: state.errorSchema || {},
            };
        };
        let errors;
        let errorSchema;
        let schemaValidationErrors = state.schemaValidationErrors;
        let schemaValidationErrorSchema = state.schemaValidationErrorSchema;
        if (mustValidate) {
            const schemaValidation = this.validate(formData, schema, schemaUtils, _retrievedSchema);
            errors = schemaValidation.errors;
            errorSchema = schemaValidation.errorSchema;
            schemaValidationErrors = errors;
            schemaValidationErrorSchema = errorSchema;
        }
        else {
            const currentErrors = getCurrentErrors();
            errors = currentErrors.errors;
            errorSchema = currentErrors.errorSchema;
        }
        if (props.extraErrors) {
            const merged = (0,lib_index_js_.validationDataMerge)({ errorSchema, errors }, props.extraErrors);
            errorSchema = merged.errorSchema;
            errors = merged.errors;
        }
        const idSchema = schemaUtils.toIdSchema(_retrievedSchema, uiSchema['ui:rootFieldId'], formData, props.idPrefix, props.idSeparator);
        const nextState = {
            schemaUtils,
            schema,
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
```
