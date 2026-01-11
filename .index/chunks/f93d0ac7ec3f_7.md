# Chunk: f93d0ac7ec3f_7

- source: `.venv-lab/Lib/site-packages/notebook/static/8929.22828925bc31ed18e912.js`
- lines: 512-612
- chunk: 8/154

```
mode with accel key.
        if (mode === 'column' && accel) {
            grid.scrollTo(grid.scrollX, grid.maxScrollY);
            return;
        }
        // Handle the column selection mode with no modifier. (ignore shift)
        if (mode === 'column') {
            grid.scrollByStep('down');
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
            r2 = Infinity;
            c1 = cs ? cs.c1 : 0;
            c2 = cs ? cs.c2 : 0;
            cr = r;
            cc = c;
            clear = 'current';
        }
        else if (shift) {
            r1 = cs ? cs.r1 : 0;
            r2 = cs ? cs.r2 + 1 : 0;
            c1 = cs ? cs.c1 : 0;
            c2 = cs ? cs.c2 : 0;
            cr = r;
            cc = c;
            clear = 'current';
        }
        else if (accel) {
            r1 = Infinity;
            r2 = Infinity;
            c1 = c;
            c2 = c;
            cr = r1;
            cc = c1;
            clear = 'all';
        }
        else {
            r1 = r + 1;
            r2 = r + 1;
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
     * Handle the `'PageUp'` key press for the data grid.
     *
     * @param grid - The data grid of interest.
     *
     * @param event - The keyboard event of interest.
     */
    onPageUp(grid, event) {
        // Ignore the event if the accel key is pressed.
        if (_lumino_domutils__WEBPACK_IMPORTED_MODULE_0__.Platform.accelKey(event)) {
            return;
        }
        // Stop the event propagation.
        event.preventDefault();
        event.stopPropagation();
        // Fetch the selection model.
        let model = grid.selectionModel;
        // Scroll by page if there is no selection model.
        if (!model || model.selectionMode === 'column') {
            grid.scrollByPage('up');
            return;
        }
        // Get the normal number of cells in the page height.
        let n = Math.floor(grid.pageHeight / grid.defaultSizes.rowHeight);
        // Fetch the cursor and selection.
```
