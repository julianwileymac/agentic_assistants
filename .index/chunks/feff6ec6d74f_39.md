# Chunk: feff6ec6d74f_39

- source: `.venv-lab/Lib/site-packages/notebook/static/1871.c375ee093b7e51966390.js`
- lines: 1616-1676
- chunk: 40/78

```
le: translateString(lib_index_js_.TranslatableString.RemoveButton), className: 'array-item-remove', ...props, iconType: 'danger', icon: 'remove' }));
}
//# sourceMappingURL=IconButton.js.map
;// CONCATENATED MODULE: ../node_modules/@rjsf/core/lib/components/templates/ButtonTemplates/AddButton.js



/** The `AddButton` renders a button that represent the `Add` action on a form
 */
function AddButton({ className, onClick, disabled, registry, }) {
    const { translateString } = registry;
    return ((0,jsx_runtime.jsx)("div", { className: 'row', children: (0,jsx_runtime.jsx)("p", { className: `col-xs-3 col-xs-offset-9 text-right ${className}`, children: (0,jsx_runtime.jsx)(IconButton, { iconType: 'info', icon: 'plus', className: 'btn-add col-xs-12', title: translateString(lib_index_js_.TranslatableString.AddButton), onClick: onClick, disabled: disabled, registry: registry }) }) }));
}
//# sourceMappingURL=AddButton.js.map
;// CONCATENATED MODULE: ../node_modules/@rjsf/core/lib/components/templates/ButtonTemplates/index.js



function buttonTemplates() {
    return {
        SubmitButton: SubmitButton,
        AddButton: AddButton,
        CopyButton: CopyButton,
        MoveDownButton: MoveDownButton,
        MoveUpButton: MoveUpButton,
        RemoveButton: RemoveButton,
    };
}
/* harmony default export */ const ButtonTemplates = (buttonTemplates);
//# sourceMappingURL=index.js.map
;// CONCATENATED MODULE: ../node_modules/@rjsf/core/lib/components/templates/DescriptionField.js

/** The `DescriptionField` is the template to use to render the description of a field
 *
 * @param props - The `DescriptionFieldProps` for this component
 */
function DescriptionField(props) {
    const { id, description } = props;
    if (!description) {
        return null;
    }
    if (typeof description === 'string') {
        return ((0,jsx_runtime.jsx)("p", { id: id, className: 'field-description', children: description }));
    }
    else {
        return ((0,jsx_runtime.jsx)("div", { id: id, className: 'field-description', children: description }));
    }
}
//# sourceMappingURL=DescriptionField.js.map
;// CONCATENATED MODULE: ../node_modules/@rjsf/core/lib/components/templates/ErrorList.js


/** The `ErrorList` component is the template that renders the all the errors associated with the fields in the `Form`
 *
 * @param props - The `ErrorListProps` for this component
 */
function ErrorList({ errors, registry, }) {
    const { translateString } = registry;
    return ((0,jsx_runtime.jsxs)("div", { className: 'panel panel-danger errors', children: [(0,jsx_runtime.jsx)("div", { className: 'panel-heading', children: (0,jsx_runtime.jsx)("h3", { className: 'panel-title', children: translateString(lib_index_js_.TranslatableString.ErrorsLabel) }) }), (0,jsx_runtime.jsx)("ul", { className: 'list-group', children: errors.map((error, i) => {
                    return ((0,jsx_runtime.jsx)("li", { className: 'list-group-item text-danger', children: error.stack }, i));
```
