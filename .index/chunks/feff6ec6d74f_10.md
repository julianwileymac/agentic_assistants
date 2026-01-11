# Chunk: feff6ec6d74f_10

- source: `.venv-lab/Lib/site-packages/notebook/static/1871.c375ee093b7e51966390.js`
- lines: 573-603
- chunk: 11/78

```
 title: uiTitle, ...options } = (0,lib_index_js_.getUiOptions)(uiSchema, globalUiOptions);
        const Widget = (0,lib_index_js_.getWidget)(schema, widget, widgets);
        const label = (_a = uiTitle !== null && uiTitle !== void 0 ? uiTitle : schema.title) !== null && _a !== void 0 ? _a : name;
        const displayLabel = schemaUtils.getDisplayLabel(schema, uiSchema, globalUiOptions);
        return ((0,jsx_runtime.jsx)(Widget, { id: idSchema.$id, name: name, multiple: true, onChange: this.onSelectChange, onBlur: onBlur, onFocus: onFocus, options: { ...options, enumOptions }, schema: schema, uiSchema: uiSchema, registry: registry, value: items, disabled: disabled, readonly: readonly, required: required, label: label, hideLabel: !displayLabel, placeholder: placeholder, formContext: formContext, autofocus: autofocus, rawErrors: rawErrors }));
    }
    /** Renders an array of files using the `FileWidget`
     */
    renderFiles() {
        var _a;
        const { schema, uiSchema, idSchema, name, disabled = false, readonly = false, autofocus = false, required = false, onBlur, onFocus, registry, formData: items = [], rawErrors, } = this.props;
        const { widgets, formContext, globalUiOptions, schemaUtils } = registry;
        const { widget = 'files', title: uiTitle, ...options } = (0,lib_index_js_.getUiOptions)(uiSchema, globalUiOptions);
        const Widget = (0,lib_index_js_.getWidget)(schema, widget, widgets);
        const label = (_a = uiTitle !== null && uiTitle !== void 0 ? uiTitle : schema.title) !== null && _a !== void 0 ? _a : name;
        const displayLabel = schemaUtils.getDisplayLabel(schema, uiSchema, globalUiOptions);
        return ((0,jsx_runtime.jsx)(Widget, { options: options, id: idSchema.$id, name: name, multiple: true, onChange: this.onSelectChange, onBlur: onBlur, onFocus: onFocus, schema: schema, uiSchema: uiSchema, value: items, disabled: disabled, readonly: readonly, required: required, registry: registry, formContext: formContext, autofocus: autofocus, rawErrors: rawErrors, label: label, hideLabel: !displayLabel }));
    }
    /** Renders an array that has a maximum limit of items
     */
    renderFixedArray() {
        const { schema, uiSchema = {}, formData = [], errorSchema, idPrefix, idSeparator = '_', idSchema, name, disabled = false, readonly = false, autofocus = false, required = false, registry, onBlur, onFocus, rawErrors, } = this.props;
        const { keyedFormData } = this.state;
        let { formData: items = [] } = this.props;
        const title = schema.title || name;
        const uiOptions = (0,lib_index_js_.getUiOptions)(uiSchema);
        const { schemaUtils, formContext } = registry;
        const _schemaItems = isObject_default()(schema.items) ? schema.items : [];
        const itemSchemas = _schemaItems.map((item, index) => schemaUtils.retrieveSchema(item, formData[index]));
        const additionalSchema = isObject_default()(schema.additionalItems)
```
