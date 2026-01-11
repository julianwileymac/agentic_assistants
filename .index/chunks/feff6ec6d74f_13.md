# Chunk: feff6ec6d74f_13

- source: `.venv-lab/Lib/site-packages/notebook/static/1871.c375ee093b7e51966390.js`
- lines: 699-760
- chunk: 14/78

```
ddIndexClick,
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
/** `ArrayField` is `React.ComponentType<FieldProps<T[], S, F>>` (necessarily) but the `registry` requires things to be a
 * `Field` which is defined as `React.ComponentType<FieldProps<T, S, F>>`, so cast it to make `registry` happy.
 */
/* harmony default export */ const fields_ArrayField = (ArrayField);
//# sourceMappingURL=ArrayField.js.map
;// CONCATENATED MODULE: ../node_modules/@rjsf/core/lib/components/fields/BooleanField.js



/** The `BooleanField` component is used to render a field in the schema is boolean. It constructs `enumOptions` for the
 * two boolean values based on the various alternatives in the schema.
 *
 * @param props - The `FieldProps` for this template
 */
function BooleanField(props) {
    var _a, _b;
    const { schema, name, uiSchema, idSchema, formData, registry, required, disabled, readonly, hideError, autofocus, onChange, onFocus, onBlur, rawErrors, } = props;
    const { title } = schema;
    const { widgets, formContext, translateString, globalUiOptions } = registry;
    const { widget = 'checkbox', title: uiTitle, 
    // Unlike the other fields, don't use `getDisplayLabel()` since it always returns false for the boolean type
    label: displayLabel = true, ...options } = (0,lib_index_js_.getUiOptions)(uiSchema, globalUiOptions);
    const Widget = (0,lib_index_js_.getWidget)(schema, widget, widgets);
    const yes = translateString(lib_index_js_.TranslatableString.YesLabel);
    const no = translateString(lib_index_js_.TranslatableString.NoLabel);
    let enumOptions;
    const label = (_a = uiTitle !== null && uiTitle !== void 0 ? uiTitle : title) !== null && _a !== void 0 ? _a : name;
    if (Array.isArray(schema.oneOf)) {
        enumOptions = (0,lib_index_js_.optionsList)({
            oneOf: schema.oneOf
                .map((option) => {
                if (isObject_default()(option)) {
                    return {
                        ...option,
                        title: option.title || (option.const === true ? yes : no),
                    };
                }
                return undefined;
            })
                .filter((o) => o), // cast away the error that typescript can't grok is fixed
        });
    }
    else {
        // We deprecated enumNames in v5. It's intentionally omitted from RSJFSchema type, so we need to cast here.
        const schemaWithEnumNames = schema;
        const enums = (_b = schema.enum) !== null && _b !== void 0 ? _b : [true, false];
        if (!schemaWithEnumNames.enumNames && enums.length === 2 && enums.every((v) => typeof v === 'boolean')) {
            enumOptions = [
                {
                    value: enums[0],
```
