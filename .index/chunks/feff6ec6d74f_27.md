# Chunk: feff6ec6d74f_27

- source: `.venv-lab/Lib/site-packages/notebook/static/1871.c375ee093b7e51966390.js`
- lines: 1097-1165
- chunk: 28/78

```
{}, ...keyValues);
                this.setState({ wasPropertyKeyModified: true });
                onChange(renamedObj, errorSchema &&
                    errorSchema && {
                    ...errorSchema,
                    [value]: newErrorSchema,
                });
            };
        };
        /** Handles the adding of a new additional property on the given `schema`. Calls the `onChange` callback once the new
         * default data for that field has been added to the formData.
         *
         * @param schema - The schema element to which the new property is being added
         */
        this.handleAddClick = (schema) => () => {
            if (!schema.additionalProperties) {
                return;
            }
            const { formData, onChange, registry } = this.props;
            const newFormData = { ...formData };
            let type = undefined;
            if (isObject_default()(schema.additionalProperties)) {
                type = schema.additionalProperties.type;
                let apSchema = schema.additionalProperties;
                if (lib_index_js_.REF_KEY in apSchema) {
                    const { schemaUtils } = registry;
                    apSchema = schemaUtils.retrieveSchema({ $ref: apSchema[lib_index_js_.REF_KEY] }, formData);
                    type = apSchema.type;
                }
                if (!type && (lib_index_js_.ANY_OF_KEY in apSchema || lib_index_js_.ONE_OF_KEY in apSchema)) {
                    type = 'object';
                }
            }
            const newKey = this.getAvailableKey('newKey', newFormData);
            // Cast this to make the `set` work properly
            set_default()(newFormData, newKey, this.getDefaultValue(type));
            onChange(newFormData);
        };
    }
    /** Returns a flag indicating whether the `name` field is required in the object schema
     *
     * @param name - The name of the field to check for required-ness
     * @returns - True if the field `name` is required, false otherwise
     */
    isRequired(name) {
        const { schema } = this.props;
        return Array.isArray(schema.required) && schema.required.indexOf(name) !== -1;
    }
    /** Returns a default value to be used for a new additional schema property of the given `type`
     *
     * @param type - The type of the new additional schema property
     */
    getDefaultValue(type) {
        const { registry: { translateString }, } = this.props;
        switch (type) {
            case 'array':
                return [];
            case 'boolean':
                return false;
            case 'null':
                return null;
            case 'number':
                return 0;
            case 'object':
                return {};
            case 'string':
            default:
                // We don't have a datatype for some reason (perhaps additionalProperties was true)
```
