# Chunk: 3cb2dbaba235_8

- source: `.venv-lab/Lib/site-packages/notebook/static/2816.03541f3103bf4c09e591.js`
- lines: 692-797
- chunk: 9/27

```
,react_index_js_.useRef)(null);
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

  /** Properties - run whenever a property has changed */
  useProperties(ref, 'autofocus', props.autofocus);
  useProperties(ref, 'step', props.step);
  useProperties(ref, 'max', props.max);
  useProperties(ref, 'min', props.min);
  useProperties(ref, 'disabled', props.disabled);
  useProperties(ref, 'required', props.required);

  /** Methods - uses `useImperativeHandle` hook to pass ref to component */
  (0,react_index_js_.useImperativeHandle)(forwardedRef, () => ref.current, [ref.current]);

  return react_index_js_default().createElement(
    'jp-date-field',
    {
      ref,
      ...filteredProps,
      class: props.className,
      exportparts: props.exportparts,
      for: props.htmlFor,
      part: props.part,
      tabindex: props.tabIndex,
      style: { ...props.style }
    },
    props.children
  );
});

;// CONCATENATED MODULE: ../node_modules/@jupyter/react-components/lib/DataGridCell.js



(0,index_js_.provideJupyterDesignSystem)().register((0,index_js_.jpDataGridCell)());

const DataGridCell = (0,react_index_js_.forwardRef)((props, forwardedRef) => {
  const ref = (0,react_index_js_.useRef)(null);
  const {
    className,
    cellType,
    gridColumn,
    rowData,
    columnDefinition,
    ...filteredProps
  } = props;

  /** Event listeners - run once */
  useEventListener(ref, 'cell-focused', props.onCellFocused);

  /** Properties - run whenever a property has changed */
  useProperties(ref, 'rowData', props.rowData);
  useProperties(ref, 'columnDefinition', props.columnDefinition);

  /** Methods - uses `useImperativeHandle` hook to pass ref to component */
  (0,react_index_js_.useImperativeHandle)(forwardedRef, () => ref.current, [ref.current]);

  // Add web component internal classes on top of `className`
  let allClasses = className ?? '';
  if (ref.current?.cellType === 'columnheader') {
    allClasses += ' column-header';
  }

  return react_index_js_default().createElement(
    'jp-data-grid-cell',
    {
      ref,
      ...filteredProps,
      'cell-type': props.cellType || props['cell-type'],
      'grid-column': props.gridColumn || props['grid-column'],
      class: allClasses.trim(),
      exportparts: props.exportparts,
      for: props.htmlFor,
      part: props.part,
      tabindex: props.tabIndex,
      style: { ...props.style }
    },
    props.children
  );
});

;// CONCATENATED MODULE: ../node_modules/@jupyter/react-components/lib/DataGridRow.js



(0,index_js_.provideJupyterDesignSystem)().register((0,index_js_.jpDataGridRow)());

const DataGridRow = (0,react_index_js_.forwardRef)((props, forwardedRef) => {
  const ref = (0,react_index_js_.useRef)(null);
  const {
    className,
    gridTemplateColumns,
```
