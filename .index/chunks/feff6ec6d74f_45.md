# Chunk: feff6ec6d74f_45

- source: `.venv-lab/Lib/site-packages/notebook/static/1871.c375ee093b7e51966390.js`
- lines: 1926-1973
- chunk: 46/78

```
he props
            setLastValue(value);
            setState((0,lib_index_js_.parseDateString)(value, time));
        }
    }, [time, value, onChange, state, lastValue]);
    const handleChange = (0,index_js_.useCallback)((property, value) => {
        setState({ [property]: value });
    }, []);
    const handleSetNow = (0,index_js_.useCallback)((event) => {
        event.preventDefault();
        if (disabled || readonly) {
            return;
        }
        const nextState = (0,lib_index_js_.parseDateString)(new Date().toJSON(), time);
        onChange((0,lib_index_js_.toDateString)(nextState, time));
    }, [disabled, readonly, time]);
    const handleClear = (0,index_js_.useCallback)((event) => {
        event.preventDefault();
        if (disabled || readonly) {
            return;
        }
        onChange(undefined);
    }, [disabled, readonly, onChange]);
    return ((0,jsx_runtime.jsxs)("ul", { className: 'list-inline', children: [dateElementProps(state, time, options.yearsRange).map((elemProps, i) => ((0,jsx_runtime.jsx)("li", { className: 'list-inline-item', children: (0,jsx_runtime.jsx)(DateElement, { rootId: id, name: name, select: handleChange, ...elemProps, disabled: disabled, readonly: readonly, registry: registry, onBlur: onBlur, onFocus: onFocus, autofocus: autofocus && i === 0 }) }, i))), (options.hideNowButton !== 'undefined' ? !options.hideNowButton : true) && ((0,jsx_runtime.jsx)("li", { className: 'list-inline-item', children: (0,jsx_runtime.jsx)("a", { href: '#', className: 'btn btn-info btn-now', onClick: handleSetNow, children: translateString(lib_index_js_.TranslatableString.NowLabel) }) })), (options.hideClearButton !== 'undefined' ? !options.hideClearButton : true) && ((0,jsx_runtime.jsx)("li", { className: 'list-inline-item', children: (0,jsx_runtime.jsx)("a", { href: '#', className: 'btn btn-warning btn-clear', onClick: handleClear, children: translateString(lib_index_js_.TranslatableString.ClearLabel) }) }))] }));
}
/* harmony default export */ const widgets_AltDateWidget = (AltDateWidget);
//# sourceMappingURL=AltDateWidget.js.map
;// CONCATENATED MODULE: ../node_modules/@rjsf/core/lib/components/widgets/AltDateTimeWidget.js

/** The `AltDateTimeWidget` is an alternative widget for rendering datetime properties.
 *  It uses the AltDateWidget for rendering, with the `time` prop set to true by default.
 *
 * @param props - The `WidgetProps` for this component
 */
function AltDateTimeWidget({ time = true, ...props }) {
    const { AltDateWidget } = props.registry.widgets;
    return (0,jsx_runtime.jsx)(AltDateWidget, { time: time, ...props });
}
/* harmony default export */ const widgets_AltDateTimeWidget = (AltDateTimeWidget);
//# sourceMappingURL=AltDateTimeWidget.js.map
;// CONCATENATED MODULE: ../node_modules/@rjsf/core/lib/components/widgets/CheckboxWidget.js



/** The `CheckBoxWidget` is a widget for rendering boolean properties.
 *  It is typically used to represent a boolean.
 *
```
