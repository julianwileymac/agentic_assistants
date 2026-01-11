# Chunk: feff6ec6d74f_3

- source: `.venv-lab/Lib/site-packages/notebook/static/1871.c375ee093b7e51966390.js`
- lines: 198-261
- chunk: 4/78

```
** Callback handler for when the user clicks on the copy button on an existing array element. Clones the row of
         * keyed form data at the `index` into the next position in the state, and then returning `onChange()` with the plain
         * form data converted from the keyed data
         *
         * @param index - The index at which the copy button is clicked
         */
        this.onCopyIndexClick = (index) => {
            return (event) => {
                if (event) {
                    event.preventDefault();
                }
                const { onChange, errorSchema } = this.props;
                const { keyedFormData } = this.state;
                // refs #195: revalidate to ensure properly reindexing errors
                let newErrorSchema;
                if (errorSchema) {
                    newErrorSchema = {};
                    for (const idx in errorSchema) {
                        const i = parseInt(idx);
                        if (i <= index) {
                            set_default()(newErrorSchema, [i], errorSchema[idx]);
                        }
                        else if (i > index) {
                            set_default()(newErrorSchema, [i + 1], errorSchema[idx]);
                        }
                    }
                }
                const newKeyedFormDataRow = {
                    key: generateRowId(),
                    item: cloneDeep_default()(keyedFormData[index].item),
                };
                const newKeyedFormData = [...keyedFormData];
                if (index !== undefined) {
                    newKeyedFormData.splice(index + 1, 0, newKeyedFormDataRow);
                }
                else {
                    newKeyedFormData.push(newKeyedFormDataRow);
                }
                this.setState({
                    keyedFormData: newKeyedFormData,
                    updatedKeyedFormData: true,
                }, () => onChange(keyedToPlainFormData(newKeyedFormData), newErrorSchema));
            };
        };
        /** Callback handler for when the user clicks on the remove button on an existing array element. Removes the row of
         * keyed form data at the `index` in the state, and then returning `onChange()` with the plain form data converted
         * from the keyed data
         *
         * @param index - The index at which the remove button is clicked
         */
        this.onDropIndexClick = (index) => {
            return (event) => {
                if (event) {
                    event.preventDefault();
                }
                const { onChange, errorSchema } = this.props;
                const { keyedFormData } = this.state;
                // refs #195: revalidate to ensure properly reindexing errors
                let newErrorSchema;
                if (errorSchema) {
                    newErrorSchema = {};
                    for (const idx in errorSchema) {
                        const i = parseInt(idx);
```
