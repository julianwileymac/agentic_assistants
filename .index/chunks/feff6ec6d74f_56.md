# Chunk: feff6ec6d74f_56

- source: `.venv-lab/Lib/site-packages/notebook/static/1871.c375ee093b7e51966390.js`
- lines: 2474-2522
- chunk: 57/78

```
               const newPaths = paths.map((path) => [...path, key]);
                        // If an object is marked with additionalProperties, all its keys are valid
                        if (_obj[key][lib_index_js_.RJSF_ADDITONAL_PROPERTIES_FLAG] && _obj[key][lib_index_js_.NAME_KEY] !== '') {
                            acc.push(_obj[key][lib_index_js_.NAME_KEY]);
                        }
                        else {
                            getAllPaths(_obj[key], acc, newPaths);
                        }
                    }
                    else if (key === lib_index_js_.NAME_KEY && _obj[key] !== '') {
                        paths.forEach((path) => {
                            const formValue = get_default()(formData, path);
                            // adds path to fieldNames if it points to a value
                            // or an empty object/array
                            if (typeof formValue !== 'object' ||
                                isEmpty_default()(formValue) ||
                                (Array.isArray(formValue) && formValue.every((val) => typeof val !== 'object'))) {
                                acc.push(path);
                            }
                        });
                    }
                });
                return acc;
            };
            return getAllPaths(pathSchema);
        };
        /** Function to handle changes made to a field in the `Form`. This handler receives an entirely new copy of the
         * `formData` along with a new `ErrorSchema`. It will first update the `formData` with any missing default fields and
         * then, if `omitExtraData` and `liveOmit` are turned on, the `formData` will be filterer to remove any extra data not
         * in a form field. Then, the resulting formData will be validated if required. The state will be updated with the new
         * updated (potentially filtered) `formData`, any errors that resulted from validation. Finally the `onChange`
         * callback will be called if specified with the updated state.
         *
         * @param formData - The new form data from a change to a field
         * @param newErrorSchema - The new `ErrorSchema` based on the field change
         * @param id - The id of the field that caused the change
         */
        this.onChange = (formData, newErrorSchema, id) => {
            const { extraErrors, omitExtraData, liveOmit, noValidate, liveValidate, onChange } = this.props;
            const { schemaUtils, schema, retrievedSchema } = this.state;
            if ((0,lib_index_js_.isObject)(formData) || Array.isArray(formData)) {
                const newState = this.getStateFromProps(this.props, formData, retrievedSchema);
                formData = newState.formData;
            }
            const mustValidate = !noValidate && liveValidate;
            let state = { formData, schema };
            let newFormData = formData;
            let _retrievedSchema;
```
