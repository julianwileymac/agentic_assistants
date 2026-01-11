# Chunk: feff6ec6d74f_44

- source: `.venv-lab/Lib/site-packages/notebook/static/1871.c375ee093b7e51966390.js`
- lines: 1874-1934
- chunk: 45/78

```
MappingURL=index.js.map
;// CONCATENATED MODULE: ../node_modules/@rjsf/core/lib/components/widgets/AltDateWidget.js



function rangeOptions(start, stop) {
    const options = [];
    for (let i = start; i <= stop; i++) {
        options.push({ value: i, label: (0,lib_index_js_.pad)(i, 2) });
    }
    return options;
}
function readyForChange(state) {
    return Object.values(state).every((value) => value !== -1);
}
function dateElementProps(state, time, yearsRange = [1900, new Date().getFullYear() + 2]) {
    const { year, month, day, hour, minute, second } = state;
    const data = [
        {
            type: 'year',
            range: yearsRange,
            value: year,
        },
        { type: 'month', range: [1, 12], value: month },
        { type: 'day', range: [1, 31], value: day },
    ];
    if (time) {
        data.push({ type: 'hour', range: [0, 23], value: hour }, { type: 'minute', range: [0, 59], value: minute }, { type: 'second', range: [0, 59], value: second });
    }
    return data;
}
function DateElement({ type, range, value, select, rootId, name, disabled, readonly, autofocus, registry, onBlur, onFocus, }) {
    const id = rootId + '_' + type;
    const { SelectWidget } = registry.widgets;
    return ((0,jsx_runtime.jsx)(SelectWidget, { schema: { type: 'integer' }, id: id, name: name, className: 'form-control', options: { enumOptions: rangeOptions(range[0], range[1]) }, placeholder: type, value: value, disabled: disabled, readonly: readonly, autofocus: autofocus, onChange: (value) => select(type, value), onBlur: onBlur, onFocus: onFocus, registry: registry, label: '', "aria-describedby": (0,lib_index_js_.ariaDescribedByIds)(rootId) }));
}
/** The `AltDateWidget` is an alternative widget for rendering date properties.
 * @param props - The `WidgetProps` for this component
 */
function AltDateWidget({ time = false, disabled = false, readonly = false, autofocus = false, options, id, name, registry, onBlur, onFocus, onChange, value, }) {
    const { translateString } = registry;
    const [lastValue, setLastValue] = (0,index_js_.useState)(value);
    const [state, setState] = (0,index_js_.useReducer)((state, action) => {
        return { ...state, ...action };
    }, (0,lib_index_js_.parseDateString)(value, time));
    (0,index_js_.useEffect)(() => {
        const stateValue = (0,lib_index_js_.toDateString)(state, time);
        if (readyForChange(state) && stateValue !== value) {
            // The user changed the date to a new valid data via the comboboxes, so call onChange
            onChange(stateValue);
        }
        else if (lastValue !== value) {
            // We got a new value in the props
            setLastValue(value);
            setState((0,lib_index_js_.parseDateString)(value, time));
        }
    }, [time, value, onChange, state, lastValue]);
    const handleChange = (0,index_js_.useCallback)((property, value) => {
        setState({ [property]: value });
    }, []);
```
