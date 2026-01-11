# Chunk: feff6ec6d74f_26

- source: `.venv-lab/Lib/site-packages/notebook/static/1871.c375ee093b7e51966390.js`
- lines: 1044-1106
- chunk: 27/78

```
turns a callback to handle the onDropPropertyClick event for the given `key` which removes the old `key` data
         * and calls the `onChange` callback with it
         *
         * @param key - The key for which the drop callback is desired
         * @returns - The drop property click callback
         */
        this.onDropPropertyClick = (key) => {
            return (event) => {
                event.preventDefault();
                const { onChange, formData } = this.props;
                const copiedFormData = { ...formData };
                unset_default()(copiedFormData, key);
                onChange(copiedFormData);
            };
        };
        /** Computes the next available key name from the `preferredKey`, indexing through the already existing keys until one
         * that is already not assigned is found.
         *
         * @param preferredKey - The preferred name of a new key
         * @param [formData] - The form data in which to check if the desired key already exists
         * @returns - The name of the next available key from `preferredKey`
         */
        this.getAvailableKey = (preferredKey, formData) => {
            const { uiSchema, registry } = this.props;
            const { duplicateKeySuffixSeparator = '-' } = (0,lib_index_js_.getUiOptions)(uiSchema, registry.globalUiOptions);
            let index = 0;
            let newKey = preferredKey;
            while (has_default()(formData, newKey)) {
                newKey = `${preferredKey}${duplicateKeySuffixSeparator}${++index}`;
            }
            return newKey;
        };
        /** Returns a callback function that deals with the rename of a key for an additional property for a schema. That
         * callback will attempt to rename the key and move the existing data to that key, calling `onChange` when it does.
         *
         * @param oldValue - The old value of a field
         * @returns - The key change callback function
         */
        this.onKeyChange = (oldValue) => {
            return (value, newErrorSchema) => {
                if (oldValue === value) {
                    return;
                }
                const { formData, onChange, errorSchema } = this.props;
                value = this.getAvailableKey(value, formData);
                const newFormData = {
                    ...formData,
                };
                const newKeys = { [oldValue]: value };
                const keyValues = Object.keys(newFormData).map((key) => {
                    const newKey = newKeys[key] || key;
                    return { [newKey]: newFormData[key] };
                });
                const renamedObj = Object.assign({}, ...keyValues);
                this.setState({ wasPropertyKeyModified: true });
                onChange(renamedObj, errorSchema &&
                    errorSchema && {
                    ...errorSchema,
                    [value]: newErrorSchema,
                });
            };
        };
```
