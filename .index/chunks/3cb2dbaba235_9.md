# Chunk: 3cb2dbaba235_9

- source: `.venv-lab/Lib/site-packages/notebook/static/2816.03541f3103bf4c09e591.js`
- lines: 786-880
- chunk: 10/27

```
react-components/lib/DataGridRow.js



(0,index_js_.provideJupyterDesignSystem)().register((0,index_js_.jpDataGridRow)());

const DataGridRow = (0,react_index_js_.forwardRef)((props, forwardedRef) => {
  const ref = (0,react_index_js_.useRef)(null);
  const {
    className,
    gridTemplateColumns,
    rowType,
    rowData,
    columnDefinitions,
    cellItemTemplate,
    headerCellItemTemplate,
    rowIndex,
    ...filteredProps
  } = props;

  /** Event listeners - run once */
  useEventListener(ref, 'row-focused', props.onRowFocused);

  /** Properties - run whenever a property has changed */
  useProperties(ref, 'rowData', props.rowData);
  useProperties(ref, 'columnDefinitions', props.columnDefinitions);
  useProperties(ref, 'cellItemTemplate', props.cellItemTemplate);
  useProperties(ref, 'headerCellItemTemplate', props.headerCellItemTemplate);
  useProperties(ref, 'rowIndex', props.rowIndex);

  /** Methods - uses `useImperativeHandle` hook to pass ref to component */
  (0,react_index_js_.useImperativeHandle)(forwardedRef, () => ref.current, [ref.current]);

  // Add web component internal classes on top of `className`
  let allClasses = className ?? '';
  if (ref.current) {
    if (ref.current.rowType !== 'default') {
      allClasses += ` ${ref.current.rowType}`;
    }
  }

  return react_index_js_default().createElement(
    'jp-data-grid-row',
    {
      ref,
      ...filteredProps,
      'grid-template-columns':
        props.gridTemplateColumns || props['grid-template-columns'],
      'row-type': props.rowType || props['row-type'],
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

;// CONCATENATED MODULE: ../node_modules/@jupyter/react-components/lib/DataGrid.js



(0,index_js_.provideJupyterDesignSystem)().register((0,index_js_.jpDataGrid)());

const DataGrid = (0,react_index_js_.forwardRef)((props, forwardedRef) => {
  const ref = (0,react_index_js_.useRef)(null);
  const {
    className,
    noTabbing,
    generateHeader,
    gridTemplateColumns,
    rowsData,
    columnDefinitions,
    rowItemTemplate,
    cellItemTemplate,
    headerCellItemTemplate,
    focusRowIndex,
    focusColumnIndex,
    rowElementTag,
    ...filteredProps
  } = props;

  /** Properties - run whenever a property has changed */
  useProperties(ref, 'rowsData', props.rowsData);
  useProperties(ref, 'columnDefinitions', props.columnDefinitions);
  useProperties(ref, 'rowItemTemplate', props.rowItemTemplate);
  useProperties(ref, 'cellItemTemplate', props.cellItemTemplate);
  useProperties(ref, 'headerCellItemTemplate', props.headerCellItemTemplate);
  useProperties(ref, 'focusRowIndex', props.focusRowIndex);
  useProperties(ref, 'focusColumnIndex', props.focusColumnIndex);
  useProperties(ref, 'rowElementTag', props.rowElementTag);
```
