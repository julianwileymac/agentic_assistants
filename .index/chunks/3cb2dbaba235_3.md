# Chunk: 3cb2dbaba235_3

- source: `.venv-lab/Lib/site-packages/notebook/static/2816.03541f3103bf4c09e591.js`
- lines: 231-323
- chunk: 4/27

```
ositioningMode || props['horizontal-positioning-mode'],
      'horizontal-default-position':
        props.horizontalDefaultPosition || props['horizontal-default-position'],
      'horizontal-threshold':
        props.horizontalThreshold || props['horizontal-threshold'],
      'horizontal-scaling':
        props.horizontalScaling || props['horizontal-scaling'],
      'vertical-positioning-mode':
        props.verticalPositioningMode || props['vertical-positioning-mode'],
      'vertical-default-position':
        props.verticalDefaultPosition || props['vertical-default-position'],
      'vertical-threshold':
        props.verticalThreshold || props['vertical-threshold'],
      'vertical-scaling': props.verticalScaling || props['vertical-scaling'],
      'auto-update-mode': props.autoUpdateMode || props['auto-update-mode'],
      class: props.className,
      exportparts: props.exportparts,
      for: props.htmlFor,
      part: props.part,
      tabindex: props.tabIndex,
      'horizontal-viewport-lock': props.horizontalViewportLock ? '' : undefined,
      'horizontal-inset': props.horizontalInset ? '' : undefined,
      'vertical-viewport-lock': props.verticalViewportLock ? '' : undefined,
      'vertical-inset': props.verticalInset ? '' : undefined,
      'fixed-placement': props.fixedPlacement ? '' : undefined,
      style: { ...props.style }
    },
    props.children
  );
});

;// CONCATENATED MODULE: ../node_modules/@jupyter/react-components/lib/Anchor.js



(0,index_js_.provideJupyterDesignSystem)().register((0,index_js_.jpAnchor)());

const Anchor = (0,react_index_js_.forwardRef)((props, forwardedRef) => {
  const ref = (0,react_index_js_.useRef)(null);
  const {
    className,
    appearance,
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
    'jp-anchor',
    {
      ref,
      ...filteredProps,
      appearance: props.appearance,
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

;// CONCATENATED MODULE: ../node_modules/@jupyter/react-components/lib/Avatar.js



(0,index_js_.provideJupyterDesignSystem)().register((0,index_js_.jpAvatar)());

const Avatar = (0,react_index_js_.forwardRef)((props, forwardedRef) => {
```
