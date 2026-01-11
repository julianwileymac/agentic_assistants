# Chunk: feff6ec6d74f_17

- source: `.venv-lab/Lib/site-packages/notebook/static/1871.c375ee093b7e51966390.js`
- lines: 900-945
- chunk: 18/78

```
ranslatableString.OptionPrefix;
        const translateParams = title ? [title] : [];
        const enumOptions = retrievedOptions.map((opt, index) => ({
            label: opt.title || translateString(translateEnum, translateParams.concat(String(index + 1))),
            value: index,
        }));
        return ((0,jsx_runtime.jsxs)("div", { className: 'panel panel-default panel-body', children: [(0,jsx_runtime.jsx)("div", { className: 'form-group', children: (0,jsx_runtime.jsx)(Widget, { id: this.getFieldId(), name: `${name}${schema.oneOf ? '__oneof_select' : '__anyof_select'}`, schema: { type: 'number', default: 0 }, onChange: this.onOptionChange, onBlur: onBlur, onFocus: onFocus, disabled: disabled || isEmpty_default()(enumOptions), multiple: false, rawErrors: rawErrors, errorSchema: fieldErrorSchema, value: selectedOption >= 0 ? selectedOption : undefined, options: { enumOptions, ...uiOptions }, registry: registry, formContext: formContext, placeholder: placeholder, autocomplete: autocomplete, autofocus: autofocus, label: title !== null && title !== void 0 ? title : name, hideLabel: !displayLabel }) }), option !== null && (0,jsx_runtime.jsx)(_SchemaField, { ...this.props, schema: optionSchema })] }));
    }
}
/* harmony default export */ const MultiSchemaField = (AnyOfField);
//# sourceMappingURL=MultiSchemaField.js.map
;// CONCATENATED MODULE: ../node_modules/@rjsf/core/lib/components/fields/NumberField.js



// Matches a string that ends in a . character, optionally followed by a sequence of
// digits followed by any number of 0 characters up until the end of the line.
// Ensuring that there is at least one prefixed character is important so that
// you don't incorrectly match against "0".
const trailingCharMatcherWithPrefix = /\.([0-9]*0)*$/;
// This is used for trimming the trailing 0 and . characters without affecting
// the rest of the string. Its possible to use one RegEx with groups for this
// functionality, but it is fairly complex compared to simply defining two
// different matchers.
const trailingCharMatcher = /[0.]0*$/;
/**
 * The NumberField class has some special handling for dealing with trailing
 * decimal points and/or zeroes. This logic is designed to allow trailing values
 * to be visible in the input element, but not be represented in the
 * corresponding form data.
 *
 * The algorithm is as follows:
 *
 * 1. When the input value changes the value is cached in the component state
 *
 * 2. The value is then normalized, removing trailing decimal points and zeros,
 *    then passed to the "onChange" callback
 *
 * 3. When the component is rendered, the formData value is checked against the
 *    value cached in the state. If it matches the cached value, the cached
 *    value is passed to the input instead of the formData value
 */
function NumberField(props) {
    const { registry, onChange, formData, value: initialValue } = props;
    const [lastValue, setLastValue] = (0,index_js_.useState)(initialValue);
```
