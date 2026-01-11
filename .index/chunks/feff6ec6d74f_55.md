# Chunk: feff6ec6d74f_55

- source: `.venv-lab/Lib/site-packages/notebook/static/1871.c375ee093b7e51966390.js`
- lines: 2409-2477
- chunk: 56/78

```
ATENATED MODULE: ../node_modules/@rjsf/core/lib/getDefaultRegistry.js




/** The default registry consists of all the fields, templates and widgets provided in the core implementation,
 * plus an empty `rootSchema` and `formContext. We omit schemaUtils here because it cannot be defaulted without a
 * rootSchema and validator. It will be added into the computed registry later in the Form.
 */
function getDefaultRegistry() {
    return {
        fields: components_fields(),
        templates: components_templates(),
        widgets: components_widgets(),
        rootSchema: {},
        formContext: {},
        translateString: lib_index_js_.englishStringTranslator,
    };
}
//# sourceMappingURL=getDefaultRegistry.js.map
;// CONCATENATED MODULE: ../node_modules/@rjsf/core/lib/components/Form.js








/** The `Form` component renders the outer form and all the fields defined in the `schema` */
class Form_Form extends index_js_.Component {
    /** Constructs the `Form` from the `props`. Will setup the initial state from the props. It will also call the
     * `onChange` handler if the initially provided `formData` is modified to add missing default values as part of the
     * state construction.
     *
     * @param props - The initial props for the `Form`
     */
    constructor(props) {
        super(props);
        /** Returns the `formData` with only the elements specified in the `fields` list
         *
         * @param formData - The data for the `Form`
         * @param fields - The fields to keep while filtering
         */
        this.getUsedFormData = (formData, fields) => {
            // For the case of a single input form
            if (fields.length === 0 && typeof formData !== 'object') {
                return formData;
            }
            // _pick has incorrect type definition, it works with string[][], because lodash/hasIn supports it
            const data = pick_default()(formData, fields);
            if (Array.isArray(formData)) {
                return Object.keys(data).map((key) => data[key]);
            }
            return data;
        };
        /** Returns the list of field names from inspecting the `pathSchema` as well as using the `formData`
         *
         * @param pathSchema - The `PathSchema` object for the form
         * @param [formData] - The form data to use while checking for empty objects/arrays
         */
        this.getFieldNames = (pathSchema, formData) => {
            const getAllPaths = (_obj, acc = [], paths = [[]]) => {
                Object.keys(_obj).forEach((key) => {
                    if (typeof _obj[key] === 'object') {
                        const newPaths = paths.map((path) => [...path, key]);
                        // If an object is marked with additionalProperties, all its keys are valid
                        if (_obj[key][lib_index_js_.RJSF_ADDITONAL_PROPERTIES_FLAG] && _obj[key][lib_index_js_.NAME_KEY] !== '') {
```
