# Chunk: 3cb2dbaba235_2

- source: `.venv-lab/Lib/site-packages/notebook/static/2816.03541f3103bf4c09e591.js`
- lines: 145-237
- chunk: 3/27

```
index_js_.useRef)(null);
  const { className, headingLevel, id, expanded, ...filteredProps } = props;

  /** Event listeners - run once */
  useEventListener(ref, 'change', props.onChange);

  /** Properties - run whenever a property has changed */
  useProperties(ref, 'expanded', props.expanded);

  /** Methods - uses `useImperativeHandle` hook to pass ref to component */
  (0,react_index_js_.useImperativeHandle)(forwardedRef, () => ref.current, [ref.current]);

  return react_index_js_default().createElement(
    'jp-accordion-item',
    {
      ref,
      ...filteredProps,
      'heading-level': props.headingLevel || props['heading-level'],
      id: props.id,
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

;// CONCATENATED MODULE: ../node_modules/@jupyter/react-components/lib/AnchoredRegion.js



(0,index_js_.provideJupyterDesignSystem)().register((0,index_js_.jpAnchoredRegion)());

const AnchoredRegion = (0,react_index_js_.forwardRef)((props, forwardedRef) => {
  const ref = (0,react_index_js_.useRef)(null);
  const {
    className,
    horizontalViewportLock,
    horizontalInset,
    verticalViewportLock,
    verticalInset,
    fixedPlacement,
    anchor,
    viewport,
    horizontalPositioningMode,
    horizontalDefaultPosition,
    horizontalThreshold,
    horizontalScaling,
    verticalPositioningMode,
    verticalDefaultPosition,
    verticalThreshold,
    verticalScaling,
    autoUpdateMode,
    anchorElement,
    viewportElement,
    verticalPosition,
    horizontalPosition,
    update,
    ...filteredProps
  } = props;

  /** Event listeners - run once */
  useEventListener(ref, 'loaded', props.onLoaded);
  useEventListener(ref, 'positionchange', props.onPositionchange);

  /** Properties - run whenever a property has changed */
  useProperties(ref, 'anchorElement', props.anchorElement);
  useProperties(ref, 'viewportElement', props.viewportElement);
  useProperties(ref, 'verticalPosition', props.verticalPosition);
  useProperties(ref, 'horizontalPosition', props.horizontalPosition);
  useProperties(ref, 'update', props.update);

  /** Methods - uses `useImperativeHandle` hook to pass ref to component */
  (0,react_index_js_.useImperativeHandle)(forwardedRef, () => ref.current, [ref.current]);

  return react_index_js_default().createElement(
    'jp-anchored-region',
    {
      ref,
      ...filteredProps,
      anchor: props.anchor,
      viewport: props.viewport,
      'horizontal-positioning-mode':
        props.horizontalPositioningMode || props['horizontal-positioning-mode'],
      'horizontal-default-position':
        props.horizontalDefaultPosition || props['horizontal-default-position'],
      'horizontal-threshold':
        props.horizontalThreshold || props['horizontal-threshold'],
      'horizontal-scaling':
```
