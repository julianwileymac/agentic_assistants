# Chunk: feff6ec6d74f_63

- source: `.venv-lab/Lib/site-packages/notebook/static/1871.c375ee093b7e51966390.js`
- lines: 2828-2895
- chunk: 64/78

```
t, translateString } = getDefaultRegistry();
        return {
            fields: { ...fields, ...this.props.fields },
            templates: {
                ...templates,
                ...this.props.templates,
                ButtonTemplates: {
                    ...templates.ButtonTemplates,
                    ...(_a = this.props.templates) === null || _a === void 0 ? void 0 : _a.ButtonTemplates,
                },
            },
            widgets: { ...widgets, ...this.props.widgets },
            rootSchema: this.props.schema,
            formContext: this.props.formContext || formContext,
            schemaUtils,
            translateString: customTranslateString || translateString,
            globalUiOptions: uiSchema[lib_index_js_.UI_GLOBAL_OPTIONS_KEY],
        };
    }
    /** Provides a function that can be used to programmatically submit the `Form` */
    submit() {
        if (this.formElement.current) {
            this.formElement.current.dispatchEvent(new CustomEvent('submit', {
                cancelable: true,
            }));
            this.formElement.current.requestSubmit();
        }
    }
    /** Attempts to focus on the field associated with the `error`. Uses the `property` field to compute path of the error
     * field, then, using the `idPrefix` and `idSeparator` converts that path into an id. Then the input element with that
     * id is attempted to be found using the `formElement` ref. If it is located, then it is focused.
     *
     * @param error - The error on which to focus
     */
    focusOnError(error) {
        const { idPrefix = 'root', idSeparator = '_' } = this.props;
        const { property } = error;
        const path = toPath_default()(property);
        if (path[0] === '') {
            // Most of the time the `.foo` property results in the first element being empty, so replace it with the idPrefix
            path[0] = idPrefix;
        }
        else {
            // Otherwise insert the idPrefix into the first location using unshift
            path.unshift(idPrefix);
        }
        const elementId = path.join(idSeparator);
        let field = this.formElement.current.elements[elementId];
        if (!field) {
            // if not an exact match, try finding an input starting with the element id (like radio buttons or checkboxes)
            field = this.formElement.current.querySelector(`input[id^=${elementId}`);
        }
        if (field && field.length) {
            // If we got a list with length > 0
            field = field[0];
        }
        if (field) {
            field.focus();
        }
    }
    /** Programmatically validate the form. If `onError` is provided, then it will be called with the list of errors the
     * same way as would happen on form submission.
     *
     * @returns - True if the form is valid, false otherwise.
     */
    validateForm() {
        const { extraErrors, extraErrorsBlockSubmit, focusOnFirstError, onError } = this.props;
```
