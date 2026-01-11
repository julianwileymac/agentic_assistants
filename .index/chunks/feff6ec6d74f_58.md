# Chunk: feff6ec6d74f_58

- source: `.venv-lab/Lib/site-packages/notebook/static/1871.c375ee093b7e51966390.js`
- lines: 2573-2633
- chunk: 59/78

```
 undefined);
            const newFormData = newState.formData;
            const state = {
                formData: newFormData,
                errorSchema: {},
                errors: [],
                schemaValidationErrors: [],
                schemaValidationErrorSchema: {},
            };
            this.setState(state, () => onChange && onChange({ ...this.state, ...state }));
        };
        /** Callback function to handle when a field on the form is blurred. Calls the `onBlur` callback for the `Form` if it
         * was provided.
         *
         * @param id - The unique `id` of the field that was blurred
         * @param data - The data associated with the field that was blurred
         */
        this.onBlur = (id, data) => {
            const { onBlur } = this.props;
            if (onBlur) {
                onBlur(id, data);
            }
        };
        /** Callback function to handle when a field on the form is focused. Calls the `onFocus` callback for the `Form` if it
         * was provided.
         *
         * @param id - The unique `id` of the field that was focused
         * @param data - The data associated with the field that was focused
         */
        this.onFocus = (id, data) => {
            const { onFocus } = this.props;
            if (onFocus) {
                onFocus(id, data);
            }
        };
        /** Callback function to handle when the form is submitted. First, it prevents the default event behavior. Nothing
         * happens if the target and currentTarget of the event are not the same. It will omit any extra data in the
         * `formData` in the state if `omitExtraData` is true. It will validate the resulting `formData`, reporting errors
         * via the `onError()` callback unless validation is disabled. Finally, it will add in any `extraErrors` and then call
         * back the `onSubmit` callback if it was provided.
         *
         * @param event - The submit HTML form event
         */
        this.onSubmit = (event) => {
            event.preventDefault();
            if (event.target !== event.currentTarget) {
                return;
            }
            event.persist();
            const { omitExtraData, extraErrors, noValidate, onSubmit } = this.props;
            let { formData: newFormData } = this.state;
            const { schema, schemaUtils } = this.state;
            if (omitExtraData === true) {
                const retrievedSchema = schemaUtils.retrieveSchema(schema, newFormData);
                const pathSchema = schemaUtils.toPathSchema(retrievedSchema, '', newFormData);
                const fieldNames = this.getFieldNames(pathSchema, newFormData);
                newFormData = this.getUsedFormData(newFormData, fieldNames);
            }
            if (noValidate || this.validateForm()) {
                // There are no errors generated through schema validation.
```
