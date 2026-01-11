# Chunk: feff6ec6d74f_64

- source: `.venv-lab/Lib/site-packages/notebook/static/1871.c375ee093b7e51966390.js`
- lines: 2888-2951
- chunk: 65/78

```
d, then it will be called with the list of errors the
     * same way as would happen on form submission.
     *
     * @returns - True if the form is valid, false otherwise.
     */
    validateForm() {
        const { extraErrors, extraErrorsBlockSubmit, focusOnFirstError, onError } = this.props;
        const { formData, errors: prevErrors } = this.state;
        const schemaValidation = this.validate(formData);
        let errors = schemaValidation.errors;
        let errorSchema = schemaValidation.errorSchema;
        const schemaValidationErrors = errors;
        const schemaValidationErrorSchema = errorSchema;
        const hasError = errors.length > 0 || (extraErrors && extraErrorsBlockSubmit);
        if (hasError) {
            if (extraErrors) {
                const merged = (0,lib_index_js_.validationDataMerge)(schemaValidation, extraErrors);
                errorSchema = merged.errorSchema;
                errors = merged.errors;
            }
            if (focusOnFirstError) {
                if (typeof focusOnFirstError === 'function') {
                    focusOnFirstError(errors[0]);
                }
                else {
                    this.focusOnError(errors[0]);
                }
            }
            this.setState({
                errors,
                errorSchema,
                schemaValidationErrors,
                schemaValidationErrorSchema,
            }, () => {
                if (onError) {
                    onError(errors);
                }
                else {
                    console.error('Form validation failed', errors);
                }
            });
        }
        else if (prevErrors.length > 0) {
            this.setState({
                errors: [],
                errorSchema: {},
                schemaValidationErrors: [],
                schemaValidationErrorSchema: {},
            });
        }
        return !hasError;
    }
    /** Renders the `Form` fields inside the <form> | `tagName` or `_internalFormWrapper`, rendering any errors if
     * needed along with the submit button or any children of the form.
     */
    render() {
        const { children, id, idPrefix, idSeparator, className = '', tagName, name, method, target, action, autoComplete, enctype, acceptcharset, noHtml5Validate = false, disabled = false, readonly = false, formContext, showErrorList = 'top', _internalFormWrapper, } = this.props;
        const { schema, uiSchema, formData, errorSchema, idSchema } = this.state;
        const registry = this.getRegistry();
        const { SchemaField: _SchemaField } = registry.fields;
        const { SubmitButton } = registry.templates.ButtonTemplates;
        // The `semantic-ui` and `material-ui` themes have `_internalFormWrapper`s that take an `as` prop that is the
        // PropTypes.elementType to use for the inner tag, so we'll need to pass `tagName` along if it is provided.
```
