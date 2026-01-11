# Chunk: feff6ec6d74f_6

- source: `.venv-lab/Lib/site-packages/notebook/static/1871.c375ee093b7e51966390.js`
- lines: 368-428
- chunk: 7/78

```
Props.formData) ? nextProps.formData : [];
        const previousKeyedFormData = prevState.keyedFormData || [];
        const newKeyedFormData = nextFormData.length === previousKeyedFormData.length
            ? previousKeyedFormData.map((previousKeyedFormDatum, index) => {
                return {
                    key: previousKeyedFormDatum.key,
                    item: nextFormData[index],
                };
            })
            : generateKeyedFormData(nextFormData);
        return {
            keyedFormData: newKeyedFormData,
        };
    }
    /** Returns the appropriate title for an item by getting first the title from the schema.items, then falling back to
     * the description from the schema.items, and finally the string "Item"
     */
    get itemTitle() {
        const { schema, registry } = this.props;
        const { translateString } = registry;
        return get_default()(schema, [lib_index_js_.ITEMS_KEY, 'title'], get_default()(schema, [lib_index_js_.ITEMS_KEY, 'description'], translateString(lib_index_js_.TranslatableString.ArrayItemTitle)));
    }
    /** Determines whether the item described in the schema is always required, which is determined by whether any item
     * may be null.
     *
     * @param itemSchema - The schema for the item
     * @return - True if the item schema type does not contain the "null" type
     */
    isItemRequired(itemSchema) {
        if (Array.isArray(itemSchema.type)) {
            // While we don't yet support composite/nullable jsonschema types, it's
            // future-proof to check for requirement against these.
            return !itemSchema.type.includes('null');
        }
        // All non-null array item types are inherently required by design
        return itemSchema.type !== 'null';
    }
    /** Determines whether more items can be added to the array. If the uiSchema indicates the array doesn't allow adding
     * then false is returned. Otherwise, if the schema indicates that there are a maximum number of items and the
     * `formData` matches that value, then false is returned, otherwise true is returned.
     *
     * @param formItems - The list of items in the form
     * @returns - True if the item is addable otherwise false
     */
    canAddItem(formItems) {
        const { schema, uiSchema, registry } = this.props;
        let { addable } = (0,lib_index_js_.getUiOptions)(uiSchema, registry.globalUiOptions);
        if (addable !== false) {
            // if ui:options.addable was not explicitly set to false, we can add
            // another item if we have not exceeded maxItems yet
            if (schema.maxItems !== undefined) {
                addable = formItems.length < schema.maxItems;
            }
            else {
                addable = true;
            }
        }
        return addable;
    }
    /** Callback handler for when the user clicks on the add or add at index buttons. Creates a new row of keyed form data
```
