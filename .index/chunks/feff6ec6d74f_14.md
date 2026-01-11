# Chunk: feff6ec6d74f_14

- source: `.venv-lab/Lib/site-packages/notebook/static/1871.c375ee093b7e51966390.js`
- lines: 754-817
- chunk: 15/78

```
mes = schema;
        const enums = (_b = schema.enum) !== null && _b !== void 0 ? _b : [true, false];
        if (!schemaWithEnumNames.enumNames && enums.length === 2 && enums.every((v) => typeof v === 'boolean')) {
            enumOptions = [
                {
                    value: enums[0],
                    label: enums[0] ? yes : no,
                },
                {
                    value: enums[1],
                    label: enums[1] ? yes : no,
                },
            ];
        }
        else {
            enumOptions = (0,lib_index_js_.optionsList)({
                enum: enums,
                // NOTE: enumNames is deprecated, but still supported for now.
                enumNames: schemaWithEnumNames.enumNames,
            });
        }
    }
    return ((0,jsx_runtime.jsx)(Widget, { options: { ...options, enumOptions }, schema: schema, uiSchema: uiSchema, id: idSchema.$id, name: name, onChange: onChange, onFocus: onFocus, onBlur: onBlur, label: label, hideLabel: !displayLabel, value: formData, required: required, disabled: disabled, readonly: readonly, hideError: hideError, registry: registry, formContext: formContext, autofocus: autofocus, rawErrors: rawErrors }));
}
/* harmony default export */ const fields_BooleanField = (BooleanField);
//# sourceMappingURL=BooleanField.js.map
// EXTERNAL MODULE: ../node_modules/lodash/omit.js
var omit = __webpack_require__(48159);
var omit_default = /*#__PURE__*/__webpack_require__.n(omit);
;// CONCATENATED MODULE: ../node_modules/@rjsf/core/lib/components/fields/MultiSchemaField.js






/** The `AnyOfField` component is used to render a field in the schema that is an `anyOf`, `allOf` or `oneOf`. It tracks
 * the currently selected option and cleans up any irrelevant data in `formData`.
 *
 * @param props - The `FieldProps` for this template
 */
class AnyOfField extends index_js_.Component {
    /** Constructs an `AnyOfField` with the given `props` to initialize the initially selected option in state
     *
     * @param props - The `FieldProps` for this template
     */
    constructor(props) {
        super(props);
        /** Callback handler to remember what the currently selected option is. In addition to that the `formData` is updated
         * to remove properties that are not part of the newly selected option schema, and then the updated data is passed to
         * the `onChange` handler.
         *
         * @param option - The new option value being selected
         */
        this.onOptionChange = (option) => {
            const { selectedOption, retrievedOptions } = this.state;
            const { formData, onChange, registry } = this.props;
            const { schemaUtils } = registry;
            const intOption = option !== undefined ? parseInt(option, 10) : -1;
            if (intOption === selectedOption) {
                return;
            }
            const newOption = intOption >= 0 ? retrievedOptions[intOption] : undefined;
```
