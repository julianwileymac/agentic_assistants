# Chunk: feff6ec6d74f_37

- source: `.venv-lab/Lib/site-packages/notebook/static/1871.c375ee093b7e51966390.js`
- lines: 1531-1576
- chunk: 38/78

```
onst options = (0,lib_index_js_.getUiOptions)(uiSchema, registry.globalUiOptions);
    const { label: displayLabel = true } = options;
    if (!title || !displayLabel) {
        return null;
    }
    const TitleFieldTemplate = (0,lib_index_js_.getTemplate)('TitleFieldTemplate', registry, options);
    return ((0,jsx_runtime.jsx)(TitleFieldTemplate, { id: (0,lib_index_js_.titleId)(idSchema), title: title, required: required, schema: schema, uiSchema: uiSchema, registry: registry }));
}
//# sourceMappingURL=ArrayFieldTitleTemplate.js.map
;// CONCATENATED MODULE: ../node_modules/@rjsf/core/lib/components/templates/BaseInputTemplate.js



/** The `BaseInputTemplate` is the template to use to render the basic `<input>` component for the `core` theme.
 * It is used as the template for rendering many of the <input> based widgets that differ by `type` and callbacks only.
 * It can be customized/overridden for other themes or individual implementations as needed.
 *
 * @param props - The `WidgetProps` for this template
 */
function BaseInputTemplate(props) {
    const { id, name, // remove this from ...rest
    value, readonly, disabled, autofocus, onBlur, onFocus, onChange, onChangeOverride, options, schema, uiSchema, formContext, registry, rawErrors, type, hideLabel, // remove this from ...rest
    hideError, // remove this from ...rest
    ...rest } = props;
    // Note: since React 15.2.0 we can't forward unknown element attributes, so we
    // exclude the "options" and "schema" ones here.
    if (!id) {
        console.log('No id for', props);
        throw new Error(`no id for props ${JSON.stringify(props)}`);
    }
    const inputProps = {
        ...rest,
        ...(0,lib_index_js_.getInputProps)(schema, type, options),
    };
    let inputValue;
    if (inputProps.type === 'number' || inputProps.type === 'integer') {
        inputValue = value || value === 0 ? value : '';
    }
    else {
        inputValue = value == null ? '' : value;
    }
    const _onChange = (0,index_js_.useCallback)(({ target: { value } }) => onChange(value === '' ? options.emptyValue : value), [onChange, options]);
    const _onBlur = (0,index_js_.useCallback)(({ target: { value } }) => onBlur(id, value), [onBlur, id]);
    const _onFocus = (0,index_js_.useCallback)(({ target: { value } }) => onFocus(id, value), [onFocus, id]);
    return ((0,jsx_runtime.jsxs)(jsx_runtime.Fragment, { children: [(0,jsx_runtime.jsx)("input", { id: id, name: id, className: 'form-control', readOnly: readonly, disabled: disabled, autoFocus: autofocus, value: inputValue, ...inputProps, list: schema.examples ? (0,lib_index_js_.examplesId)(id) : undefined, onChange: onChangeOverride || _onChange, onBlur: _onBlur, onFocus: _onFocus, "aria-describedby": (0,lib_index_js_.ariaDescribedByIds)(id, !!schema.examples) }), Array.isArray(schema.examples) && ((0,jsx_runtime.jsx)("datalist", { id: (0,lib_index_js_.examplesId)(id), children: schema.examples
```
