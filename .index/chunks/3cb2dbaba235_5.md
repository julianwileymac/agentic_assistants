# Chunk: 3cb2dbaba235_5

- source: `.venv-lab/Lib/site-packages/notebook/static/2816.03541f3103bf4c09e591.js`
- lines: 401-516
- chunk: 6/27

```
f, () => ref.current, [ref.current]);

  return react_index_js_default().createElement(
    'jp-breadcrumb',
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

;// CONCATENATED MODULE: ../node_modules/@jupyter/react-components/lib/BreadcrumbItem.js



(0,index_js_.provideJupyterDesignSystem)().register((0,index_js_.jpBreadcrumbItem)());

const BreadcrumbItem = (0,react_index_js_.forwardRef)((props, forwardedRef) => {
  const ref = (0,react_index_js_.useRef)(null);
  const {
    className,
    download,
    href,
    hreflang,
    ping,
    referrerpolicy,
    rel,
    target,
    type,
    control,
    ...filteredProps
  } = props;

  /** Properties - run whenever a property has changed */
  useProperties(ref, 'control', props.control);

  /** Methods - uses `useImperativeHandle` hook to pass ref to component */
  (0,react_index_js_.useImperativeHandle)(forwardedRef, () => ref.current, [ref.current]);

  return react_index_js_default().createElement(
    'jp-breadcrumb-item',
    {
      ref,
      ...filteredProps,
      download: props.download,
      href: props.href,
      hreflang: props.hreflang,
      ping: props.ping,
      referrerpolicy: props.referrerpolicy,
      rel: props.rel,
      target: props.target,
      type: props.type,
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

;// CONCATENATED MODULE: ../node_modules/@jupyter/react-components/lib/Button.js



(0,index_js_.provideJupyterDesignSystem)().register((0,index_js_.jpButton)());

const Button = (0,react_index_js_.forwardRef)((props, forwardedRef) => {
  const ref = (0,react_index_js_.useRef)(null);
  const {
    className,
    minimal,
    appearance,
    form,
    formaction,
    formenctype,
    formmethod,
    formtarget,
    type,
    autofocus,
    formnovalidate,
    defaultSlottedContent,
    disabled,
    required,
    ...filteredProps
  } = props;

  /** Properties - run whenever a property has changed */
  useProperties(ref, 'autofocus', props.autofocus);
  useProperties(ref, 'formnovalidate', props.formnovalidate);
  useProperties(ref, 'defaultSlottedContent', props.defaultSlottedContent);
  useProperties(ref, 'disabled', props.disabled);
  useProperties(ref, 'required', props.required);

  /** Methods - uses `useImperativeHandle` hook to pass ref to component */
  (0,react_index_js_.useImperativeHandle)(forwardedRef, () => ref.current, [ref.current]);

  return react_index_js_default().createElement(
    'jp-button',
    {
      ref,
      ...filteredProps,
      appearance: props.appearance,
      form: props.form,
      formaction: props.formaction,
      formenctype: props.formenctype,
```
