# Chunk: f93d0ac7ec3f_6

- source: `.venv-lab/Lib/site-packages/notebook/static/8929.22828925bc31ed18e912.js`
- lines: 419-520
- chunk: 7/154

```
tch the cursor and selection.
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
            r2 = 0;
            c1 = cs ? cs.c1 : 0;
            c2 = cs ? cs.c2 : 0;
            cr = r;
            cc = c;
            clear = 'current';
        }
        else if (shift) {
            r1 = cs ? cs.r1 : 0;
            r2 = cs ? cs.r2 - 1 : 0;
            c1 = cs ? cs.c1 : 0;
            c2 = cs ? cs.c2 : 0;
            cr = r;
            cc = c;
            clear = 'current';
        }
        else if (accel) {
            r1 = 0;
            r2 = 0;
            c1 = c;
            c2 = c;
            cr = r1;
            cc = c1;
            clear = 'all';
        }
        else {
            r1 = r - 1;
            r2 = r - 1;
            c1 = c;
            c2 = c;
            cr = r1;
            cc = c1;
            clear = 'all';
        }
        // Create the new selection.
        model.select({ r1, c1, r2, c2, cursorRow: cr, cursorColumn: cc, clear });
        // Re-fetch the current selection.
        cs = model.currentSelection();
        // Bail if there is no selection.
        if (!cs) {
            return;
        }
        // Scroll the grid appropriately.
        if (shift || mode === 'row') {
            grid.scrollToRow(cs.r2);
        }
        else {
            grid.scrollToCursor();
        }
    }
    /**
     * Handle the `'ArrowDown'` key press for the data grid.
     *
     * @param grid - The data grid of interest.
     *
     * @param event - The keyboard event of interest.
     */
    onArrowDown(grid, event) {
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
            grid.scrollTo(grid.scrollX, grid.maxScrollY);
            return;
        }
        // Handle no model and no modifier. (ignore shift)
        if (!model) {
            grid.scrollByStep('down');
            return;
        }
        // Fetch the selection mode.
        let mode = model.selectionMode;
        // Handle the column selection mode with accel key.
        if (mode === 'column' && accel) {
            grid.scrollTo(grid.scrollX, grid.maxScrollY);
            return;
        }
        // Handle the column selection mode with no modifier. (ignore shift)
        if (mode === 'column') {
            grid.scrollByStep('down');
```
