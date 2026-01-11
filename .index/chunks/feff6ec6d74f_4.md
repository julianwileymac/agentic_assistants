# Chunk: feff6ec6d74f_4

- source: `.venv-lab/Lib/site-packages/notebook/static/1871.c375ee093b7e51966390.js`
- lines: 254-317
- chunk: 5/78

```
.state;
                // refs #195: revalidate to ensure properly reindexing errors
                let newErrorSchema;
                if (errorSchema) {
                    newErrorSchema = {};
                    for (const idx in errorSchema) {
                        const i = parseInt(idx);
                        if (i < index) {
                            set_default()(newErrorSchema, [i], errorSchema[idx]);
                        }
                        else if (i > index) {
                            set_default()(newErrorSchema, [i - 1], errorSchema[idx]);
                        }
                    }
                }
                const newKeyedFormData = keyedFormData.filter((_, i) => i !== index);
                this.setState({
                    keyedFormData: newKeyedFormData,
                    updatedKeyedFormData: true,
                }, () => onChange(keyedToPlainFormData(newKeyedFormData), newErrorSchema));
            };
        };
        /** Callback handler for when the user clicks on one of the move item buttons on an existing array element. Moves the
         * row of keyed form data at the `index` to the `newIndex` in the state, and then returning `onChange()` with the
         * plain form data converted from the keyed data
         *
         * @param index - The index of the item to move
         * @param newIndex - The index to where the item is to be moved
         */
        this.onReorderClick = (index, newIndex) => {
            return (event) => {
                if (event) {
                    event.preventDefault();
                    event.currentTarget.blur();
                }
                const { onChange, errorSchema } = this.props;
                let newErrorSchema;
                if (errorSchema) {
                    newErrorSchema = {};
                    for (const idx in errorSchema) {
                        const i = parseInt(idx);
                        if (i == index) {
                            set_default()(newErrorSchema, [newIndex], errorSchema[index]);
                        }
                        else if (i == newIndex) {
                            set_default()(newErrorSchema, [index], errorSchema[newIndex]);
                        }
                        else {
                            set_default()(newErrorSchema, [idx], errorSchema[i]);
                        }
                    }
                }
                const { keyedFormData } = this.state;
                function reOrderArray() {
                    // Copy item
                    const _newKeyedFormData = keyedFormData.slice();
                    // Moves item from index to newIndex
                    _newKeyedFormData.splice(index, 1);
                    _newKeyedFormData.splice(newIndex, 0, keyedFormData[index]);
                    return _newKeyedFormData;
                }
                const newKeyedFormData = reOrderArray();
                this.setState({
```
