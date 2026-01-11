# Chunk: feff6ec6d74f_25

- source: `.venv-lab/Lib/site-packages/notebook/static/1871.c375ee093b7e51966390.js`
- lines: 983-1049
- chunk: 26/78

```
return i}(t,n);return index_js_.cloneElement(Qe(r,i),l)});
//# sourceMappingURL=index.modern.js.map

// EXTERNAL MODULE: ../node_modules/lodash/has.js
var has = __webpack_require__(73915);
var has_default = /*#__PURE__*/__webpack_require__.n(has);
// EXTERNAL MODULE: ../node_modules/lodash/unset.js
var unset = __webpack_require__(43551);
var unset_default = /*#__PURE__*/__webpack_require__.n(unset);
;// CONCATENATED MODULE: ../node_modules/@rjsf/core/lib/components/fields/ObjectField.js









/** The `ObjectField` component is used to render a field in the schema that is of type `object`. It tracks whether an
 * additional property key was modified and what it was modified to
 *
 * @param props - The `FieldProps` for this template
 */
class ObjectField extends index_js_.Component {
    constructor() {
        super(...arguments);
        /** Set up the initial state */
        this.state = {
            wasPropertyKeyModified: false,
            additionalProperties: {},
        };
        /** Returns the `onPropertyChange` handler for the `name` field. Handles the special case where a user is attempting
         * to clear the data for a field added as an additional property. Calls the `onChange()` handler with the updated
         * formData.
         *
         * @param name - The name of the property
         * @param addedByAdditionalProperties - Flag indicating whether this property is an additional property
         * @returns - The onPropertyChange callback for the `name` property
         */
        this.onPropertyChange = (name, addedByAdditionalProperties = false) => {
            return (value, newErrorSchema, id) => {
                const { formData, onChange, errorSchema } = this.props;
                if (value === undefined && addedByAdditionalProperties) {
                    // Don't set value = undefined for fields added by
                    // additionalProperties. Doing so removes them from the
                    // formData, which causes them to completely disappear
                    // (including the input field for the property name). Unlike
                    // fields which are "mandated" by the schema, these fields can
                    // be set to undefined by clicking a "delete field" button, so
                    // set empty values to the empty string.
                    value = '';
                }
                const newFormData = { ...formData, [name]: value };
                onChange(newFormData, errorSchema &&
                    errorSchema && {
                    ...errorSchema,
                    [name]: newErrorSchema,
                }, id);
            };
        };
        /** Returns a callback to handle the onDropPropertyClick event for the given `key` which removes the old `key` data
         * and calls the `onChange` callback with it
         *
         * @param key - The key for which the drop callback is desired
         * @returns - The drop property click callback
```
