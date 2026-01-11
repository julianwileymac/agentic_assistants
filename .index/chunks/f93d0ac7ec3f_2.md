# Chunk: f93d0ac7ec3f_2

- source: `.venv-lab/Lib/site-packages/notebook/static/8929.22828925bc31ed18e912.js`
- lines: 74-162
- chunk: 3/154

```
CENSE, distributed with this software.
|----------------------------------------------------------------------------*/
/**
 * A basic implementation of a data grid key handler.
 *
 * #### Notes
 * This class may be subclassed and customized as needed.
 */
class BasicKeyHandler {
    constructor() {
        this._disposed = false;
    }
    /**
     * Whether the key handler is disposed.
     */
    get isDisposed() {
        return this._disposed;
    }
    /**
     * Dispose of the resources held by the key handler.
     */
    dispose() {
        this._disposed = true;
    }
    /**
     * Handle the key down event for the data grid.
     *
     * @param grid - The data grid of interest.
     *
     * @param event - The keydown event of interest.
     *
     * #### Notes
     * This will not be called if the mouse button is pressed.
     */
    onKeyDown(grid, event) {
        // if grid is editable and cell selection available, start cell editing
        // on key press (letters, numbers and space only)
        if (grid.editable &&
            grid.selectionModel.cursorRow !== -1 &&
            grid.selectionModel.cursorColumn !== -1) {
            const input = String.fromCharCode(event.keyCode);
            if (/[a-zA-Z0-9-_ ]/.test(input)) {
                const row = grid.selectionModel.cursorRow;
                const column = grid.selectionModel.cursorColumn;
                const cell = {
                    grid: grid,
                    row: row,
                    column: column
                };
                grid.editorController.edit(cell);
                if ((0,_lumino_keyboard__WEBPACK_IMPORTED_MODULE_1__.getKeyboardLayout)().keyForKeydownEvent(event) === 'Space') {
                    event.stopPropagation();
                    event.preventDefault();
                }
                return;
            }
        }
        switch ((0,_lumino_keyboard__WEBPACK_IMPORTED_MODULE_1__.getKeyboardLayout)().keyForKeydownEvent(event)) {
            case 'ArrowLeft':
                this.onArrowLeft(grid, event);
                break;
            case 'ArrowRight':
                this.onArrowRight(grid, event);
                break;
            case 'ArrowUp':
                this.onArrowUp(grid, event);
                break;
            case 'ArrowDown':
                this.onArrowDown(grid, event);
                break;
            case 'PageUp':
                this.onPageUp(grid, event);
                break;
            case 'PageDown':
                this.onPageDown(grid, event);
                break;
            case 'Escape':
                this.onEscape(grid, event);
                break;
            case 'Delete':
                this.onDelete(grid, event);
                break;
            case 'C':
                this.onKeyC(grid, event);
                break;
            case 'Enter':
                if (grid.selectionModel) {
                    grid.moveCursor(event.shiftKey ? 'up' : 'down');
```
