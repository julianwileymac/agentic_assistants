# Chunk: feff6ec6d74f_36

- source: `.venv-lab/Lib/site-packages/notebook/static/1871.c375ee093b7e51966390.js`
- lines: 1499-1537
- chunk: 37/78

```
 style: btnStyle, disabled: disabled || readonly, onClick: onCopyIndexClick(index), uiSchema: uiSchema, registry: registry })), hasRemove && ((0,jsx_runtime.jsx)(RemoveButton, { style: btnStyle, disabled: disabled || readonly, onClick: onDropIndexClick(index), uiSchema: uiSchema, registry: registry }))] }) }))] }));
}
//# sourceMappingURL=ArrayFieldItemTemplate.js.map
;// CONCATENATED MODULE: ../node_modules/@rjsf/core/lib/components/templates/ArrayFieldTemplate.js


/** The `ArrayFieldTemplate` component is the template used to render all items in an array.
 *
 * @param props - The `ArrayFieldTemplateItemType` props for the component
 */
function ArrayFieldTemplate(props) {
    const { canAdd, className, disabled, idSchema, uiSchema, items, onAddClick, readonly, registry, required, schema, title, } = props;
    const uiOptions = (0,lib_index_js_.getUiOptions)(uiSchema);
    const ArrayFieldDescriptionTemplate = (0,lib_index_js_.getTemplate)('ArrayFieldDescriptionTemplate', registry, uiOptions);
    const ArrayFieldItemTemplate = (0,lib_index_js_.getTemplate)('ArrayFieldItemTemplate', registry, uiOptions);
    const ArrayFieldTitleTemplate = (0,lib_index_js_.getTemplate)('ArrayFieldTitleTemplate', registry, uiOptions);
    // Button templates are not overridden in the uiSchema
    const { ButtonTemplates: { AddButton }, } = registry.templates;
    return ((0,jsx_runtime.jsxs)("fieldset", { className: className, id: idSchema.$id, children: [(0,jsx_runtime.jsx)(ArrayFieldTitleTemplate, { idSchema: idSchema, title: uiOptions.title || title, required: required, schema: schema, uiSchema: uiSchema, registry: registry }), (0,jsx_runtime.jsx)(ArrayFieldDescriptionTemplate, { idSchema: idSchema, description: uiOptions.description || schema.description, schema: schema, uiSchema: uiSchema, registry: registry }), (0,jsx_runtime.jsx)("div", { className: 'row array-item-list', children: items &&
                    items.map(({ key, ...itemProps }) => ((0,jsx_runtime.jsx)(ArrayFieldItemTemplate, { ...itemProps }, key))) }), canAdd && ((0,jsx_runtime.jsx)(AddButton, { className: 'array-item-add', onClick: onAddClick, disabled: disabled || readonly, uiSchema: uiSchema, registry: registry }))] }));
}
//# sourceMappingURL=ArrayFieldTemplate.js.map
;// CONCATENATED MODULE: ../node_modules/@rjsf/core/lib/components/templates/ArrayFieldTitleTemplate.js


/** The `ArrayFieldTitleTemplate` component renders a `TitleFieldTemplate` with an `id` derived from
 * the `idSchema`.
 *
 * @param props - The `ArrayFieldTitleProps` for the component
 */
function ArrayFieldTitleTemplate(props) {
    const { idSchema, title, schema, uiSchema, required, registry } = props;
    const options = (0,lib_index_js_.getUiOptions)(uiSchema, registry.globalUiOptions);
    const { label: displayLabel = true } = options;
    if (!title || !displayLabel) {
        return null;
    }
    const TitleFieldTemplate = (0,lib_index_js_.getTemplate)('TitleFieldTemplate', registry, options);
```
