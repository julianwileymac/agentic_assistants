# Chunk: feff6ec6d74f_69

- source: `.venv-lab/Lib/site-packages/notebook/static/1871.c375ee093b7e51966390.js`
- lines: 3253-3365
- chunk: 70/78

```
revItemChangeId) {
                this.sheet.splice(curIndex, 1, item.getStyles());
                this.changeId++;
                this.changes.change(item, curIndex, curIndex);
            }
        }
    }
    remove(style) {
        const count = this._counters[style.id];
        if (count) {
            this._counters[style.id] = count - 1;
            const item = this._children[style.id];
            const index = this._keys.indexOf(item.id);
            if (count === 1) {
                delete this._counters[style.id];
                delete this._children[style.id];
                this._keys.splice(index, 1);
                this.sheet.splice(index, 1);
                this.changeId++;
                this.changes.remove(item, index);
            }
            else if (item instanceof Cache && style instanceof Cache) {
                const prevChangeId = item.changeId;
                item.unmerge(style);
                if (item.changeId !== prevChangeId) {
                    this.sheet.splice(index, 1, item.getStyles());
                    this.changeId++;
                    this.changes.change(item, index, index);
                }
            }
        }
    }
    values() {
        return this._keys.map(key => this._children[key]);
    }
    merge(cache) {
        for (const item of cache.values())
            this.add(item);
        return this;
    }
    unmerge(cache) {
        for (const item of cache.values())
            this.remove(item);
        return this;
    }
    clone() {
        return new Cache().merge(this);
    }
}
/**
 * Selector is a dumb class made to represent nested CSS selectors.
 */
class Selector {
    constructor(selector, id) {
        this.selector = selector;
        this.id = id;
    }
    getStyles() {
        return this.selector;
    }
    clone() {
        return this;
    }
}
/**
 * The style container registers a style string with selectors.
 */
class Style extends Cache {
    constructor(style, id) {
        super();
        this.style = style;
        this.id = id;
    }
    getStyles() {
        return `${this.sheet.join(",")}{${this.style}}`;
    }
    clone() {
        return new Style(this.style, this.id).merge(this);
    }
}
/**
 * Implement rule logic for style output.
 */
class Rule extends Cache {
    constructor(rule, style, id) {
        super();
        this.rule = rule;
        this.style = style;
        this.id = id;
    }
    getStyles() {
        return `${this.rule}{${this.style}${join(this.sheet)}}`;
    }
    clone() {
        return new Rule(this.rule, this.style, this.id).merge(this);
    }
}
function key(pid, styles) {
    const key = `f${stringHash(pid)}`;
    if (true)
        return key;
    return `${styles.$displayName}_${key}`;
}
/**
 * The FreeStyle class implements the API for everything else.
 */
class FreeStyle extends Cache {
    constructor(id, changes) {
        super(changes);
        this.id = id;
    }
    registerStyle(styles) {
```
