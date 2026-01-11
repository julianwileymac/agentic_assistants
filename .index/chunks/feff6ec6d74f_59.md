# Chunk: feff6ec6d74f_59

- source: `.venv-lab/Lib/site-packages/notebook/static/1871.c375ee093b7e51966390.js`
- lines: 2628-2679
- chunk: 60/78

```
                const fieldNames = this.getFieldNames(pathSchema, newFormData);
                newFormData = this.getUsedFormData(newFormData, fieldNames);
            }
            if (noValidate || this.validateForm()) {
                // There are no errors generated through schema validation.
                // Check for user provided errors and update state accordingly.
                const errorSchema = extraErrors || {};
                const errors = extraErrors ? (0,lib_index_js_.toErrorList)(extraErrors) : [];
                this.setState({
                    formData: newFormData,
                    errors,
                    errorSchema,
                    schemaValidationErrors: [],
                    schemaValidationErrorSchema: {},
                }, () => {
                    if (onSubmit) {
                        onSubmit({ ...this.state, formData: newFormData, status: 'submitted' }, event);
                    }
                });
            }
        };
        if (!props.validator) {
            throw new Error('A validator is required for Form functionality to work');
        }
        this.state = this.getStateFromProps(props, props.formData);
        if (this.props.onChange && !(0,lib_index_js_.deepEquals)(this.state.formData, this.props.formData)) {
            this.props.onChange(this.state);
        }
        this.formElement = (0,index_js_.createRef)();
    }
    /**
     * `getSnapshotBeforeUpdate` is a React lifecycle method that is invoked right before the most recently rendered
     * output is committed to the DOM. It enables your component to capture current values (e.g., scroll position) before
     * they are potentially changed.
     *
     * In this case, it checks if the props have changed since the last render. If they have, it computes the next state
     * of the component using `getStateFromProps` method and returns it along with a `shouldUpdate` flag set to `true` IF
     * the `nextState` and `prevState` are different, otherwise `false`. This ensures that we have the most up-to-date
     * state ready to be applied in `componentDidUpdate`.
     *
     * If `formData` hasn't changed, it simply returns an object with `shouldUpdate` set to `false`, indicating that a
     * state update is not necessary.
     *
     * @param prevProps - The previous set of props before the update.
     * @param prevState - The previous state before the update.
     * @returns Either an object containing the next state and a flag indicating that an update should occur, or an object
     *        with a flag indicating that an update is not necessary.
     */
    getSnapshotBeforeUpdate(prevProps, prevState) {
        if (!(0,lib_index_js_.deepEquals)(this.props, prevProps)) {
            const nextState = this.getStateFromProps(this.props, this.props.formData, prevProps.schema !== this.props.schema ? undefined : this.state.retrievedSchema);
```
