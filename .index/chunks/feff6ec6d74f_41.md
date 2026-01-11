# Chunk: feff6ec6d74f_41

- source: `.venv-lab/Lib/site-packages/notebook/static/1871.c375ee093b7e51966390.js`
- lines: 1726-1774
- chunk: 42/78

```
rors.length === 0) {
        return null;
    }
    const id = (0,lib_index_js_.errorId)(idSchema);
    return ((0,jsx_runtime.jsx)("div", { children: (0,jsx_runtime.jsx)("ul", { id: id, className: 'error-detail bs-callout bs-callout-info', children: errors
                .filter((elem) => !!elem)
                .map((error, index) => {
                return ((0,jsx_runtime.jsx)("li", { className: 'text-danger', children: error }, index));
            }) }) }));
}
//# sourceMappingURL=FieldErrorTemplate.js.map
;// CONCATENATED MODULE: ../node_modules/@rjsf/core/lib/components/templates/FieldHelpTemplate.js


/** The `FieldHelpTemplate` component renders any help desired for a field
 *
 * @param props - The `FieldHelpProps` to be rendered
 */
function FieldHelpTemplate(props) {
    const { idSchema, help } = props;
    if (!help) {
        return null;
    }
    const id = (0,lib_index_js_.helpId)(idSchema);
    if (typeof help === 'string') {
        return ((0,jsx_runtime.jsx)("p", { id: id, className: 'help-block', children: help }));
    }
    return ((0,jsx_runtime.jsx)("div", { id: id, className: 'help-block', children: help }));
}
//# sourceMappingURL=FieldHelpTemplate.js.map
;// CONCATENATED MODULE: ../node_modules/@rjsf/core/lib/components/templates/ObjectFieldTemplate.js


/** The `ObjectFieldTemplate` is the template to use to render all the inner properties of an object along with the
 * title and description if available. If the object is expandable, then an `AddButton` is also rendered after all
 * the properties.
 *
 * @param props - The `ObjectFieldTemplateProps` for this component
 */
function ObjectFieldTemplate(props) {
    const { description, disabled, formData, idSchema, onAddClick, properties, readonly, registry, required, schema, title, uiSchema, } = props;
    const options = (0,lib_index_js_.getUiOptions)(uiSchema);
    const TitleFieldTemplate = (0,lib_index_js_.getTemplate)('TitleFieldTemplate', registry, options);
    const DescriptionFieldTemplate = (0,lib_index_js_.getTemplate)('DescriptionFieldTemplate', registry, options);
    // Button templates are not overridden in the uiSchema
    const { ButtonTemplates: { AddButton }, } = registry.templates;
    return ((0,jsx_runtime.jsxs)("fieldset", { id: idSchema.$id, children: [title && ((0,jsx_runtime.jsx)(TitleFieldTemplate, { id: (0,lib_index_js_.titleId)(idSchema), title: title, required: required, schema: schema, uiSchema: uiSchema, registry: registry })), description && ((0,jsx_runtime.jsx)(DescriptionFieldTemplate, { id: (0,lib_index_js_.descriptionId)(idSchema), description: description, schema: schema, uiSchema: uiSchema, registry: registry })), properties.map((prop) => prop.content), (0,lib_index_js_.canExpand)(schema, uiSchema, formData) && ((0,jsx_runtime.jsx)(AddButton, { className: 'object-property-expand', onClick: onAddClick(schema), disabled: disabled || readonly, uiSchema: uiSchema, registry: registry }))] }));
}
```
