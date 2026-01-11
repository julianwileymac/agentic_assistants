# Chunk: f93d0ac7ec3f_9

- source: `.venv-lab/Lib/site-packages/notebook/static/8929.22828925bc31ed18e912.js`
- lines: 690-783
- chunk: 10/154

```
iftKey) {
            r1 = cs ? cs.r1 : 0;
            r2 = cs ? cs.r2 + n : 0;
            c1 = cs ? cs.c1 : 0;
            c2 = cs ? cs.c2 : 0;
            cr = r;
            cc = c;
            clear = 'current';
        }
        else {
            r1 = cs ? cs.r1 + n : 0;
            r2 = r1;
            c1 = c;
            c2 = c;
            cr = r1;
            cc = c;
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
        grid.scrollToRow(cs.r2);
    }
    /**
     * Handle the `'Escape'` key press for the data grid.
     *
     * @param grid - The data grid of interest.
     *
     * @param event - The keyboard event of interest.
     */
    onEscape(grid, event) {
        if (grid.selectionModel) {
            grid.selectionModel.clear();
        }
    }
    /**
     * Handle the `'Delete'` key press for the data grid.
     *
     * @param grid - The data grid of interest.
     *
     * @param event - The keyboard event of interest.
     */
    onDelete(grid, event) {
        if (grid.editable && !grid.selectionModel.isEmpty) {
            const dataModel = grid.dataModel;
            // Fetch the max row and column.
            let maxRow = dataModel.rowCount('body') - 1;
            let maxColumn = dataModel.columnCount('body') - 1;
            for (let s of grid.selectionModel.selections()) {
                // Clamp the cell to the model bounds.
                let sr1 = Math.max(0, Math.min(s.r1, maxRow));
                let sc1 = Math.max(0, Math.min(s.c1, maxColumn));
                let sr2 = Math.max(0, Math.min(s.r2, maxRow));
                let sc2 = Math.max(0, Math.min(s.c2, maxColumn));
                for (let r = sr1; r <= sr2; ++r) {
                    for (let c = sc1; c <= sc2; ++c) {
                        dataModel.setData('body', r, c, null);
                    }
                }
            }
        }
    }
    /**
     * Handle the `'C'` key press for the data grid.
     *
     * @param grid - The data grid of interest.
     *
     * @param event - The keyboard event of interest.
     */
    onKeyC(grid, event) {
        // Bail early if the modifiers aren't correct for copy.
        if (event.shiftKey || !_lumino_domutils__WEBPACK_IMPORTED_MODULE_0__.Platform.accelKey(event)) {
            return;
        }
        // Stop the event propagation.
        event.preventDefault();
        event.stopPropagation();
        // Copy the current selection to the clipboard.
        grid.copyToClipboard();
    }
}

/**
 * An object which renders the cells of a data grid.
 *
 * #### Notes
 * If the predefined cell renderers are insufficient for a particular
```
