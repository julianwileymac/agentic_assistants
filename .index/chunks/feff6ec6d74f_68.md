# Chunk: feff6ec6d74f_68

- source: `.venv-lab/Lib/site-packages/notebook/static/1871.c375ee093b7e51966390.js`
- lines: 3172-3263
- chunk: 69/78

```
yles support (e.g. `.foo > @media > .bar`).
        if (style && parent) {
            child.styles.push({ selector: parent, style, isUnique });
        }
        for (const [name, value] of nested) {
            pid += name + stylize(name, value, child.rules, child.styles, parent);
        }
    }
    else {
        const key = parent ? interpolate(selector, parent) : selector;
        if (style)
            stylesList.push({ selector: key, style, isUnique });
        for (const [name, value] of nested) {
            pid += name + stylize(name, value, rulesList, stylesList, key);
        }
    }
    return pid;
}
/**
 * Transform `stylize` tree into style objects.
 */
function composeStylize(cache, pid, rulesList, stylesList, className, isStyle) {
    for (const { selector, style, isUnique } of stylesList) {
        const key = isStyle ? interpolate(selector, className) : selector;
        const id = isUnique
            ? `u\0${(++uniqueId).toString(36)}`
            : `s\0${pid}\0${style}`;
        const item = new Style(style, id);
        item.add(new Selector(key, `k\0${pid}\0${key}`));
        cache.add(item);
    }
    for (const { selector, style, rules, styles } of rulesList) {
        const item = new Rule(selector, style, `r\0${pid}\0${selector}\0${style}`);
        composeStylize(item, pid, rules, styles, className, isStyle);
        cache.add(item);
    }
}
/**
 * Cache to list to styles.
 */
function join(arr) {
    let res = "";
    for (let i = 0; i < arr.length; i++)
        res += arr[i];
    return res;
}
/**
 * Noop changes.
 */
const noopChanges = {
    add: () => undefined,
    change: () => undefined,
    remove: () => undefined
};
/**
 * Implement a cache/event emitter.
 */
class Cache {
    constructor(changes = noopChanges) {
        this.changes = changes;
        this.sheet = [];
        this.changeId = 0;
        this._keys = [];
        this._children = Object.create(null);
        this._counters = Object.create(null);
    }
    add(style) {
        const count = this._counters[style.id] || 0;
        const item = this._children[style.id] || style.clone();
        this._counters[style.id] = count + 1;
        if (count === 0) {
            this._children[item.id] = item;
            this._keys.push(item.id);
            this.sheet.push(item.getStyles());
            this.changeId++;
            this.changes.add(item, this._keys.length - 1);
        }
        else if (item instanceof Cache && style instanceof Cache) {
            const curIndex = this._keys.indexOf(style.id);
            const prevItemChangeId = item.changeId;
            item.merge(style);
            if (item.changeId !== prevItemChangeId) {
                this.sheet.splice(curIndex, 1, item.getStyles());
                this.changeId++;
                this.changes.change(item, curIndex, curIndex);
            }
        }
    }
    remove(style) {
        const count = this._counters[style.id];
        if (count) {
```
