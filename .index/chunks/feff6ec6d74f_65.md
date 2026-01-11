# Chunk: feff6ec6d74f_65

- source: `.venv-lab/Lib/site-packages/notebook/static/1871.c375ee093b7e51966390.js`
- lines: 2948-2983
- chunk: 66/78

```
     const { SubmitButton } = registry.templates.ButtonTemplates;
        // The `semantic-ui` and `material-ui` themes have `_internalFormWrapper`s that take an `as` prop that is the
        // PropTypes.elementType to use for the inner tag, so we'll need to pass `tagName` along if it is provided.
        // NOTE, the `as` prop is native to `semantic-ui` and is emulated in the `material-ui` theme
        const as = _internalFormWrapper ? tagName : undefined;
        const FormTag = _internalFormWrapper || tagName || 'form';
        let { [lib_index_js_.SUBMIT_BTN_OPTIONS_KEY]: submitOptions = {} } = (0,lib_index_js_.getUiOptions)(uiSchema);
        if (disabled) {
            submitOptions = { ...submitOptions, props: { ...submitOptions.props, disabled: true } };
        }
        const submitUiSchema = { [lib_index_js_.UI_OPTIONS_KEY]: { [lib_index_js_.SUBMIT_BTN_OPTIONS_KEY]: submitOptions } };
        return ((0,jsx_runtime.jsxs)(FormTag, { className: className ? className : 'rjsf', id: id, name: name, method: method, target: target, action: action, autoComplete: autoComplete, encType: enctype, acceptCharset: acceptcharset, noValidate: noHtml5Validate, onSubmit: this.onSubmit, as: as, ref: this.formElement, children: [showErrorList === 'top' && this.renderErrors(registry), (0,jsx_runtime.jsx)(_SchemaField, { name: '', schema: schema, uiSchema: uiSchema, errorSchema: errorSchema, idSchema: idSchema, idPrefix: idPrefix, idSeparator: idSeparator, formContext: formContext, formData: formData, onChange: this.onChange, onBlur: this.onBlur, onFocus: this.onFocus, registry: registry, disabled: disabled, readonly: readonly }), children ? children : (0,jsx_runtime.jsx)(SubmitButton, { uiSchema: submitUiSchema, registry: registry }), showErrorList === 'bottom' && this.renderErrors(registry)] }));
    }
}
//# sourceMappingURL=Form.js.map
;// CONCATENATED MODULE: ../node_modules/@rjsf/core/lib/withTheme.js



/** A Higher-Order component that creates a wrapper around a `Form` with the overrides from the `WithThemeProps` */
function withTheme(themeProps) {
    return forwardRef(({ fields, widgets, templates, ...directProps }, ref) => {
        var _a;
        fields = { ...themeProps === null || themeProps === void 0 ? void 0 : themeProps.fields, ...fields };
        widgets = { ...themeProps === null || themeProps === void 0 ? void 0 : themeProps.widgets, ...widgets };
        templates = {
            ...themeProps === null || themeProps === void 0 ? void 0 : themeProps.templates,
            ...templates,
            ButtonTemplates: {
                ...(_a = themeProps === null || themeProps === void 0 ? void 0 : themeProps.templates) === null || _a === void 0 ? void 0 : _a.ButtonTemplates,
                ...templates === null || templates === void 0 ? void 0 : templates.ButtonTemplates,
            },
        };
        return (_jsx(Form, { ...themeProps, ...directProps, fields: fields, widgets: widgets, templates: templates, ref: ref }));
    });
```
