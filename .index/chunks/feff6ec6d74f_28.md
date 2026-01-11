# Chunk: feff6ec6d74f_28

- source: `.venv-lab/Lib/site-packages/notebook/static/1871.c375ee093b7e51966390.js`
- lines: 1156-1199
- chunk: 29/78

```
   case 'null':
                return null;
            case 'number':
                return 0;
            case 'object':
                return {};
            case 'string':
            default:
                // We don't have a datatype for some reason (perhaps additionalProperties was true)
                return translateString(lib_index_js_.TranslatableString.NewStringDefault);
        }
    }
    /** Renders the `ObjectField` from the given props
     */
    render() {
        var _a, _b, _c;
        const { schema: rawSchema, uiSchema = {}, formData, errorSchema, idSchema, name, required = false, disabled = false, readonly = false, hideError, idPrefix, idSeparator, onBlur, onFocus, registry, } = this.props;
        const { fields, formContext, schemaUtils, translateString, globalUiOptions } = registry;
        const { SchemaField } = fields;
        const schema = schemaUtils.retrieveSchema(rawSchema, formData);
        const uiOptions = (0,lib_index_js_.getUiOptions)(uiSchema, globalUiOptions);
        const { properties: schemaProperties = {} } = schema;
        const title = (_b = (_a = uiOptions.title) !== null && _a !== void 0 ? _a : schema.title) !== null && _b !== void 0 ? _b : name;
        const description = (_c = uiOptions.description) !== null && _c !== void 0 ? _c : schema.description;
        let orderedProperties;
        try {
            const properties = Object.keys(schemaProperties);
            orderedProperties = (0,lib_index_js_.orderProperties)(properties, uiOptions.order);
        }
        catch (err) {
            return ((0,jsx_runtime.jsxs)("div", { children: [(0,jsx_runtime.jsx)("p", { className: 'config-error', style: { color: 'red' }, children: (0,jsx_runtime.jsx)(index_modern, { children: translateString(lib_index_js_.TranslatableString.InvalidObjectField, [name || 'root', err.message]) }) }), (0,jsx_runtime.jsx)("pre", { children: JSON.stringify(schema) })] }));
        }
        const Template = (0,lib_index_js_.getTemplate)('ObjectFieldTemplate', registry, uiOptions);
        const templateProps = {
            // getDisplayLabel() always returns false for object types, so just check the `uiOptions.label`
            title: uiOptions.label === false ? '' : title,
            description: uiOptions.label === false ? undefined : description,
            properties: orderedProperties.map((name) => {
                const addedByAdditionalProperties = has_default()(schema, [lib_index_js_.PROPERTIES_KEY, name, lib_index_js_.ADDITIONAL_PROPERTY_FLAG]);
                const fieldUiSchema = addedByAdditionalProperties ? uiSchema.additionalProperties : uiSchema[name];
                const hidden = (0,lib_index_js_.getUiOptions)(fieldUiSchema).widget === 'hidden';
                const fieldIdSchema = get_default()(idSchema, [name], {});
                return {
```
