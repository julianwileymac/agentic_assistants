# Chunk: feff6ec6d74f_9

- source: `.venv-lab/Lib/site-packages/notebook/static/1871.c375ee093b7e51966390.js`
- lines: 529-576
- chunk: 10/78

```
      autofocus: autofocus && index === 0,
                    onBlur,
                    onFocus,
                    rawErrors,
                    totalItems: keyedFormData.length,
                });
            }),
            className: `field field-array field-array-of-${itemsSchema.type}`,
            disabled,
            idSchema,
            uiSchema,
            onAddClick: this.onAddClick,
            readonly,
            required,
            schema,
            title,
            formContext,
            formData,
            rawErrors,
            registry,
        };
        const Template = (0,lib_index_js_.getTemplate)('ArrayFieldTemplate', registry, uiOptions);
        return (0,jsx_runtime.jsx)(Template, { ...arrayProps });
    }
    /** Renders an array using the custom widget provided by the user in the `uiSchema`
     */
    renderCustomWidget() {
        var _a;
        const { schema, idSchema, uiSchema, disabled = false, readonly = false, autofocus = false, required = false, hideError, placeholder, onBlur, onFocus, formData: items = [], registry, rawErrors, name, } = this.props;
        const { widgets, formContext, globalUiOptions, schemaUtils } = registry;
        const { widget, title: uiTitle, ...options } = (0,lib_index_js_.getUiOptions)(uiSchema, globalUiOptions);
        const Widget = (0,lib_index_js_.getWidget)(schema, widget, widgets);
        const label = (_a = uiTitle !== null && uiTitle !== void 0 ? uiTitle : schema.title) !== null && _a !== void 0 ? _a : name;
        const displayLabel = schemaUtils.getDisplayLabel(schema, uiSchema, globalUiOptions);
        return ((0,jsx_runtime.jsx)(Widget, { id: idSchema.$id, name: name, multiple: true, onChange: this.onSelectChange, onBlur: onBlur, onFocus: onFocus, options: options, schema: schema, uiSchema: uiSchema, registry: registry, value: items, disabled: disabled, readonly: readonly, hideError: hideError, required: required, label: label, hideLabel: !displayLabel, placeholder: placeholder, formContext: formContext, autofocus: autofocus, rawErrors: rawErrors }));
    }
    /** Renders an array as a set of checkboxes
     */
    renderMultiSelect() {
        var _a;
        const { schema, idSchema, uiSchema, formData: items = [], disabled = false, readonly = false, autofocus = false, required = false, placeholder, onBlur, onFocus, registry, rawErrors, name, } = this.props;
        const { widgets, schemaUtils, formContext, globalUiOptions } = registry;
        const itemsSchema = schemaUtils.retrieveSchema(schema.items, items);
        const enumOptions = (0,lib_index_js_.optionsList)(itemsSchema);
        const { widget = 'select', title: uiTitle, ...options } = (0,lib_index_js_.getUiOptions)(uiSchema, globalUiOptions);
        const Widget = (0,lib_index_js_.getWidget)(schema, widget, widgets);
        const label = (_a = uiTitle !== null && uiTitle !== void 0 ? uiTitle : schema.title) !== null && _a !== void 0 ? _a : name;
```
