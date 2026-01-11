# Chunk: 3cb2dbaba235_4

- source: `.venv-lab/Lib/site-packages/notebook/static/2816.03541f3103bf4c09e591.js`
- lines: 310-413
- chunk: 5/27

```
 style: { ...props.style }
    },
    props.children
  );
});

;// CONCATENATED MODULE: ../node_modules/@jupyter/react-components/lib/Avatar.js



(0,index_js_.provideJupyterDesignSystem)().register((0,index_js_.jpAvatar)());

const Avatar = (0,react_index_js_.forwardRef)((props, forwardedRef) => {
  const ref = (0,react_index_js_.useRef)(null);
  const { className, src, alt, fill, color, link, shape, ...filteredProps } =
    props;

  /** Properties - run whenever a property has changed */

  /** Methods - uses `useImperativeHandle` hook to pass ref to component */
  (0,react_index_js_.useImperativeHandle)(forwardedRef, () => ref.current, [ref.current]);

  return react_index_js_default().createElement(
    'jp-avatar',
    {
      ref,
      ...filteredProps,
      src: props.src,
      alt: props.alt,
      fill: props.fill,
      color: props.color,
      link: props.link,
      shape: props.shape,
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

;// CONCATENATED MODULE: ../node_modules/@jupyter/react-components/lib/Badge.js



(0,index_js_.provideJupyterDesignSystem)().register((0,index_js_.jpBadge)());

const Badge = (0,react_index_js_.forwardRef)((props, forwardedRef) => {
  const ref = (0,react_index_js_.useRef)(null);
  const { className, fill, color, circular, ...filteredProps } = props;

  /** Properties - run whenever a property has changed */
  useProperties(ref, 'circular', props.circular);

  /** Methods - uses `useImperativeHandle` hook to pass ref to component */
  (0,react_index_js_.useImperativeHandle)(forwardedRef, () => ref.current, [ref.current]);

  return react_index_js_default().createElement(
    'jp-badge',
    {
      ref,
      ...filteredProps,
      fill: props.fill,
      color: props.color,
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

;// CONCATENATED MODULE: ../node_modules/@jupyter/react-components/lib/Breadcrumb.js



(0,index_js_.provideJupyterDesignSystem)().register((0,index_js_.jpBreadcrumb)());

const Breadcrumb = (0,react_index_js_.forwardRef)((props, forwardedRef) => {
  const ref = (0,react_index_js_.useRef)(null);
  const { className, ...filteredProps } = props;

  /** Properties - run whenever a property has changed */

  /** Methods - uses `useImperativeHandle` hook to pass ref to component */
  (0,react_index_js_.useImperativeHandle)(forwardedRef, () => ref.current, [ref.current]);

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
```
