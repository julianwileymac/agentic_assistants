# Chunk: feff6ec6d74f_35

- source: `.venv-lab/Lib/site-packages/notebook/static/1871.c375ee093b7e51966390.js`
- lines: 1462-1499
- chunk: 36/78

```
ULE: ../node_modules/@rjsf/core/lib/components/templates/ArrayFieldDescriptionTemplate.js


/** The `ArrayFieldDescriptionTemplate` component renders a `DescriptionFieldTemplate` with an `id` derived from
 * the `idSchema`.
 *
 * @param props - The `ArrayFieldDescriptionProps` for the component
 */
function ArrayFieldDescriptionTemplate(props) {
    const { idSchema, description, registry, schema, uiSchema } = props;
    const options = (0,lib_index_js_.getUiOptions)(uiSchema, registry.globalUiOptions);
    const { label: displayLabel = true } = options;
    if (!description || !displayLabel) {
        return null;
    }
    const DescriptionFieldTemplate = (0,lib_index_js_.getTemplate)('DescriptionFieldTemplate', registry, options);
    return ((0,jsx_runtime.jsx)(DescriptionFieldTemplate, { id: (0,lib_index_js_.descriptionId)(idSchema), description: description, schema: schema, uiSchema: uiSchema, registry: registry }));
}
//# sourceMappingURL=ArrayFieldDescriptionTemplate.js.map
;// CONCATENATED MODULE: ../node_modules/@rjsf/core/lib/components/templates/ArrayFieldItemTemplate.js

/** The `ArrayFieldItemTemplate` component is the template used to render an items of an array.
 *
 * @param props - The `ArrayFieldTemplateItemType` props for the component
 */
function ArrayFieldItemTemplate(props) {
    const { children, className, disabled, hasToolbar, hasMoveDown, hasMoveUp, hasRemove, hasCopy, index, onCopyIndexClick, onDropIndexClick, onReorderClick, readonly, registry, uiSchema, } = props;
    const { CopyButton, MoveDownButton, MoveUpButton, RemoveButton } = registry.templates.ButtonTemplates;
    const btnStyle = {
        flex: 1,
        paddingLeft: 6,
        paddingRight: 6,
        fontWeight: 'bold',
    };
    return ((0,jsx_runtime.jsxs)("div", { className: className, children: [(0,jsx_runtime.jsx)("div", { className: hasToolbar ? 'col-xs-9' : 'col-xs-12', children: children }), hasToolbar && ((0,jsx_runtime.jsx)("div", { className: 'col-xs-3 array-item-toolbox', children: (0,jsx_runtime.jsxs)("div", { className: 'btn-group', style: {
                        display: 'flex',
                        justifyContent: 'space-around',
                    }, children: [(hasMoveUp || hasMoveDown) && ((0,jsx_runtime.jsx)(MoveUpButton, { style: btnStyle, disabled: disabled || readonly || !hasMoveUp, onClick: onReorderClick(index, index - 1), uiSchema: uiSchema, registry: registry })), (hasMoveUp || hasMoveDown) && ((0,jsx_runtime.jsx)(MoveDownButton, { style: btnStyle, disabled: disabled || readonly || !hasMoveDown, onClick: onReorderClick(index, index + 1), uiSchema: uiSchema, registry: registry })), hasCopy && ((0,jsx_runtime.jsx)(CopyButton, { style: btnStyle, disabled: disabled || readonly, onClick: onCopyIndexClick(index), uiSchema: uiSchema, registry: registry })), hasRemove && ((0,jsx_runtime.jsx)(RemoveButton, { style: btnStyle, disabled: disabled || readonly, onClick: onDropIndexClick(index), uiSchema: uiSchema, registry: registry 
```
