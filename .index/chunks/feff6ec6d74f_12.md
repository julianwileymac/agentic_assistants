# Chunk: feff6ec6d74f_12

- source: `.venv-lab/Lib/site-packages/notebook/static/1871.c375ee093b7e51966390.js`
- lines: 649-710
- chunk: 13/78

```
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
            formContext,
            rawErrors,
        };
        const Template = (0,lib_index_js_.getTemplate)('ArrayFieldTemplate', registry, uiOptions);
        return (0,jsx_runtime.jsx)(Template, { ...arrayProps });
    }
    /** Renders the individual array item using a `SchemaField` along with the additional properties required to be send
     * back to the `ArrayFieldItemTemplate`.
     *
     * @param props - The props for the individual array item to be rendered
     */
    renderArrayFieldItem(props) {
        const { key, index, name, canAdd, canRemove = true, canMoveUp, canMoveDown, itemSchema, itemData, itemUiSchema, itemIdSchema, itemErrorSchema, autofocus, onBlur, onFocus, rawErrors, totalItems, } = props;
        const { disabled, hideError, idPrefix, idSeparator, readonly, uiSchema, registry, formContext } = this.props;
        const { fields: { ArraySchemaField, SchemaField }, globalUiOptions, } = registry;
        const ItemSchemaField = ArraySchemaField || SchemaField;
        const { orderable = true, removable = true, copyable = false } = (0,lib_index_js_.getUiOptions)(uiSchema, globalUiOptions);
        const has = {
            moveUp: orderable && canMoveUp,
            moveDown: orderable && canMoveDown,
            copy: copyable && canAdd,
            remove: removable && canRemove,
            toolbar: false,
        };
        has.toolbar = Object.keys(has).some((key) => has[key]);
        return {
            children: ((0,jsx_runtime.jsx)(ItemSchemaField, { name: name, index: index, schema: itemSchema, uiSchema: itemUiSchema, formData: itemData, formContext: formContext, errorSchema: itemErrorSchema, idPrefix: idPrefix, idSeparator: idSeparator, idSchema: itemIdSchema, required: this.isItemRequired(itemSchema), onChange: this.onChangeForIndex(index), onBlur: onBlur, onFocus: onFocus, registry: registry, disabled: disabled, readonly: readonly, hideError: hideError, autofocus: autofocus, rawErrors: rawErrors })),
            className: 'array-item',
            disabled,
            canAdd,
            hasCopy: has.copy,
            hasToolbar: has.toolbar,
            hasMoveUp: has.moveUp,
            hasMoveDown: has.moveDown,
            hasRemove: has.remove,
            index,
            totalItems,
            key,
            onAddIndexClick: this.onAddIndexClick,
            onCopyIndexClick: this.onCopyIndexClick,
            onDropIndexClick: this.onDropIndexClick,
            onReorderClick: this.onReorderClick,
            readonly,
            registry,
            schema: itemSchema,
            uiSchema: itemUiSchema,
        };
    }
}
```
