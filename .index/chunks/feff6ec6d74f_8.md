# Chunk: feff6ec6d74f_8

- source: `.venv-lab/Lib/site-packages/notebook/static/1871.c375ee093b7e51966390.js`
- lines: 478-537
- chunk: 9/78

```
 registry: registry }));
        }
        if (schemaUtils.isMultiSelect(schema)) {
            // If array has enum or uniqueItems set to true, call renderMultiSelect() to render the default multiselect widget or a custom widget, if specified.
            return this.renderMultiSelect();
        }
        if ((0,lib_index_js_.isCustomWidget)(uiSchema)) {
            return this.renderCustomWidget();
        }
        if ((0,lib_index_js_.isFixedItems)(schema)) {
            return this.renderFixedArray();
        }
        if (schemaUtils.isFilesArray(schema, uiSchema)) {
            return this.renderFiles();
        }
        return this.renderNormalArray();
    }
    /** Renders a normal array without any limitations of length
     */
    renderNormalArray() {
        const { schema, uiSchema = {}, errorSchema, idSchema, name, disabled = false, readonly = false, autofocus = false, required = false, registry, onBlur, onFocus, idPrefix, idSeparator = '_', rawErrors, } = this.props;
        const { keyedFormData } = this.state;
        const title = schema.title === undefined ? name : schema.title;
        const { schemaUtils, formContext } = registry;
        const uiOptions = (0,lib_index_js_.getUiOptions)(uiSchema);
        const _schemaItems = isObject_default()(schema.items) ? schema.items : {};
        const itemsSchema = schemaUtils.retrieveSchema(_schemaItems);
        const formData = keyedToPlainFormData(this.state.keyedFormData);
        const canAdd = this.canAddItem(formData);
        const arrayProps = {
            canAdd,
            items: keyedFormData.map((keyedItem, index) => {
                const { key, item } = keyedItem;
                // While we are actually dealing with a single item of type T, the types require a T[], so cast
                const itemCast = item;
                const itemSchema = schemaUtils.retrieveSchema(_schemaItems, itemCast);
                const itemErrorSchema = errorSchema ? errorSchema[index] : undefined;
                const itemIdPrefix = idSchema.$id + idSeparator + index;
                const itemIdSchema = schemaUtils.toIdSchema(itemSchema, itemIdPrefix, itemCast, idPrefix, idSeparator);
                return this.renderArrayFieldItem({
                    key,
                    index,
                    name: name && `${name}-${index}`,
                    canAdd,
                    canMoveUp: index > 0,
                    canMoveDown: index < formData.length - 1,
                    itemSchema,
                    itemIdSchema,
                    itemErrorSchema,
                    itemData: itemCast,
                    itemUiSchema: uiSchema.items,
                    autofocus: autofocus && index === 0,
                    onBlur,
                    onFocus,
                    rawErrors,
                    totalItems: keyedFormData.length,
                });
            }),
            className: `field field-array field-array-of-${itemsSchema.type}`,
```
