# Chunk: feff6ec6d74f_43

- source: `.venv-lab/Lib/site-packages/notebook/static/1871.c375ee093b7e51966390.js`
- lines: 1823-1884
- chunk: 44/78

```
e `WrapIfAdditionalProps` for this component
 */
function WrapIfAdditionalTemplate(props) {
    const { id, classNames, style, disabled, label, onKeyChange, onDropPropertyClick, readonly, required, schema, children, uiSchema, registry, } = props;
    const { templates, translateString } = registry;
    // Button templates are not overridden in the uiSchema
    const { RemoveButton } = templates.ButtonTemplates;
    const keyLabel = translateString(lib_index_js_.TranslatableString.KeyLabel, [label]);
    const additional = lib_index_js_.ADDITIONAL_PROPERTY_FLAG in schema;
    if (!additional) {
        return ((0,jsx_runtime.jsx)("div", { className: classNames, style: style, children: children }));
    }
    return ((0,jsx_runtime.jsx)("div", { className: classNames, style: style, children: (0,jsx_runtime.jsxs)("div", { className: 'row', children: [(0,jsx_runtime.jsx)("div", { className: 'col-xs-5 form-additional', children: (0,jsx_runtime.jsxs)("div", { className: 'form-group', children: [(0,jsx_runtime.jsx)(Label, { label: keyLabel, required: required, id: `${id}-key` }), (0,jsx_runtime.jsx)("input", { className: 'form-control', type: 'text', id: `${id}-key`, onBlur: (event) => onKeyChange(event.target.value), defaultValue: label })] }) }), (0,jsx_runtime.jsx)("div", { className: 'form-additional form-group col-xs-5', children: children }), (0,jsx_runtime.jsx)("div", { className: 'col-xs-2', children: (0,jsx_runtime.jsx)(RemoveButton, { className: 'array-item-remove btn-block', style: { border: '0' }, disabled: disabled || readonly, onClick: onDropPropertyClick(label), uiSchema: uiSchema, registry: registry }) })] }) }));
}
//# sourceMappingURL=WrapIfAdditionalTemplate.js.map
;// CONCATENATED MODULE: ../node_modules/@rjsf/core/lib/components/templates/index.js















function templates() {
    return {
        ArrayFieldDescriptionTemplate: ArrayFieldDescriptionTemplate,
        ArrayFieldItemTemplate: ArrayFieldItemTemplate,
        ArrayFieldTemplate: ArrayFieldTemplate,
        ArrayFieldTitleTemplate: ArrayFieldTitleTemplate,
        ButtonTemplates: ButtonTemplates(),
        BaseInputTemplate: BaseInputTemplate,
        DescriptionFieldTemplate: DescriptionField,
        ErrorListTemplate: ErrorList,
        FieldTemplate: templates_FieldTemplate,
        FieldErrorTemplate: FieldErrorTemplate,
        FieldHelpTemplate: FieldHelpTemplate,
        ObjectFieldTemplate: ObjectFieldTemplate,
        TitleFieldTemplate: TitleField,
        UnsupportedFieldTemplate: templates_UnsupportedField,
        WrapIfAdditionalTemplate: WrapIfAdditionalTemplate,
    };
}
/* harmony default export */ const components_templates = (templates);
//# sourceMappingURL=index.js.map
;// CONCATENATED MODULE: ../node_modules/@rjsf/core/lib/components/widgets/AltDateWidget.js



function rangeOptions(start, stop) {
    const options = [];
    for (let i = start; i <= stop; i++) {
        options.push({ value: i, label: (0,lib_index_js_.pad)(i, 2) });
    }
```
