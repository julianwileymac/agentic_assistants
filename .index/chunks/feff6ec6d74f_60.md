# Chunk: feff6ec6d74f_60

- source: `.venv-lab/Lib/site-packages/notebook/static/1871.c375ee093b7e51966390.js`
- lines: 2674-2728
- chunk: 61/78

```
ry.
     */
    getSnapshotBeforeUpdate(prevProps, prevState) {
        if (!(0,lib_index_js_.deepEquals)(this.props, prevProps)) {
            const nextState = this.getStateFromProps(this.props, this.props.formData, prevProps.schema !== this.props.schema ? undefined : this.state.retrievedSchema);
            const shouldUpdate = !(0,lib_index_js_.deepEquals)(nextState, prevState);
            return { nextState, shouldUpdate };
        }
        return { shouldUpdate: false };
    }
    /**
     * `componentDidUpdate` is a React lifecycle method that is invoked immediately after updating occurs. This method is
     * not called for the initial render.
     *
     * Here, it checks if an update is necessary based on the `shouldUpdate` flag received from `getSnapshotBeforeUpdate`.
     * If an update is required, it applies the next state and, if needed, triggers the `onChange` handler to inform about
     * changes.
     *
     * This method effectively replaces the deprecated `UNSAFE_componentWillReceiveProps`, providing a safer alternative
     * to handle prop changes and state updates.
     *
     * @param _ - The previous set of props.
     * @param prevState - The previous state of the component before the update.
     * @param snapshot - The value returned from `getSnapshotBeforeUpdate`.
     */
    componentDidUpdate(_, prevState, snapshot) {
        if (snapshot.shouldUpdate) {
            const { nextState } = snapshot;
            if (!(0,lib_index_js_.deepEquals)(nextState.formData, this.props.formData) &&
                !(0,lib_index_js_.deepEquals)(nextState.formData, prevState.formData) &&
                this.props.onChange) {
                this.props.onChange(nextState);
            }
            this.setState(nextState);
        }
    }
    /** Extracts the updated state from the given `props` and `inputFormData`. As part of this process, the
     * `inputFormData` is first processed to add any missing required defaults. After that, the data is run through the
     * validation process IF required by the `props`.
     *
     * @param props - The props passed to the `Form`
     * @param inputFormData - The new or current data for the `Form`
     * @returns - The new state for the `Form`
     */
    getStateFromProps(props, inputFormData, retrievedSchema) {
        const state = this.state || {};
        const schema = 'schema' in props ? props.schema : this.props.schema;
        const uiSchema = ('uiSchema' in props ? props.uiSchema : this.props.uiSchema) || {};
        const edit = typeof inputFormData !== 'undefined';
        const liveValidate = 'liveValidate' in props ? props.liveValidate : this.props.liveValidate;
        const mustValidate = edit && !props.noValidate && liveValidate;
        const rootSchema = schema;
        const experimental_defaultFormStateBehavior = 'experimental_defaultFormStateBehavior' in props
            ? props.experimental_defaultFormStateBehavior
```
