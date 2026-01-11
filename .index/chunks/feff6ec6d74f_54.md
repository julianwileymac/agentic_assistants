# Chunk: feff6ec6d74f_54

- source: `.venv-lab/Lib/site-packages/notebook/static/1871.c375ee093b7e51966390.js`
- lines: 2327-2416
- chunk: 55/78

```
defined when it is falsy during the `onChange` handling.
 *
 * @param props - The `WidgetProps` for this component
 */
function TimeWidget(props) {
    const { onChange, options, registry } = props;
    const BaseInputTemplate = (0,lib_index_js_.getTemplate)('BaseInputTemplate', registry, options);
    const handleChange = (0,index_js_.useCallback)((value) => onChange(value ? `${value}:00` : undefined), [onChange]);
    return (0,jsx_runtime.jsx)(BaseInputTemplate, { type: 'time', ...props, onChange: handleChange });
}
//# sourceMappingURL=TimeWidget.js.map
;// CONCATENATED MODULE: ../node_modules/@rjsf/core/lib/components/widgets/URLWidget.js


/** The `URLWidget` component uses the `BaseInputTemplate` changing the type to `url`.
 *
 * @param props - The `WidgetProps` for this component
 */
function URLWidget(props) {
    const { options, registry } = props;
    const BaseInputTemplate = (0,lib_index_js_.getTemplate)('BaseInputTemplate', registry, options);
    return (0,jsx_runtime.jsx)(BaseInputTemplate, { type: 'url', ...props });
}
//# sourceMappingURL=URLWidget.js.map
;// CONCATENATED MODULE: ../node_modules/@rjsf/core/lib/components/widgets/UpDownWidget.js


/** The `UpDownWidget` component uses the `BaseInputTemplate` changing the type to `number`.
 *
 * @param props - The `WidgetProps` for this component
 */
function UpDownWidget(props) {
    const { options, registry } = props;
    const BaseInputTemplate = (0,lib_index_js_.getTemplate)('BaseInputTemplate', registry, options);
    return (0,jsx_runtime.jsx)(BaseInputTemplate, { type: 'number', ...props });
}
//# sourceMappingURL=UpDownWidget.js.map
;// CONCATENATED MODULE: ../node_modules/@rjsf/core/lib/components/widgets/index.js



















function widgets() {
    return {
        AltDateWidget: widgets_AltDateWidget,
        AltDateTimeWidget: widgets_AltDateTimeWidget,
        CheckboxWidget: widgets_CheckboxWidget,
        CheckboxesWidget: widgets_CheckboxesWidget,
        ColorWidget: ColorWidget,
        DateWidget: DateWidget,
        DateTimeWidget: DateTimeWidget,
        EmailWidget: EmailWidget,
        FileWidget: widgets_FileWidget,
        HiddenWidget: widgets_HiddenWidget,
        PasswordWidget: PasswordWidget,
        RadioWidget: widgets_RadioWidget,
        RangeWidget: RangeWidget,
        SelectWidget: widgets_SelectWidget,
        TextWidget: TextWidget,
        TextareaWidget: widgets_TextareaWidget,
        TimeWidget: TimeWidget,
        UpDownWidget: UpDownWidget,
        URLWidget: URLWidget,
    };
}
/* harmony default export */ const components_widgets = (widgets);
//# sourceMappingURL=index.js.map
;// CONCATENATED MODULE: ../node_modules/@rjsf/core/lib/getDefaultRegistry.js




/** The default registry consists of all the fields, templates and widgets provided in the core implementation,
 * plus an empty `rootSchema` and `formContext. We omit schemaUtils here because it cannot be defaulted without a
```
