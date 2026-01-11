# Chunk: feff6ec6d74f_15

- source: `.venv-lab/Lib/site-packages/notebook/static/1871.c375ee093b7e51966390.js`
- lines: 811-862
- chunk: 16/78

```
            const { schemaUtils } = registry;
            const intOption = option !== undefined ? parseInt(option, 10) : -1;
            if (intOption === selectedOption) {
                return;
            }
            const newOption = intOption >= 0 ? retrievedOptions[intOption] : undefined;
            const oldOption = selectedOption >= 0 ? retrievedOptions[selectedOption] : undefined;
            let newFormData = schemaUtils.sanitizeDataForNewSchema(newOption, oldOption, formData);
            if (newFormData && newOption) {
                // Call getDefaultFormState to make sure defaults are populated on change. Pass "excludeObjectChildren"
                // so that only the root objects themselves are created without adding undefined children properties
                newFormData = schemaUtils.getDefaultFormState(newOption, newFormData, 'excludeObjectChildren');
            }
            onChange(newFormData, undefined, this.getFieldId());
            this.setState({ selectedOption: intOption });
        };
        const { formData, options, registry: { schemaUtils }, } = this.props;
        // cache the retrieved options in state in case they have $refs to save doing it later
        const retrievedOptions = options.map((opt) => schemaUtils.retrieveSchema(opt, formData));
        this.state = {
            retrievedOptions,
            selectedOption: this.getMatchingOption(0, formData, retrievedOptions),
        };
    }
    /** React lifecycle method that is called when the props and/or state for this component is updated. It recomputes the
     * currently selected option based on the overall `formData`
     *
     * @param prevProps - The previous `FieldProps` for this template
     * @param prevState - The previous `AnyOfFieldState` for this template
     */
    componentDidUpdate(prevProps, prevState) {
        const { formData, options, idSchema } = this.props;
        const { selectedOption } = this.state;
        let newState = this.state;
        if (!(0,lib_index_js_.deepEquals)(prevProps.options, options)) {
            const { registry: { schemaUtils }, } = this.props;
            // re-cache the retrieved options in state in case they have $refs to save doing it later
            const retrievedOptions = options.map((opt) => schemaUtils.retrieveSchema(opt, formData));
            newState = { selectedOption, retrievedOptions };
        }
        if (!(0,lib_index_js_.deepEquals)(formData, prevProps.formData) && idSchema.$id === prevProps.idSchema.$id) {
            const { retrievedOptions } = newState;
            const matchingOption = this.getMatchingOption(selectedOption, formData, retrievedOptions);
            if (prevState && matchingOption !== selectedOption) {
                newState = { selectedOption: matchingOption, retrievedOptions };
            }
        }
        if (newState !== this.state) {
            this.setState(newState);
        }
    }
```
