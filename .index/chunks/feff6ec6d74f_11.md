# Chunk: feff6ec6d74f_11

- source: `.venv-lab/Lib/site-packages/notebook/static/1871.c375ee093b7e51966390.js`
- lines: 599-661
- chunk: 12/78

```
 formContext } = registry;
        const _schemaItems = isObject_default()(schema.items) ? schema.items : [];
        const itemSchemas = _schemaItems.map((item, index) => schemaUtils.retrieveSchema(item, formData[index]));
        const additionalSchema = isObject_default()(schema.additionalItems)
            ? schemaUtils.retrieveSchema(schema.additionalItems, formData)
            : null;
        if (!items || items.length < itemSchemas.length) {
            // to make sure at least all fixed items are generated
            items = items || [];
            items = items.concat(new Array(itemSchemas.length - items.length));
        }
        // These are the props passed into the render function
        const canAdd = this.canAddItem(items) && !!additionalSchema;
        const arrayProps = {
            canAdd,
            className: 'field field-array field-array-fixed-items',
            disabled,
            idSchema,
            formData,
            items: keyedFormData.map((keyedItem, index) => {
                const { key, item } = keyedItem;
                // While we are actually dealing with a single item of type T, the types require a T[], so cast
                const itemCast = item;
                const additional = index >= itemSchemas.length;
                const itemSchema = (additional && isObject_default()(schema.additionalItems)
                    ? schemaUtils.retrieveSchema(schema.additionalItems, itemCast)
                    : itemSchemas[index]) || {};
                const itemIdPrefix = idSchema.$id + idSeparator + index;
                const itemIdSchema = schemaUtils.toIdSchema(itemSchema, itemIdPrefix, itemCast, idPrefix, idSeparator);
                const itemUiSchema = additional
                    ? uiSchema.additionalItems || {}
                    : Array.isArray(uiSchema.items)
                        ? uiSchema.items[index]
                        : uiSchema.items || {};
                const itemErrorSchema = errorSchema ? errorSchema[index] : undefined;
                return this.renderArrayFieldItem({
                    key,
                    index,
                    name: name && `${name}-${index}`,
                    canAdd,
                    canRemove: additional,
                    canMoveUp: index >= itemSchemas.length + 1,
                    canMoveDown: additional && index < items.length - 1,
                    itemSchema,
                    itemData: itemCast,
                    itemUiSchema,
                    itemIdSchema,
                    itemErrorSchema,
                    autofocus: autofocus && index === 0,
                    onBlur,
                    onFocus,
                    rawErrors,
                    totalItems: keyedFormData.length,
                });
            }),
            onAddClick: this.onAddClick,
            readonly,
            required,
            registry,
            schema,
            uiSchema,
            title,
```
