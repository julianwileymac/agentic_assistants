# Chunk: 3cb2dbaba235_7

- source: `.venv-lab/Lib/site-packages/notebook/static/2816.03541f3103bf4c09e591.js`
- lines: 597-708
- chunk: 8/27

```
  allClasses += ' indeterminate';
  }

  return react_index_js_default().createElement(
    'jp-checkbox',
    {
      ref,
      ...filteredProps,
      class: allClasses.trim(),
      exportparts: props.exportparts,
      for: props.htmlFor,
      part: props.part,
      tabindex: props.tabIndex,
      readonly: props.readonly ? '' : undefined,
      style: { ...props.style }
    },
    props.children
  );
});

;// CONCATENATED MODULE: ../node_modules/@jupyter/react-components/lib/Combobox.js



(0,index_js_.provideJupyterDesignSystem)().register((0,index_js_.jpCombobox)());

const Combobox = (0,react_index_js_.forwardRef)((props, forwardedRef) => {
  const ref = (0,react_index_js_.useRef)(null);
  const {
    className,
    autowidth,
    minimal,
    open,
    autocomplete,
    placeholder,
    position,
    autoWidth,
    filteredOptions,
    options,
    value,
    length,
    disabled,
    selectedIndex,
    selectedOptions,
    required,
    ...filteredProps
  } = props;

  /** Event listeners - run once */
  useEventListener(ref, 'input', props.onInput);
  useEventListener(ref, 'change', props.onChange);

  /** Properties - run whenever a property has changed */
  useProperties(ref, 'autoWidth', props.autoWidth);
  useProperties(ref, 'filteredOptions', props.filteredOptions);
  useProperties(ref, 'options', props.options);
  useProperties(ref, 'value', props.value);
  useProperties(ref, 'length', props.length);
  useProperties(ref, 'disabled', props.disabled);
  useProperties(ref, 'selectedIndex', props.selectedIndex);
  useProperties(ref, 'selectedOptions', props.selectedOptions);
  useProperties(ref, 'required', props.required);

  /** Methods - uses `useImperativeHandle` hook to pass ref to component */
  (0,react_index_js_.useImperativeHandle)(forwardedRef, () => ref.current, [ref.current]);

  return react_index_js_default().createElement(
    'jp-combobox',
    {
      ref,
      ...filteredProps,
      autocomplete: props.autocomplete,
      placeholder: props.placeholder,
      position: props.position,
      class: props.className,
      exportparts: props.exportparts,
      for: props.htmlFor,
      part: props.part,
      tabindex: props.tabIndex,
      autowidth: props.autowidth ? '' : undefined,
      minimal: props.minimal ? '' : undefined,
      open: props.open ? '' : undefined,
      style: { ...props.style }
    },
    props.children
  );
});

;// CONCATENATED MODULE: ../node_modules/@jupyter/react-components/lib/DateField.js



(0,index_js_.provideJupyterDesignSystem)().register((0,index_js_.jpDateField)());

const DateField = (0,react_index_js_.forwardRef)((props, forwardedRef) => {
  const ref = (0,react_index_js_.useRef)(null);
  const {
    className,
    autofocus,
    step,
    max,
    min,
    disabled,
    required,
    ...filteredProps
  } = props;

  /** Event listeners - run once */
  useEventListener(ref, 'input', props.onInput);
  useEventListener(ref, 'change', props.onChange);
```
