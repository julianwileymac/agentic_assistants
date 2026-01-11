# Chunk: feff6ec6d74f_7

- source: `.venv-lab/Lib/site-packages/notebook/static/1871.c375ee093b7e51966390.js`
- lines: 419-484
- chunk: 8/78

```
            addable = formItems.length < schema.maxItems;
            }
            else {
                addable = true;
            }
        }
        return addable;
    }
    /** Callback handler for when the user clicks on the add or add at index buttons. Creates a new row of keyed form data
     * either at the end of the list (when index is not specified) or inserted at the `index` when it is, adding it into
     * the state, and then returning `onChange()` with the plain form data converted from the keyed data
     *
     * @param event - The event for the click
     * @param [index] - The optional index at which to add the new data
     */
    _handleAddClick(event, index) {
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
                if (index === undefined || i < index) {
                    set_default()(newErrorSchema, [i], errorSchema[idx]);
                }
                else if (i >= index) {
                    set_default()(newErrorSchema, [i + 1], errorSchema[idx]);
                }
            }
        }
        const newKeyedFormDataRow = {
            key: generateRowId(),
            item: this._getNewFormDataRow(),
        };
        const newKeyedFormData = [...keyedFormData];
        if (index !== undefined) {
            newKeyedFormData.splice(index, 0, newKeyedFormDataRow);
        }
        else {
            newKeyedFormData.push(newKeyedFormDataRow);
        }
        this.setState({
            keyedFormData: newKeyedFormData,
            updatedKeyedFormData: true,
        }, () => onChange(keyedToPlainFormData(newKeyedFormData), newErrorSchema));
    }
    /** Renders the `ArrayField` depending on the specific needs of the schema and uischema elements
     */
    render() {
        const { schema, uiSchema, idSchema, registry } = this.props;
        const { schemaUtils, translateString } = registry;
        if (!(lib_index_js_.ITEMS_KEY in schema)) {
            const uiOptions = (0,lib_index_js_.getUiOptions)(uiSchema);
            const UnsupportedFieldTemplate = (0,lib_index_js_.getTemplate)('UnsupportedFieldTemplate', registry, uiOptions);
            return ((0,jsx_runtime.jsx)(UnsupportedFieldTemplate, { schema: schema, idSchema: idSchema, reason: translateString(lib_index_js_.TranslatableString.MissingItems), registry: registry }));
        }
        if (schemaUtils.isMultiSelect(schema)) {
            // If array has enum or uniqueItems set to true, call renderMultiSelect() to render the default multiselect widget or a custom widget, if specified.
            return this.renderMultiSelect();
        }
```
