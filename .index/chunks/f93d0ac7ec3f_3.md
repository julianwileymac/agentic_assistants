# Chunk: f93d0ac7ec3f_3

- source: `.venv-lab/Lib/site-packages/notebook/static/8929.22828925bc31ed18e912.js`
- lines: 153-251
- chunk: 4/154

```
elete':
                this.onDelete(grid, event);
                break;
            case 'C':
                this.onKeyC(grid, event);
                break;
            case 'Enter':
                if (grid.selectionModel) {
                    grid.moveCursor(event.shiftKey ? 'up' : 'down');
                    grid.scrollToCursor();
                }
                break;
            case 'Tab':
                if (grid.selectionModel) {
                    grid.moveCursor(event.shiftKey ? 'left' : 'right');
                    grid.scrollToCursor();
                    event.stopPropagation();
                    event.preventDefault();
                }
                break;
        }
    }
    /**
     * Handle the `'ArrowLeft'` key press for the data grid.
     *
     * @param grid - The data grid of interest.
     *
     * @param event - The keyboard event of interest.
     */
    onArrowLeft(grid, event) {
        // Stop the event propagation.
        event.preventDefault();
        event.stopPropagation();
        // Fetch the selection model.
        let model = grid.selectionModel;
        // Fetch the modifier flags.
        let shift = event.shiftKey;
        let accel = _lumino_domutils__WEBPACK_IMPORTED_MODULE_0__.Platform.accelKey(event);
        // Handle no model with the accel modifier.
        if (!model && accel) {
            grid.scrollTo(0, grid.scrollY);
            return;
        }
        // Handle no model and no modifier. (ignore shift)
        if (!model) {
            grid.scrollByStep('left');
            return;
        }
        // Fetch the selection mode.
        let mode = model.selectionMode;
        // Handle the row selection mode with accel key.
        if (mode === 'row' && accel) {
            grid.scrollTo(0, grid.scrollY);
            return;
        }
        // Handle the row selection mode with no modifier. (ignore shift)
        if (mode === 'row') {
            grid.scrollByStep('left');
            return;
        }
        // Fetch the cursor and selection.
        let r = model.cursorRow;
        let c = model.cursorColumn;
        let cs = model.currentSelection();
        // Set up the selection variables.
        let r1;
        let r2;
        let c1;
        let c2;
        let cr;
        let cc;
        let clear;
        // Dispatch based on the modifier keys.
        if (accel && shift) {
            r1 = cs ? cs.r1 : 0;
            r2 = cs ? cs.r2 : 0;
            c1 = cs ? cs.c1 : 0;
            c2 = 0;
            cr = r;
            cc = c;
            clear = 'current';
        }
        else if (shift) {
            r1 = cs ? cs.r1 : 0;
            r2 = cs ? cs.r2 : 0;
            c1 = cs ? cs.c1 : 0;
            c2 = cs ? cs.c2 - 1 : 0;
            cr = r;
            cc = c;
            clear = 'current';
        }
        else if (accel) {
            r1 = r;
            r2 = r;
            c1 = 0;
            c2 = 0;
            cr = r1;
            cc = c1;
```
