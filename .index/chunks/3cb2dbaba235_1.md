# Chunk: 3cb2dbaba235_1

- source: `.venv-lab/Lib/site-packages/notebook/static/2816.03541f3103bf4c09e591.js`
- lines: 62-154
- chunk: 2/27

```
s)
var index_js_ = __webpack_require__(83074);
// EXTERNAL MODULE: consume shared module (default) react@~18.2.0 (singleton) (fallback: ../node_modules/react/index.js)
var react_index_js_ = __webpack_require__(78156);
var react_index_js_default = /*#__PURE__*/__webpack_require__.n(react_index_js_);
;// CONCATENATED MODULE: ../node_modules/@jupyter/react-components/lib/react-utils.js


function useProperties(targetElement, propName, value) {
  (0,react_index_js_.useEffect)(() => {
    if (
      value !== undefined &&
      targetElement.current &&
      targetElement.current[propName] !== value
    ) {
      // add try catch to avoid errors when setting read-only properties
      try {
        targetElement.current[propName] = value;
      } catch (e) {
        console.warn(e);
      }
    }
  }, [value, targetElement.current]);
}

function useEventListener(targetElement, eventName, eventHandler) {
  (0,react_index_js_.useLayoutEffect)(() => {
    if (eventHandler !== undefined) {
      targetElement?.current?.addEventListener(eventName, eventHandler);
    }

    return () => {
      if (eventHandler?.cancel) {
        eventHandler.cancel();
      }

      targetElement?.current?.removeEventListener(eventName, eventHandler);
    };
  }, [eventName, eventHandler, targetElement.current]);
}

;// CONCATENATED MODULE: ../node_modules/@jupyter/react-components/lib/Accordion.js



(0,index_js_.provideJupyterDesignSystem)().register((0,index_js_.jpAccordion)());

const Accordion = (0,react_index_js_.forwardRef)((props, forwardedRef) => {
  const ref = (0,react_index_js_.useRef)(null);
  const { className, expandMode, ...filteredProps } = props;

  /** Event listeners - run once */
  useEventListener(ref, 'change', props.onChange);

  /** Properties - run whenever a property has changed */

  /** Methods - uses `useImperativeHandle` hook to pass ref to component */
  (0,react_index_js_.useImperativeHandle)(forwardedRef, () => ref.current, [ref.current]);

  return react_index_js_default().createElement(
    'jp-accordion',
    {
      ref,
      ...filteredProps,
      'expand-mode': props.expandMode || props['expand-mode'],
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

;// CONCATENATED MODULE: ../node_modules/@jupyter/react-components/lib/AccordionItem.js



(0,index_js_.provideJupyterDesignSystem)().register((0,index_js_.jpAccordionItem)());

const AccordionItem = (0,react_index_js_.forwardRef)((props, forwardedRef) => {
  const ref = (0,react_index_js_.useRef)(null);
  const { className, headingLevel, id, expanded, ...filteredProps } = props;

  /** Event listeners - run once */
  useEventListener(ref, 'change', props.onChange);

  /** Properties - run whenever a property has changed */
  useProperties(ref, 'expanded', props.expanded);
```
