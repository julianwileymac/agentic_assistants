# Chunk: feff6ec6d74f_5

- source: `.venv-lab/Lib/site-packages/notebook/static/1871.c375ee093b7e51966390.js`
- lines: 310-373
- chunk: 6/78

```
 newIndex
                    _newKeyedFormData.splice(index, 1);
                    _newKeyedFormData.splice(newIndex, 0, keyedFormData[index]);
                    return _newKeyedFormData;
                }
                const newKeyedFormData = reOrderArray();
                this.setState({
                    keyedFormData: newKeyedFormData,
                }, () => onChange(keyedToPlainFormData(newKeyedFormData), newErrorSchema));
            };
        };
        /** Callback handler used to deal with changing the value of the data in the array at the `index`. Calls the
         * `onChange` callback with the updated form data
         *
         * @param index - The index of the item being changed
         */
        this.onChangeForIndex = (index) => {
            return (value, newErrorSchema, id) => {
                const { formData, onChange, errorSchema } = this.props;
                const arrayData = Array.isArray(formData) ? formData : [];
                const newFormData = arrayData.map((item, i) => {
                    // We need to treat undefined items as nulls to have validation.
                    // See https://github.com/tdegrunt/jsonschema/issues/206
                    const jsonValue = typeof value === 'undefined' ? null : value;
                    return index === i ? jsonValue : item;
                });
                onChange(newFormData, errorSchema &&
                    errorSchema && {
                    ...errorSchema,
                    [index]: newErrorSchema,
                }, id);
            };
        };
        /** Callback handler used to change the value for a checkbox */
        this.onSelectChange = (value) => {
            const { onChange, idSchema } = this.props;
            onChange(value, undefined, idSchema && idSchema.$id);
        };
        const { formData = [] } = props;
        const keyedFormData = generateKeyedFormData(formData);
        this.state = {
            keyedFormData,
            updatedKeyedFormData: false,
        };
    }
    /** React lifecycle method that is called when the props are about to change allowing the state to be updated. It
     * regenerates the keyed form data and returns it
     *
     * @param nextProps - The next set of props data
     * @param prevState - The previous set of state data
     */
    static getDerivedStateFromProps(nextProps, prevState) {
        // Don't call getDerivedStateFromProps if keyed formdata was just updated.
        if (prevState.updatedKeyedFormData) {
            return {
                updatedKeyedFormData: false,
            };
        }
        const nextFormData = Array.isArray(nextProps.formData) ? nextProps.formData : [];
        const previousKeyedFormData = prevState.keyedFormData || [];
        const newKeyedFormData = nextFormData.length === previousKeyedFormData.length
            ? previousKeyedFormData.map((previousKeyedFormDatum, index) => {
                return {
```
