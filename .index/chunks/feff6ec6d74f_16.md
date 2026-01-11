# Chunk: feff6ec6d74f_16

- source: `.venv-lab/Lib/site-packages/notebook/static/1871.c375ee093b7e51966390.js`
- lines: 853-906
- chunk: 17/78

```
Option, formData, retrievedOptions);
            if (prevState && matchingOption !== selectedOption) {
                newState = { selectedOption: matchingOption, retrievedOptions };
            }
        }
        if (newState !== this.state) {
            this.setState(newState);
        }
    }
    /** Determines the best matching option for the given `formData` and `options`.
     *
     * @param formData - The new formData
     * @param options - The list of options to choose from
     * @return - The index of the `option` that best matches the `formData`
     */
    getMatchingOption(selectedOption, formData, options) {
        const { schema, registry: { schemaUtils }, } = this.props;
        const discriminator = (0,lib_index_js_.getDiscriminatorFieldFromSchema)(schema);
        const option = schemaUtils.getClosestMatchingOption(formData, options, selectedOption, discriminator);
        return option;
    }
    getFieldId() {
        const { idSchema, schema } = this.props;
        return `${idSchema.$id}${schema.oneOf ? '__oneof_select' : '__anyof_select'}`;
    }
    /** Renders the `AnyOfField` selector along with a `SchemaField` for the value of the `formData`
     */
    render() {
        const { name, disabled = false, errorSchema = {}, formContext, onBlur, onFocus, registry, schema, uiSchema, } = this.props;
        const { widgets, fields, translateString, globalUiOptions, schemaUtils } = registry;
        const { SchemaField: _SchemaField } = fields;
        const { selectedOption, retrievedOptions } = this.state;
        const { widget = 'select', placeholder, autofocus, autocomplete, title = schema.title, ...uiOptions } = (0,lib_index_js_.getUiOptions)(uiSchema, globalUiOptions);
        const Widget = (0,lib_index_js_.getWidget)({ type: 'number' }, widget, widgets);
        const rawErrors = get_default()(errorSchema, lib_index_js_.ERRORS_KEY, []);
        const fieldErrorSchema = omit_default()(errorSchema, [lib_index_js_.ERRORS_KEY]);
        const displayLabel = schemaUtils.getDisplayLabel(schema, uiSchema, globalUiOptions);
        const option = selectedOption >= 0 ? retrievedOptions[selectedOption] || null : null;
        let optionSchema;
        if (option) {
            // merge top level required field
            const { required } = schema;
            // Merge in all the non-oneOf/anyOf properties and also skip the special ADDITIONAL_PROPERTY_FLAG property
            optionSchema = required ? (0,lib_index_js_.mergeSchemas)({ required }, option) : option;
        }
        const translateEnum = title
            ? lib_index_js_.TranslatableString.TitleOptionPrefix
            : lib_index_js_.TranslatableString.OptionPrefix;
        const translateParams = title ? [title] : [];
        const enumOptions = retrievedOptions.map((opt, index) => ({
            label: opt.title || translateString(translateEnum, translateParams.concat(String(index + 1))),
            value: index,
        }));
```
